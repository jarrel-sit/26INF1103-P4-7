# --- Imports --- #
from dataclasses import dataclass
from .generated_recipe import GeneratedRecipe


# --- Classes --- #
@dataclass
class AIResult:
    success: bool
    recipe: GeneratedRecipe
    error_message: str
