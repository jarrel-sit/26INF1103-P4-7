from typing import Iterable, Optional
from models import GeneratedRecipe, RecipeRequest
from .ai_confidence_rule import AIConfidenceRule
from .allergy_rule import AllergyRule
from .cooking_time_rule import CookingTimeRule
from .dietary_rule import DietaryRule
from .evaluation import Evaluation
from .exceptions import InvalidRecordError
from .i_rule import IRule
from .i_scorer import IScorer
from .ingredient_availability_rule import IngredientAvailabilityRule
from .outcome import Outcome
from .outcome_router import OutcomeRouter
from .record_validator import RecordValidator
from .routing_decision import RoutingDecision
from .rule_evaluator import RuleEvaluator
from .weighted_scorer import WeightedScorer
from .logic_settings import LogicSettings


class LogicManager:
    """Domain brain: applies the business rules to an AI-enriched record.
    Public API mirrors Phase 1: evaluate(), score(), route(), route_batch(),
    plus process() which takes the team's RecipeRequest and GeneratedRecipe.

        - Composition: it creates and owns its RuleEvaluator and OutcomeRouter.
        - Aggregation: the scorer is injected (any IScorer) and the rules it
          runs are injected (any IRule) - both can exist without this manager.
        - Association: it uses a RecordValidator to check every incoming record.
    """

    def __init__(
        self,
        scorer: Optional[IScorer] = None,
        rules: Optional[Iterable[IRule]] = None,
        validator: Optional[RecordValidator] = None,
        settings: Optional[LogicSettings] = None,
    ):
        self.__validator = validator if validator is not None else RecordValidator()
        self.__evaluator = RuleEvaluator(
            rules if rules is not None else self.default_rules()
        )
        self.__settings = settings or LogicSettings()
        self.__scorer = scorer if scorer is not None else self.__settings.build_scorer()
        self.__router = OutcomeRouter()

    @staticmethod
    def default_rules() -> list:
        """The five business rules from Phase 1, in evaluation order."""
        return [
            IngredientAvailabilityRule(),
            AllergyRule(),
            DietaryRule(),
            CookingTimeRule(),
            AIConfidenceRule(),
        ]

    @property
    def settings(self) -> LogicSettings:
        """The LogicSettings instance that controls the business rules."""
        return self.__settings

    def apply_settings(self, settings: LogicSettings) -> None:
        """Applies new user settings and clears any fixed rule/scorer overrides."""
        self.__settings = settings
        self.__scorer = settings.build_scorer()

    def process(
        self, request: RecipeRequest, recipe: GeneratedRecipe
    ) -> RoutingDecision:
        """Same style as the AI manager's process(): takes the team models and
        returns the decision. Raises InvalidRecordError on a malformed record."""
        return self.route(self.__combine(request, recipe))

    def evaluate(self, record: dict) -> Evaluation:
        """Runs every business rule. Raises InvalidRecordError on a malformed record."""
        return self.__evaluator.evaluate(self.__validator.validate(record))

    def score(self, record: dict) -> float:
        """Numeric 0-100 score. Raises InvalidRecordError on a malformed record."""
        return self.__scorer.score(self.__validator.validate(record))

    def route(self, record: dict) -> RoutingDecision:
        """Evaluates + scores the record and assigns it accept / flag / reject.
        Raises InvalidRecordError on a malformed record so the caller can show
        an error instead of acting on bad AI output."""
        typed_record = self.__validator.validate(record)
        evaluation = self.__evaluator.evaluate(typed_record)
        numeric_score = self.__scorer.score(typed_record)

        return self.__router.decide(typed_record, evaluation, numeric_score)

    def route_batch(self, records: list) -> list:
        """Routes a list of candidate records, ranked accept -> flag -> reject,
        highest score first within each group. One malformed record does not
        stop the batch: it is ranked last as a reject explaining the problem."""
        decisions = []

        for record in records:
            try:
                decisions.append(self.route(record))
            except InvalidRecordError as error:
                decisions.append(self.__rejected_as_invalid(record, error))

        return sorted(decisions, key=self.__sort_key)

    # --- Private helpers ---
    @staticmethod
    def __combine(request: RecipeRequest, recipe: GeneratedRecipe) -> dict:
        """Phase 1 merge: the user's input first, then the AI's fields on top."""
        combined = {
            "ingredients": request.ingredients,
            "available_ingredients": request.available_ingredients,
            "allergies": request.allergies,
            "dietary_preferences": request.dietary_preferences,
        }
        combined.update(recipe.recipe_to_dict())

        return combined

    @staticmethod
    def __sort_key(decision: RoutingDecision) -> tuple:
        return (list(Outcome).index(decision.outcome), -decision.score)

    @staticmethod
    def __rejected_as_invalid(record, error: InvalidRecordError) -> RoutingDecision:
        name = record.get("recipe") if isinstance(record, dict) else None
        recipe = name if isinstance(name, str) else "Unknown Recipe"

        return RoutingDecision(
            recipe, Outcome.REJECT, f"invalid AI record: {error}", 0.0, {}, {}
        )
