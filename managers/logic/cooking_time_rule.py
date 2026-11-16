from .base_rule import BaseRule
from .recipe_record import RecipeRecord
from .severity import Severity


# CookingTimeRule ==== Recipe should match the user's max cooking-time preference where possible

class CookingTimeRule(BaseRule):
    """Recipe should match the user's max cooking-time preference where possible."""

    def __init__(self):
        super().__init__("cooking_time", Severity.ADVISORY)

    def _check(self, record: RecipeRecord) -> dict:
        max_time = record.cooking_time_limit
        estimated = record.estimated_cooking_time

        return {
            "passed": max_time is None or estimated <= max_time,
            "estimated_minutes": estimated,
            "max_minutes": max_time,
        }

    def failure_reason(self) -> str:
        return "exceeds max cooking time"