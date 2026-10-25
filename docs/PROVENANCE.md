# Provenance and release boundary

Lumen Recipe Engine was extracted from the public `maestrokaka/cyberboard-studio` snapshot at commit `7245b833217820b651e3f127632297b3799b1ec7` on 2026-10-25.

## Included

- `backend/lighting_recipe.py` became `src/lumen_recipe/compiler.py`.
- `backend/ai_quality.py` became `src/lumen_recipe/quality.py`.
- Public normalized CYBERBOARD geometry became `src/lumen_recipe/cyberboard.json`.
- The compiler was generalized with immutable `DeviceProfile` objects and a 16×16 example profile.
- The extracted offline tests remain under the MIT project license and add device, CLI, concurrency, deterministic output and legacy RGB-vector checks.
- `demo/photo-preview.js` is an isolated browser demonstration derived from the public `web/preview-engine.js` implementation. It is only used with a user-selected local image.

## Excluded

No API keys, user workspaces, device state, USB records, model responses, recordings, private history, desktop app, native integration, or original product release binaries are included. The reference photograph and branded artwork are not redistributed.

The vendored `cyberboard-cli` and its dependency notices were not copied into this repository; they remain third-party material in the source application. No claim is made that this project owns the original CLI or any device firmware.

## Attribution and permissions

The extracted source is released under MIT by the repository author. Before adding new photos, fonts, logos, or demos, confirm that each asset has a compatible license or an explicit redistribution grant. `demo/photo-calibration.json` contains only calibration coordinates and product labels; it does not contain pixels.
