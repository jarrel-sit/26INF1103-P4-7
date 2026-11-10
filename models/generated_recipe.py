# --- Imports --- #
from dataclasses import dataclass
from .instruction import Instruction


# --- Classes --- #
@dataclass
class GeneratedRecipe:
    recipe: str
    ingredients: dict[str, str]
    instructions: dict[str, Instruction]
    confidence: float
    dietary_preferences: list[str]
    equipment: list[str]
    hazardous_ingredients: dict[str, str]
    insufficient_ingredients: bool
