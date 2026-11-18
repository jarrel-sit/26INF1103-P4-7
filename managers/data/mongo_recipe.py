# --- Imports --- #
from .mongo_repository import MongoRepository
from .recipe_repo import RecipeRepository
from managers.logic import RoutingDecision, Outcome


# --- Classes --- #
class MongoRecipeRepository(MongoRepository, RecipeRepository):
    def __init__(self, uri, db_name, logger=None):
        super().__init__(uri, db_name, "recipes", logger=logger)

    def save(self, recipe: RoutingDecision | dict) -> bool:
        """Inserts one evaluated recipe. Returns True if the save succeeded."""
        if not recipe or not isinstance(recipe, (RoutingDecision, dict)):
            return False

        if isinstance(recipe, RoutingDecision):
            recipe = recipe.to_dict()

        outcome = recipe.get("outcome", "unknown")
        if isinstance(outcome, Outcome):
            outcome = outcome.value          # store the plain string

        document = {
            "recipe": recipe.get("recipe", "Unknown Recipe"),
            "outcome": outcome,
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
        return RoutingDecision(
            recipe=document.get("recipe", "Unknown Recipe"),
            outcome=Outcome(document.get("outcome", "unknown")),
            reason=document.get("reason", ""),
            score=float(document.get("score", 0.0)),
            ingredients=document.get("ingredients", "[]"),
            instructions=document.get("instructions", "[]"),
        )
