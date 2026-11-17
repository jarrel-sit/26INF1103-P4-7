# --- Imports --- #
from .mongo_repository import MongoRepository
from .recipe_repo import RecipeRepository


# --- Classes --- #
class MongoRecipeRepository(MongoRepository, RecipeRepository):
    def __init__(self, uri, db_name, logger=None):
        super().__init__(uri, db_name, "recipes", logger=logger)

    def save(self, recipe):
        """Inserts one evaluated recipe. Returns True if the save succeeded."""
        if not recipe or not isinstance(recipe, dict):
            return False

        document = {
            "recipe": recipe.get("recipe", "Unknown Recipe"),
            "outcome": recipe.get("outcome", "unknown"),
            "score": recipe.get("score", 0.0),
            "reason": recipe.get("reason", ""),
            "ingredients": recipe.get("ingredients", {}),
            "instructions": recipe.get("instructions", {}),
        }

        return super().save(document)

    def find_all(self):
        return self.load()

    def find_successful(self):
        return self.query(lambda r: r.get("outcome") == "accept")

    def find_by_ingredient(self, name):
        name = name.strip().lower()
        return self.query(
            lambda r: any(
                name in str(i).strip().lower() for i in r.get("ingredients", {})
            )
        )

    def _process_document(self, document):
        """Turns a stored document into a recipe record."""
        return {
            "recipe": document["recipe"],
            "outcome": document["outcome"],
            "score": float(document.get("score", 0.0)),
            "reason": document.get("reason", ""),
            "ingredients": document.get("ingredients", {}),
            "instructions": document.get("instructions", {}),
        }