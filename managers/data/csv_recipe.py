import json
from .recipe_repo import RecipeRepository

from data_manager import (
    RecipeRepository,
    DEFAULT_RECIPES_FILEPATH,
    RECIPE_FIELDNAMES,
    load_recipes,
    save,
    query,
)

class CsvRecipeRepository(RecipeRepository):
    def __init__(self, filepath=DEFAULT_RECIPES_FILEPATH, logger=None):
        self.__filepath = filepath
        self.__logger = logger

    def save(self, recipe):
        """Appends one evaluated recipe. Returns True if the save succeeded."""
        if not recipe or not isinstance(recipe, dict):
            return False

        row = {
            "recipe": recipe.get("recipe", "Unknown Recipe"),
            "outcome": recipe.get("outcome", "unknown"),
            "score": recipe.get("score", 0.0),
            "reason": recipe.get("reason", ""),
            "ingredients": json.dumps(recipe.get("ingredients", [])),
            "instructions": json.dumps(recipe.get("instructions", [])),
        }
        return save(self.__filepath, RECIPE_FIELDNAMES, row,
                    mode="a", logger=self.__logger)

    def find_all(self):
        return load_recipes(self.__filepath, logger=self.__logger)

    def find_successful(self):
        return query(lambda r: r.get("outcome") == "accept", self.find_all())

    def find_by_ingredient(self, name):
        name = name.strip().lower()
        return query(
            lambda r: any(name in str(i).strip().lower()
                          for i in r.get("ingredients", [])),
            self.find_all(),
        )