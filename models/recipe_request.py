# --- Imports --- #
from dataclasses import dataclass


# --- Classes --- #
@dataclass
class RecipeRequest:
    ingredients: dict[str, str]
    available_ingredients: dict[str, str]
    allergies: list[str]
    dietary_preferences: list[str]
    pax: int
