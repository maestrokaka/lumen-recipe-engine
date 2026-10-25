# Release checklist

- [ ] Run `python -m unittest discover -s tests -v` with the optional `jsonschema` extra.
- [ ] Run `python scripts/build_demo.py --check` and `node --check demo/app.js`.
- [ ] Build a wheel and source distribution in an environment with build dependencies available.
- [ ] Review `git diff --check` and scan tracked files for credentials, recordings, private paths and binaries.
- [ ] Verify the repository is public, has a top-level MIT license, and the README has an installable example.
- [ ] Create a tag only after the final commit is selected; keep the first release source-only.
