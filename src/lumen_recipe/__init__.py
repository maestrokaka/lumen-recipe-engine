"""Offline, declarative RGB animation compilation and quality inspection."""
from .devices import DeviceProfile, CYBERBOARD, MATRIX16
from .compiler import RecipeError, compile_recipe, validate_recipe, recipe_schema, model_recipe_schema
from .quality import inspect_design_quality

__version__ = "0.1.0"
__all__ = ["DeviceProfile", "CYBERBOARD", "MATRIX16", "RecipeError", "compile_recipe",
           "validate_recipe", "recipe_schema", "model_recipe_schema", "inspect_design_quality"]
