from .base_rule import BaseRule
from .recipe_record import RecipeRecord
from .severity import Severity


# AIConfidenceRule ==== Guards the logic layer against acting on a low-confidence AI response

class AIConfidenceRule(BaseRule):
    """Guards the logic layer against acting on a low-confidence AI response."""

    def __init__(self, min_confidence: float = 0.6):
        super().__init__("ai_confidence", Severity.BLOCKING, "ai_confidence_threshold")
        self.__min_confidence = min_confidence

    def _check(self, record: RecipeRecord) -> dict:
        return {
            "passed": record.confidence >= self.__min_confidence,
            "confidence": record.confidence,
            "threshold": self.__min_confidence,
        }

    def failure_reason(self) -> str:
        return "AI confidence too low"