import json
from .recipe_repo import RecipeRepository
from .csv_repository import CsvRepository


class CsvRecipeRepository(CsvRepository, RecipeRepository):
    def __init__(self, filepath, fieldnames, logger=None):
        super().__init__(filepath, fieldnames, mode="a", logger=logger)

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

        return super().save(row)

    def find_all(self):
        return self.load()

    def find_successful(self):
        return self.query(lambda r: r.get("outcome") == "accept")

    def find_by_ingredient(self, name):
        name = name.strip().lower()
        return self.query(
            lambda r: any(
                name in str(i).strip().lower() for i in r.get("ingredients", [])
            )
        )

    def _process_data_row(self, row):
        """Processes a single row of data loaded from the CSV file."""
        # Convert JSON strings back to lists
        row["score"] = float(row.get("score", 0.0))
        row["ingredients"] = json.loads(row.get("ingredients", "[]"))
        row["instructions"] = json.loads(row.get("instructions", "[]"))

        return row
