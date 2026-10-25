"""File-only CLI. Exit 0=success, 1=quality failure, 2=input/usage error."""
import argparse
import json
import os
from pathlib import Path
import sys
import tempfile
from . import compile_recipe, validate_recipe, inspect_design_quality, recipe_schema, model_recipe_schema
from .devices import DeviceProfile

MAX_INPUT_BYTES = 32 * 1024 * 1024

def read_json(path):
    with Path(path).open("rb") as handle:
        raw = handle.read(MAX_INPUT_BYTES + 1)
    if len(raw) > MAX_INPUT_BYTES:
        raise ValueError("JSON input exceeds 32 MiB")
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("Duplicate JSON field: " + key)
            result[key] = value
        return result
    def constant(value):
        raise ValueError("Non-finite JSON number: " + value)
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=constant)

def write_json(value, path=None):
    text = json.dumps(value, ensure_ascii=False, allow_nan=False, indent=2) + "\n"
    if path is None:
        sys.stdout.write(text)
        return
    destination = Path(path)
    fd, temporary = tempfile.mkstemp(prefix=".lumen-", dir=destination.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
        os.replace(temporary, destination)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)

def main(argv=None):
    parser = argparse.ArgumentParser(prog="lumen-recipe")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("compile", "validate", "inspect"):
        command = sub.add_parser(name)
        command.add_argument("input")
        command.add_argument("--device", help="cyberboard, matrix16, or a profile JSON path")
        command.add_argument("-o", "--output")
        if name == "inspect":
            command.add_argument("--brief", default="")
            command.add_argument("--has-images", action="store_true")
    schema = sub.add_parser("schema")
    schema.add_argument("--compact", action="store_true")
    schema.add_argument("-o", "--output")
    args = parser.parse_args(argv)
    try:
        if args.command == "schema":
            write_json(model_recipe_schema() if args.compact else recipe_schema(), args.output)
            return 0
        value = read_json(args.input)
        device = args.device
        if device and device not in ("cyberboard", "matrix16"):
            device = DeviceProfile.resolve(read_json(device))
        if args.command == "compile":
            result = compile_recipe(value, device=device or "cyberboard")
        elif args.command == "validate":
            validate_recipe(value, device=device or "cyberboard")
            result = {"valid": True}
        else:
            result = inspect_design_quality(value, device=device, brief=args.brief, has_images=args.has_images)
        write_json(result, args.output)
        return 1 if args.command == "inspect" and not result["passed"] else 0
    except (ValueError, TypeError, OSError, RecursionError) as error:
        print("lumen-recipe: " + str(error), file=sys.stderr)
        return 2
