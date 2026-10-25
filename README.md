# Lumen Recipe Engine

Lumen Recipe Engine compiles a small, declarative JSON recipe into bounded RGB animation frames and reports obvious pixel-level quality problems before an animation is saved or sent to hardware. It was extracted from the public lighting workflow in [Cyberboard Studio](https://github.com/maestrokaka/cyberboard-studio); the original application remains independent.

The engine is offline by design. It does not call a model, read credentials, discover devices, access USB, or load image files. A model may produce a recipe, but local validation is the authority: unknown fields, unsafe numbers, unsupported layers, incomplete timelines and excessive work are rejected before rendering.

## Quick start

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e ".[test]"
python -m lumen_recipe compile examples/orbit.recipe.json -o /tmp/orbit.design.json
python -m lumen_recipe inspect /tmp/orbit.design.json
python -m unittest discover -s tests -v
```

The package exposes `compile_recipe`, `inspect_design_quality`, `DeviceProfile`, and `recipe_schema`. `cyberboard` is the default profile: a 40×5 top matrix and a 90-position key layout with seven reserved positions. `matrix16` demonstrates that the compiler is not limited to the original keyboard geometry.

```python
from lumen_recipe import compile_recipe, inspect_design_quality

design = compile_recipe(recipe, device="matrix16")
report = inspect_design_quality(design, brief="cyan scan with violet keys")
assert report["passed"]
```

`lumen-recipe schema --compact` prints the model-facing JSON Schema. The compact schema reduces repeated motion definitions; semantic timeline and work-budget checks remain local Python checks.

## Photo preview demonstration

`demo/` is a browser-only playback demonstration. `scripts/build_demo.py` generates fixtures from the Python compiler and quality checker. Open `demo/index.html` in a local web server after running:

```bash
python scripts/build_demo.py
python -m http.server 8000 --directory demo
```

The optional photo overlay asks you to select the matching CYBERBOARD R6 Vision front photograph from your own machine. The calibration is intentionally kept separate from the compiler, and the repository does not redistribute a photograph or claim physical color accuracy. The preview uses the same Canvas renderer extracted from the public Cyberboard Studio snapshot.

## Contract and limits

- Recipe v1 uses normalized coordinates, bounded layers, contiguous scenes and 10–100 ms frame intervals.
- The compiler emits RGB hex frames; it does not write a device configuration.
- Quality metrics are digital RGB proxies, not photometric measurements. A warning or pass is not a guarantee of physical appearance.
- The engine does not infer reference-image fidelity from a prompt or image flag.
- Device profiles are data. Hardware transport, firmware semantics and USB permissions belong to an integration layer.

## Provenance and licensing

The core compiler and quality checker are derived from the public `cyberboard-studio` snapshot at commit `7245b833217820b651e3f127632297b3799b1ec7`. The public snapshot's tests were adapted as offline regression vectors; the resulting RGB hashes are checked in `tests/legacy-vectors.json`. The photo preview code is an isolated demonstration and retains its source attribution in `docs/PROVENANCE.md`.

This repository's original code is MIT licensed. Third-party notices and image/font licenses are listed separately in `docs/PROVENANCE.md`. The reference photo is not included. See `LICENSE`.
