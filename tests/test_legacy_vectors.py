import hashlib,json,unittest
from pathlib import Path
from lumen_recipe import compile_recipe
class LegacyPixels(unittest.TestCase):
    def test_original_public_snapshot_rgb_is_preserved(self):
        vectors=json.loads(Path(__file__).with_name("legacy-vectors.json").read_text(encoding="utf-8"))
        for v in vectors:
            d=compile_recipe(v["recipe"])
            actual=hashlib.sha256(json.dumps([d["frames"],d["keyframes"]],separators=(",",":")).encode()).hexdigest()
            self.assertEqual(actual,v["rgb_sha256"])
