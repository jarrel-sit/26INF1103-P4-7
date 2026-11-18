from .base_rule import BaseRule
from .recipe_record import RecipeRecord
from .severity import Severity

# DietaryRule ==== Recipe must follow the user's selected dietary requirements

class DietaryRule(BaseRule):
    """Recipe must follow the user's selected dietary requirements."""

    def __init__(self):
        super().__init__("dietary_restrictions", Severity.ADVISORY)

    def _check(self, record: RecipeRecord) -> dict:
        diets = {d.strip().lower() for d in record.dietary_preferences}
        ingredients = record.ingredients
        unmet = {diet for diet in diets if diet in ingredients}

        return {"passed": len(unmet) == 0, "unmet_preferences": sorted(unmet)}

    def failure_reason(self) -> str:
        return "dietary preference not met"