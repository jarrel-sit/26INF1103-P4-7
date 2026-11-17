from typing import Optional
from models import EvaluationResult
from .evaluation import Evaluation
from .outcome import Outcome

# RoutingDecision ==== holds the final decision

class RoutingDecision:
    """The final decision for one record: where it goes, why, and its score."""

    def __init__(
        self,
        recipe: str,
        outcome: Outcome,
        reason: str,
        score: float,
        ingredients: dict,
        instructions: dict,
        evaluation: Optional[Evaluation] = None,
    ):
        self.__recipe = recipe
        self.__outcome = outcome
        self.__reason = reason
        self.__score = score
        self.__ingredients = dict(ingredients)
        self.__instructions = dict(instructions)
        self.__evaluation = evaluation

    @property
    def recipe(self) -> str:
        return self.__recipe

    @property
    def outcome(self) -> Outcome:
        return self.__outcome

    @property
    def reason(self) -> str:
        return self.__reason

    @property
    def score(self) -> float:
        return self.__score

    @property
    def ingredients(self) -> dict:
        return dict(self.__ingredients)

    @property
    def evaluation(self) -> Optional[Evaluation]:
        return self.__evaluation

    def to_evaluation_result(self) -> EvaluationResult:
        """Convert to the team's models.EvaluationResult."""
        findings = self.__evaluation.results if self.__evaluation else ()

        return EvaluationResult(
            outcome=self.__outcome.value,
            score=self.__score,
            reason=self.__reason,
            rule_results=[finding.to_rule_result() for finding in findings],
        )

    def to_dict(self) -> dict:
        """Same dict shape the Phase 1 route() returned, so data_manager and
        io_manager can keep reading it with .get()."""
        rule_results = self.__evaluation.to_dict()["rule_results"] if self.__evaluation else {}

        return {
            "recipe": self.__recipe,
            "outcome": self.__outcome.value,
            "reason": self.__reason,
            "score": self.__score,
            "rule_results": rule_results,
            "ingredients": dict(self.__ingredients),
            "instructions": dict(self.__instructions),
        }