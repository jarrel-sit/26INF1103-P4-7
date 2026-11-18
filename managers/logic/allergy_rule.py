from .base_rule import BaseRule
from .recipe_record import RecipeRecord
from .severity import Severity


# AllergyRule ==== Rejects any recipe that conflicts with a stated allergy

class AllergyRule(BaseRule):
    """Rejects any recipe that conflicts with a stated allergy."""

    def __init__(self):
        super().__init__("allergy_restrictions", Severity.BLOCKING)

    def _check(self, record: RecipeRecord) -> dict:
        allergies = {a.strip().lower() for a in record.allergies}
        ingredients = {i.strip().lower() for i in record.ingredients}
        conflicts = allergies & ingredients

        return {"passed": len(conflicts) == 0, "conflicting_allergens": sorted(conflicts)}

    def failure_reason(self) -> str:
        return "allergy conflict"