# --- Imports --- #
from dataclasses import dataclass
from .generated_recipe import GeneratedRecipe


# --- Classes --- #
@dataclass
class AIResult:
    success: bool
    recipe: GeneratedRecipe | None = None
    error_message: str | None = None
