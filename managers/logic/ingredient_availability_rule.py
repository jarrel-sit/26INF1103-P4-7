from .base_rule import BaseRule
from .recipe_record import RecipeRecord
from .severity import Severity

# IngredientAvailabilityRule ==== Only recommend recipes using ingredients the user has, or flag what needs to be bought.

class IngredientAvailabilityRule(BaseRule):
    """Only recommend recipes using ingredients the user has, or flag what
    needs to be bought."""

    def __init__(self):
        super().__init__("ingredient_availability", Severity.ADVISORY)

    def _check(self, record: RecipeRecord) -> dict:
        have = record.available_quantities
        missing = []

        for item, needed in record.required_quantities.items():
            if item not in have:
                missing.append(item)
                continue

            available = have[item]

            # Only compare real amounts, and only when the units line up
            if needed.amount > 0 and available.amount > 0:
                if available.is_comparable_to(needed) and not available.covers(needed):
                    missing.append(item)

        return {"passed": len(missing) == 0, "missing_ingredients": sorted(missing)}

    def failure_reason(self) -> str:
        return "missing or insufficient ingredients"