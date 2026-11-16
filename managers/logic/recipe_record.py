from typing import Optional
from .quantity import Quantity

# RecipeRecord ====

class RecipeRecord:
    """A validated, read-only view of one AI-enriched recipe record.
    Owns the Quantity objects parsed from its ingredient amounts."""

    def __init__(
        self,
        recipe: str,
        ingredients: dict,
        confidence: float,
        available_ingredients: Optional[dict] = None,
        ingredients_used: Optional[list] = None,
        allergies: Optional[list] = None,
        dietary_preferences: Optional[list] = None,
        max_cooking_time: Optional[float] = None,
        estimated_cooking_time: float = 0,
        instructions: Optional[dict] = None,
    ):
        self.__recipe = recipe
        self.__ingredients = dict(ingredients)
        self.__available_ingredients = dict(available_ingredients or {})
        self.__ingredients_used = list(ingredients_used or [])
        self.__allergies = list(allergies or [])
        self.__dietary_preferences = list(dietary_preferences or [])
        self.__max_cooking_time = max_cooking_time
        self.__estimated_cooking_time = estimated_cooking_time
        self.__confidence = confidence
        self.__instructions = dict(instructions or {})

        # Composition: the record creates (and owns) its Quantity objects
        self.__required_quantities = {
            name: Quantity.parse(raw) for name, raw in self.__ingredients.items()
        }
        self.__available_quantities = {
            name: Quantity.parse(raw)
            for name, raw in self.__available_ingredients.items()
        }

    # Read-only access: callers get copies, so nobody can mutate the record
    @property
    def recipe(self) -> str:
        return self.__recipe

    @property
    def ingredients(self) -> dict:
        return dict(self.__ingredients)

    @property
    def available_ingredients(self) -> dict:
        return dict(self.__available_ingredients)

    @property
    def ingredients_used(self) -> list:
        return list(self.__ingredients_used)

    @property
    def allergies(self) -> list:
        return list(self.__allergies)

    @property
    def dietary_preferences(self) -> list:
        return list(self.__dietary_preferences)

    @property
    def confidence(self) -> float:
        return self.__confidence

    @property
    def cooking_time_limit(self) -> Optional[float]:
        """The user's max cooking time in minutes, or None if there isn't one."""
        return self.__max_cooking_time

    @property
    def estimated_cooking_time(self) -> float:
        return self.__estimated_cooking_time

    @property
    def instructions(self) -> dict:
        return dict(self.__instructions)

    @property
    def required_quantities(self) -> dict:
        """Ingredient name -> Quantity the recipe calls for."""
        return dict(self.__required_quantities)

    @property
    def available_quantities(self) -> dict:
        """Ingredient name -> Quantity the user has."""
        return dict(self.__available_quantities)