# --- Imports --- #
from dataclasses import dataclass
from instruction import Instruction

# --- Classes --- #
@dataclass
class GeneratedRecipe:
    name: str
    ingredients: dict[str, str]
    instructions: dict[str, Instruction]
    confidence: float
    equipment: list[str]
    hazardous_ingredients: dict[str, str]
    insufficient_ingredients: bool