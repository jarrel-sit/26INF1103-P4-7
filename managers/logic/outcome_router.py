from .evaluation import Evaluation
from .outcome import Outcome
from .recipe_record import RecipeRecord
from .routing_decision import RoutingDecision
from .severity import Severity

# OutcomeRouter ==== makes the decision from the rule results

class OutcomeRouter:
    """Single job: turn an Evaluation into an outcome.
        - REJECT if any BLOCKING rule failed (allergy conflict OR low AI
          confidence). Safety/trust issues get no partial credit, whatever the score.
        - FLAG if any ADVISORY rule failed (missing ingredients, dietary
          preference not met, over time) - one or a combination.
        - ACCEPT only if every rule passed.
    It reads each rule's Severity, so adding a rule never means editing this class."""

    def decide(
        self, record: RecipeRecord, evaluation: Evaluation, score: float
    ) -> RoutingDecision:
        blocking = evaluation.failed(Severity.BLOCKING)
        advisory = evaluation.failed(Severity.ADVISORY)

        if blocking:
            outcome = Outcome.REJECT
            reason = blocking[0].failure_reason  # first blocking rule wins
        elif advisory:
            outcome = Outcome.FLAG
            reason = self.__build_reason(advisory)
        else:
            outcome = Outcome.ACCEPT
            reason = "all business rules passed"

        return RoutingDecision(
            record.recipe,
            outcome,
            reason,
            score,
            record.ingredients,
            record.instructions,
            evaluation,
        )

    def __build_reason(self, failed: list) -> str:
        return ", ".join(result.failure_reason for result in failed)