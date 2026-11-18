import json
from .recipe_repo import RecipeRepository
from .csv_repository import CsvRepository
from managers.logic import RoutingDecision, Outcome


class CsvRecipeRepository(CsvRepository, RecipeRepository):
    """A CSV-based implementation of the RecipeRepository interface."""
    def __init__(self, filepath, fieldnames, logger=None):
        super().__init__(filepath, fieldnames, mode="a", logger=logger)

    def save(self, recipe: RoutingDecision | dict) -> bool:
        """Appends one evaluated recipe. Returns True if the save succeeded."""

        if not recipe or not isinstance(recipe, (RoutingDecision, dict)):
            return False

        if isinstance(recipe, RoutingDecision):
            recipe = recipe.to_dict()

        row = {
            "recipe": recipe.get("recipe", "Unknown Recipe"),
            "outcome": recipe.get("outcome", "unknown"),
            "score": recipe.get("score", 0.0),
            "reason": recipe.get("reason", ""),
            "ingredients": json.dumps(recipe.get("ingredients", [])),
            "instructions": json.dumps(recipe.get("instructions", [])),
        }

        return super().save(row)

    def find_all(self) -> list[RoutingDecision]:
        """Returns all recipes as a list of RoutingDecision objects."""
        return self.load()

    def find_successful(self) -> list[RoutingDecision]:
        """Returns all recipes with outcome 'accept' as a list of RoutingDecision objects."""
        return self.query(lambda r: r.outcome == Outcome.ACCEPT)

    def find_by_ingredient(self, name) -> list[RoutingDecision]:
        """Returns all recipes that include the given ingredient (case-insensitive)."""
        name = name.strip().lower()
        return self.query(
            lambda r: any(name in str(i).strip().lower() for i in r.ingredients)
        )

    def _process_data_row(self, row) -> RoutingDecision:
        """Processes a single row of data loaded from the CSV file."""
        # Convert JSON strings back to lists
        row["score"] = float(row.get("score", 0.0))
        row["ingredients"] = json.loads(row.get("ingredients", "[]"))
        row["instructions"] = json.loads(row.get("instructions", "[]"))

        return self._row_to_routing_decision(row)

    def _row_to_routing_decision(self, row) -> RoutingDecision:
        """Converts a CSV row to a RoutingDecision object."""
        return RoutingDecision(
            recipe=row.get("recipe", "Unknown Recipe"),
            outcome=Outcome(row.get("outcome", "unknown")),
            reason=row.get("reason", ""),
            score=float(row.get("score", 0.0)),
            ingredients=row.get("ingredients", "[]"),
            instructions=row.get("instructions", "[]"),
        )
