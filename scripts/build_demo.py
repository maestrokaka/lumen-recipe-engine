"""Generate deterministic browser fixtures using the actual Python compiler."""
import argparse
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from lumen_recipe import compile_recipe, inspect_design_quality

def build():
    recipe=json.loads((ROOT/"examples/orbit.recipe.json").read_text(encoding="utf-8"))
    result={}
    for name in ("cyberboard","matrix16"):
        design=compile_recipe(recipe,device=name)
        report=inspect_design_quality(design,brief="Animated cyan scan and violet keys, seamless loop")
        if not report["passed"]:raise ValueError(report)
        result[name]={"design":design,"report":report}
    result["photoCalibration"]=json.loads((ROOT/"demo/photo-calibration.json").read_text(encoding="utf-8"))
    return "window.LUMEN_EXAMPLES = " + json.dumps(result,ensure_ascii=False,separators=(",",":")) + ";\n"
if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("--check",action="store_true");args=parser.parse_args()
    path=ROOT/"demo/fixtures.js";text=build()
    if args.check:
        if not path.exists() or path.read_text(encoding="utf-8")!=text:raise SystemExit("Demo fixtures are stale: run python scripts/build_demo.py")
        print("PASS: demo fixtures match compiler and quality reports")
    else:path.write_text(text,encoding="utf-8");print("Built demo/fixtures.js")
