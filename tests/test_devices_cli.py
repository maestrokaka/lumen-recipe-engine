import copy
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from lumen_recipe import DeviceProfile, CYBERBOARD, MATRIX16, compile_recipe, inspect_design_quality, RecipeError
from lumen_recipe import compiler
from lumen_recipe.cli import read_json

ROOT = Path(__file__).resolve().parents[1]
def recipe():
    return {"version":1,"name":"Wave","description":"","frame_count":16,"speed_ms":40,"palette":["#00FFFF"],
            "scenes":[{"name":"Loop","start":0,"end":16,"top":[{"kind":"wave","color":"#00FFFF","phase":{"from":0,"to":2}}],
                       "keys":[{"kind":"wave","color":"#00FFFF","phase":{"from":0,"to":2}}]}]}

class DevicesAndCli(unittest.TestCase):
    def test_two_profiles_independent_shapes_and_quality(self):
        for device in (CYBERBOARD, MATRIX16):
            design=compile_recipe(recipe(),device=device)
            self.assertEqual(len(design["frames"][0]),device.top_width*device.top_height)
            self.assertEqual(len(design["keyframes"][0]),len(device.key_coordinates))
            report=inspect_design_quality(design)
            self.assertTrue(report["passed"],report)
            self.assertEqual(report["metrics"]["regions"]["keys"]["active_led_positions"],len(device.active_keys))
        self.assertNotEqual(compile_recipe(recipe())["id"],compile_recipe(recipe(),device=MATRIX16)["id"])

    def test_one_pixel_matrix_and_reserved_keys(self):
        device=DeviceProfile("single",1,1,[(.5,.5),None])
        r=recipe();r["scenes"][0]["top"]=[{"kind":"bitmap","rows":["1"]}]
        d=compile_recipe(r,device=device)
        self.assertEqual(d["frames"][0],["#00FFFF"])
        self.assertTrue(all(f[1]=="#000000" for f in d["keyframes"]))
        self.assertEqual(DeviceProfile.resolve(json.loads(json.dumps(device.to_dict()))),device)

    def test_devices_reject_invalid_dimensions_and_coordinates(self):
        cases=[("x",True,5,[(0,0)]),("x",65,1,[(0,0)]),("x",64,64,[(0,0)]),
               ("x",0,1,[(0,0)]),("x",1,1,[]),("x",1,1,[None]),("x",1,1,[(float("nan"),0)]),
               ("x",1,1,[(float("inf"),0)]),("x",1,1,[(True,0)]),("x",1,1,[(2,0)]),("../x",1,1,[(0,0)]),
               ("x",1,1,[(0,0)]*1025)]
        for args in cases:
            with self.subTest(args=str(args)[:60]),self.assertRaises(ValueError):DeviceProfile(*args)
        with self.assertRaises(ValueError):DeviceProfile.resolve({**CYBERBOARD.to_dict(),"code":"bad"})

    def test_profile_is_immutable_and_copies_callers_coordinates(self):
        coords=[[0,0],[1,1]];device=DeviceProfile("immutable",2,2,coords);coords[0][0]=1
        self.assertEqual(device.key_coordinates[0],(0,0))
        with self.assertRaises(AttributeError):device.name="changed"

    def test_work_budget_accounts_for_actual_geometry(self):
        r=recipe();r["frame_count"]=1;r["scenes"][0]["end"]=1
        r["scenes"][0]["top"]=[{"kind":"solid","color":"#FFFFFF"}];r["scenes"][0]["keys"]=[]
        with patch.object(compiler,"MAX_WORK",200):
            compile_recipe(r,device=CYBERBOARD)
            with self.assertRaises(RecipeError):compile_recipe(r,device=MATRIX16)

    def test_parallel_compilation_does_not_leak_device_geometry(self):
        devices=[CYBERBOARD,MATRIX16]*8
        with ThreadPoolExecutor(max_workers=4) as pool:
            outputs=list(pool.map(lambda d:compile_recipe(recipe(),device=d),devices))
        for d,result in zip(devices,outputs):self.assertEqual(result,compile_recipe(recipe(),device=d))

    def test_matrix_bitmap_uses_target_pixels_not_cyberboard_width(self):
        r=recipe();r["scenes"][0]["top"]=[{"kind":"bitmap","rows":["1"],"x":8/15,"y":8/15}]
        frame=compile_recipe(r,device=MATRIX16)["frames"][0]
        self.assertEqual(sum(c!="#000000" for c in frame),1)
        self.assertEqual(frame[8*16+8],"#00FFFF")

    def test_quality_rejects_bad_metadata_reserved_and_mismatched_tracks(self):
        d=compile_recipe(recipe());d["device"]["top_width"]=True
        self.assertEqual(inspect_design_quality(d)["issues"][0]["code"],"invalid_device")
        d=compile_recipe(recipe());d["keyframes"][0][57]="#FFFFFF"
        self.assertIn("reserved_key_lit",{x["code"] for x in inspect_design_quality(d)["issues"]})
        d=compile_recipe(recipe());d["keyframes"].pop()
        self.assertIn("mismatched_tracks",{x["code"] for x in inspect_design_quality(d)["issues"]})

    def test_cli_roundtrip_and_exit_codes(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);source=root/"recipe.json";output=root/"design.json";source.write_text(json.dumps(recipe()))
            def run(*args):return subprocess.run([sys.executable,"-m","lumen_recipe",*map(str,args)],capture_output=True,text=True)
            result=run("compile",source,"--device","matrix16","-o",output);self.assertEqual(result.returncode,0,result.stderr)
            result=run("inspect",output);self.assertEqual(result.returncode,0,result.stderr);self.assertTrue(json.loads(result.stdout)["passed"])
            before=output.read_bytes();source.write_text('{"code":"bad"}')
            result=run("compile",source,"-o",output);self.assertEqual(result.returncode,2);self.assertEqual(output.read_bytes(),before)
            r=recipe();r["scenes"][0]["top"]=[];r["scenes"][0]["keys"]=[];source.write_text(json.dumps(r))
            self.assertEqual(run("compile",source,"-o",output).returncode,0)
            self.assertEqual(run("inspect",output).returncode,1)
            self.assertEqual(run("inspect",output,"--brief","all lights off").returncode,0)
            self.assertEqual(json.loads(run("schema").stdout)["properties"]["version"]["const"],1)

    def test_cli_rejects_duplicate_nonfinite_and_oversized_json(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/"input.json"
            for raw in ('{"x":1,"x":2}','{"x":NaN}','{"x":Infinity}'):
                path.write_text(raw)
                with self.assertRaises(ValueError):read_json(path)
            path.write_text('"123456789"')
            with patch("lumen_recipe.cli.MAX_INPUT_BYTES",4),self.assertRaises(ValueError):read_json(path)

if __name__=="__main__":unittest.main()
