# === Imports ===
import math
import re
from abc import ABC, abstractmethod
from enum import Enum
from typing import Iterable


# ===========================================================================
# === Exceptions ============================================================
# ===========================================================================
class LogicManagerError(Exception):
    """Base class for every error the Logic Manager raises on purpose."""


class InvalidRecordError(LogicManagerError):
    """Raised when an AI-enriched record is missing a field, or a field has
    the wrong type or an out-of-range value."""

    def __init__(self, field: str, message: str):
        super().__init__(f"'{field}' {message}")
        self.__field = field

    @property
    def field(self) -> str:
        """Name of the offending field."""
        return self.__field


# ===========================================================================
# === Enumerations ==========================================================
# ===========================================================================
class Severity(Enum):
    """What a failed rule means for the final outcome."""

    BLOCKING = "blocking"  # a failure here REJECTS the recipe (safety / trust)
    ADVISORY = "advisory"  # a failure here FLAGS the recipe (user should check)


class Outcome(Enum):
    """The three outcome paths. Values match the Phase 1 strings, so saved
    CSV rows and io_manager comparisons such as `== "accept"` keep working."""

    ACCEPT = "accept"
    FLAG = "flag"
    REJECT = "reject"


# ===========================================================================
# === Value object: Quantity ================================================
# ===========================================================================
class Quantity:
    """An amount plus a unit, e.g. 200 g. Replaces Phase 1 parse_quantity()."""

    _PATTERN = re.compile(r"^([\d.]+)\s*([a-zA-Z]*)$")

    def __init__(self, amount: float = 0.0, unit: str = ""):
        self.__amount = float(amount)
        self.__unit = unit

    @staticmethod
    def parse(raw) -> "Quantity":
        """Builds a Quantity from raw AI/user text such as '200g' or '2'.
        Anything unreadable becomes 0 with no unit - never raises."""

        # In case in the future quantity is returned as a numerical value
        if not isinstance(raw, str):
            try:
                return Quantity(float(raw))
            except (ValueError, TypeError, OverflowError):
                return Quantity()

        match = Quantity._PATTERN.match(raw.strip())
        if match:
            try:
                return Quantity(float(match.group(1)), match.group(2).lower())
            except ValueError:
                return Quantity()

        return Quantity()

    @property
    def amount(self) -> float:
        return self.__amount

    @property
    def unit(self) -> str:
        return self.__unit

    def is_comparable_to(self, other: "Quantity") -> bool:
        """Same unit, or at least one side has no unit stated."""
        return self.__unit == other.unit or not self.__unit or not other.unit

    def covers(self, needed: "Quantity") -> bool:
        """True if this amount is enough to supply `needed`."""
        return self.__amount >= needed.amount

    def __eq__(self, other):
        if not isinstance(other, Quantity):
            return NotImplemented
        return (self.__amount, self.__unit) == (other.amount, other.unit)

    def __hash__(self):
        return hash((self.__amount, self.__unit))

    def __repr__(self):
        return f"Quantity({self.__amount}, {self.__unit!r})"


# ===========================================================================
# === Typed record ==========================================================
# ===========================================================================
class RecipeRecord:
    """A validated, read-only view of one AI-enriched recipe record.
    Owns the Quantity objects parsed from its ingredient amounts."""

    def __init__(
        self,
        recipe: str,
        ingredients: dict,
        confidence: float,
        available_ingredients: dict = None,
        ingredients_used: list = None,
        allergies: list = None,
        dietary_preferences: list = None,
        max_cooking_time=None,
        estimated_cooking_time=0,
        instructions: dict = None,
    ):
        self.__recipe = recipe
        self.__ingredients = dict(ingredients)
        self.__available_ingredients = dict(available_ingredients or {})
        self.__ingredients_used = list(ingredients_used or [])
        self.__allergies = list(allergies or [])
        self.__dietary_preferences = list(dietary_preferences or [])
        self.__max_cooking_time = max_cooking_time
        self.__estimated_cooking_time = estimated_cooking_time
        self.__confidence = confidence
        self.__instructions = dict(instructions or {})

        # Composition: the record creates (and owns) its Quantity objects
        self.__required_quantities = {
            name: Quantity.parse(raw) for name, raw in self.__ingredients.items()
        }
        self.__available_quantities = {
            name: Quantity.parse(raw)
            for name, raw in self.__available_ingredients.items()
        }

    # Read-only access: callers get copies, so nobody can mutate the record
    @property
    def recipe(self) -> str:
        return self.__recipe

    @property
    def ingredients(self) -> dict:
        return dict(self.__ingredients)

    @property
    def available_ingredients(self) -> dict:
        return dict(self.__available_ingredients)

    @property
    def ingredients_used(self) -> list:
        return list(self.__ingredients_used)

    @property
    def allergies(self) -> list:
        return list(self.__allergies)

    @property
    def dietary_preferences(self) -> list:
        return list(self.__dietary_preferences)

    @property
    def confidence(self) -> float:
        return self.__confidence

    @property
    def cooking_time_limit(self):
        """The user's max cooking time in minutes, or None if there isn't one."""
        return self.__max_cooking_time

    @property
    def estimated_cooking_time(self):
        return self.__estimated_cooking_time

    @property
    def instructions(self) -> dict:
        return dict(self.__instructions)

    @property
    def required_quantities(self) -> dict:
        """Ingredient name -> Quantity the recipe calls for."""
        return dict(self.__required_quantities)

    @property
    def available_quantities(self) -> dict:
        """Ingredient name -> Quantity the user has."""
        return dict(self.__available_quantities)


# ===========================================================================
# === Validation of the raw (AI-enriched) dict ==============================
# ===========================================================================
class RecordValidator:
    """Single job: turn the raw merged dict (user input + AI response) into a
    RecipeRecord, or raise InvalidRecordError explaining what is wrong.
    Guards the business rules against acting on a malformed AI response."""

    def validate(self, raw: dict) -> RecipeRecord:
        if not isinstance(raw, dict):
            raise InvalidRecordError("record", "must be a dict")

        return RecipeRecord(
            recipe=self.__require(raw, "recipe", str),
            ingredients=self.__str_key_dict(raw, "ingredients", required=True),
            confidence=self.__check_confidence(raw.get("confidence")),
            available_ingredients=self.__str_key_dict(raw, "available_ingredients"),
            ingredients_used=self.__str_list(raw, "ingredients_used"),
            allergies=self.__str_list(raw, "allergies"),
            dietary_preferences=self.__str_list(raw, "dietary_preferences"),
            max_cooking_time=self.__number(
                raw, "max_cooking_time_minutes", default=None, allow_none=True
            ),
            estimated_cooking_time=self.__number(
                raw, "estimated_cooking_time_minutes", default=0
            ),
            instructions=self.__str_key_dict(raw, "instructions"),
        )

    # --- Private helpers ---
    def __require(self, raw: dict, field: str, expected_type: type):
        if field not in raw:
            raise InvalidRecordError(field, "is missing")

        value = raw[field]
        if not isinstance(value, expected_type):
            raise InvalidRecordError(field, f"must be a {expected_type.__name__}")

        return value

    def __str_key_dict(self, raw: dict, field: str, required: bool = False) -> dict:
        value = self.__require(raw, field, dict) if required else raw.get(field, {})

        if not isinstance(value, dict):
            raise InvalidRecordError(field, "must be a dict")

        if not all(isinstance(key, str) for key in value):
            raise InvalidRecordError(field, "must only have text keys")

        return value

    def __str_list(self, raw: dict, field: str) -> list:
        value = raw.get(field, [])

        if not isinstance(value, list):
            raise InvalidRecordError(field, "must be a list")

        if not all(isinstance(item, str) for item in value):
            raise InvalidRecordError(field, "must only contain text")

        return value

    def __number(self, raw: dict, field: str, default, allow_none: bool = False):
        value = raw.get(field, default)

        if value is None and allow_none:
            return None

        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise InvalidRecordError(field, "must be a number")

        return value

    def __check_confidence(self, value) -> float:
        message = "must be a number between 0 and 1"

        if value is None:
            raise InvalidRecordError("confidence", "is missing")

        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise InvalidRecordError("confidence", message)

        if not 0 <= value <= 1:
            raise InvalidRecordError("confidence", message)

        return value


# ===========================================================================
# === Rule results ==========================================================
# ===========================================================================
class RuleResult:
    """What one rule found. Created by a rule, then owned by an Evaluation."""

    def __init__(
        self,
        rule_name: str,
        passed: bool,
        details: dict,
        severity: Severity,
        failure_reason: str,
        label: str = None,
    ):
        self.__rule_name = rule_name
        self.__passed = passed
        self.__details = dict(details)
        self.__severity = severity
        self.__failure_reason = failure_reason
        self.__label = label or rule_name

    @property
    def rule_name(self) -> str:
        return self.__rule_name

    @property
    def passed(self) -> bool:
        return self.__passed

    @property
    def details(self) -> dict:
        return dict(self.__details)

    @property
    def severity(self) -> Severity:
        return self.__severity

    @property
    def failure_reason(self) -> str:
        return self.__failure_reason

    def to_dict(self) -> dict:
        """Same shape the Phase 1 rule functions returned."""
        return {"rule": self.__label, "passed": self.__passed, **self.__details}


class Evaluation:
    """The outcome of running every rule against one record.
    Owns its RuleResults. Does not decide a final outcome - that's the router's job."""

    def __init__(self, recipe: str, results: Iterable[RuleResult]):
        self.__recipe = recipe
        self.__results = list(results)

    @property
    def recipe(self) -> str:
        return self.__recipe

    @property
    def results(self) -> tuple:
        return tuple(self.__results)

    def failed(self, severity: Severity) -> list:
        """Failed results of the given severity, in rule order."""
        return [
            result
            for result in self.__results
            if not result.passed and result.severity is severity
        ]

    def result_for(self, rule_name: str) -> RuleResult:
        for result in self.__results:
            if result.rule_name == rule_name:
                return result

        raise KeyError(rule_name)

    def all_passed(self) -> bool:
        return all(result.passed for result in self.__results)

    def to_dict(self) -> dict:
        """Same decision dict shape the Phase 1 evaluate() returned."""
        return {
            "recipe": self.__recipe,
            "rule_results": {
                result.rule_name: result.to_dict() for result in self.__results
            },
        }


# ===========================================================================
# === Rules: interface -> abstract base class -> concrete rules =============
# ===========================================================================
class IRule(ABC):
    """Interface (contract) every business rule must honour."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique name of the rule."""

    @property
    @abstractmethod
    def severity(self) -> Severity:
        """BLOCKING rules reject on failure, ADVISORY rules flag."""

    @abstractmethod
    def evaluate(self, record: RecipeRecord) -> RuleResult:
        """Run the rule. Must return a RuleResult for any valid RecipeRecord."""


class BaseRule(IRule):
    """Abstract class holding the behaviour every rule shares (name, severity,
    and building the RuleResult). Subclasses only supply the rule itself."""

    def __init__(self, name: str, severity: Severity, result_label: str = None):
        self._name = name
        self._severity = severity
        self._result_label = result_label or name

    @property
    def name(self) -> str:
        return self._name

    @property
    def severity(self) -> Severity:
        return self._severity

    def evaluate(self, record: RecipeRecord) -> RuleResult:
        # Template method: shared steps here, the rule-specific part in _check()
        details = dict(self._check(record))
        passed = bool(details.pop("passed"))

        return RuleResult(
            self._name,
            passed,
            details,
            self._severity,
            self.failure_reason(),
            self._result_label,
        )

    @abstractmethod
    def _check(self, record: RecipeRecord) -> dict:
        """Return {"passed": bool, ...any details to report}."""

    @abstractmethod
    def failure_reason(self) -> str:
        """Short text used in the routing reason when this rule fails."""


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


class AllergyRule(BaseRule):
    """Reject any recipe that conflicts with a stated allergy."""

    def __init__(self):
        super().__init__("allergy_restrictions", Severity.BLOCKING)

    def _check(self, record: RecipeRecord) -> dict:
        allergies = {a.strip().lower() for a in record.allergies}
        ingredients = {i.strip().lower() for i in record.ingredients}
        conflicts = allergies & ingredients

        return {"passed": len(conflicts) == 0, "conflicting_allergens": sorted(conflicts)}

    def failure_reason(self) -> str:
        return "allergy conflict"


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


class RuleEvaluator:
    """Runs a set of rules against a record. Holds the rules it is given
    (aggregation: rules can exist and be reused outside this evaluator).
    Treats every rule as an IRule - no type-specific branching."""

    def __init__(self, rules: Iterable[IRule]):
        self.__rules = []

        for rule in rules:
            self.add_rule(rule)

        if not self.__rules:
            raise ValueError("RuleEvaluator needs at least one rule.")

    def add_rule(self, rule: IRule) -> None:
        if any(existing.name == rule.name for existing in self.__rules):
            raise ValueError(f"A rule named '{rule.name}' is already registered.")

        self.__rules.append(rule)

    def evaluate(self, record: RecipeRecord) -> Evaluation:
        return Evaluation(record.recipe, [rule.evaluate(record) for rule in self.__rules])


# ===========================================================================
# === Scoring: interface -> concrete scorer =================================
# ===========================================================================
class IScorer(ABC):
    """Interface (contract) for anything that can score a record from 0-100."""

    @abstractmethod
    def score(self, record: RecipeRecord) -> float:
        """Return a number from 0 to 100."""


class ScoringWeights:
    """How much each factor counts towards the score. Must add up to 1."""

    def __init__(
        self, confidence: float = 0.5, ingredients: float = 0.35, time: float = 0.15
    ):
        weights = (confidence, ingredients, time)

        if any(weight < 0 for weight in weights) or not math.isclose(sum(weights), 1.0):
            raise ValueError("Scoring weights must be non-negative and add up to 1.")

        self.__confidence = confidence
        self.__ingredients = ingredients
        self.__time = time

    @property
    def confidence(self) -> float:
        return self.__confidence

    @property
    def ingredients(self) -> float:
        return self.__ingredients

    @property
    def time(self) -> float:
        return self.__time


class WeightedScorer(IScorer):
    """Produces a 0-100 score used to rank candidate recipes. Rewards high AI
    confidence, then having the ingredients on hand, then staying within the
    time budget. Owns its ScoringWeights."""

    def __init__(
        self, confidence: float = 0.5, ingredients: float = 0.35, time: float = 0.15
    ):
        self.__weights = ScoringWeights(confidence, ingredients, time)

    def score(self, record: RecipeRecord) -> float:
        weighted = (
            (record.confidence * self.__weights.confidence)
            + (self.__ingredient_ratio(record) * self.__weights.ingredients)
            + (self.__time_ratio(record) * self.__weights.time)
        )

        return round(weighted * 100, 1)

    def __ingredient_ratio(self, record: RecipeRecord) -> float:
        needed = {i.strip().lower() for i in record.ingredients_used}
        have = {i.strip().lower() for i in record.available_ingredients}

        return len(needed & have) / len(needed) if needed else 1.0

    def __time_ratio(self, record: RecipeRecord) -> float:
        max_time = record.cooking_time_limit
        estimated = record.estimated_cooking_time

        if max_time and estimated > max_time:
            return max(0.0, min(1.0, 1 - (estimated - max_time) / max_time))

        return 1.0


# ===========================================================================
# === Routing ===============================================================
# ===========================================================================
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
        evaluation: Evaluation = None,
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
    def evaluation(self) -> Evaluation:
        return self.__evaluation

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


# ===========================================================================
# === The Logic Manager =====================================================
# ===========================================================================
class LogicManager:
    """Domain brain: applies the business rules to an AI-enriched record.
    Public API mirrors Phase 1: evaluate(), score(), route(), route_batch().

        - Composition: it creates and owns its RuleEvaluator and OutcomeRouter.
        - Aggregation: the scorer is injected (any IScorer) and the rules it
          runs are injected (any IRule) - both can exist without this manager.
        - Association: it uses a RecordValidator to check every incoming record.
    """

    def __init__(
        self,
        scorer: IScorer = None,
        rules: Iterable[IRule] = None,
        validator: RecordValidator = None,
    ):
        self.__validator = validator if validator is not None else RecordValidator()
        self.__evaluator = RuleEvaluator(
            rules if rules is not None else self.default_rules()
        )
        self.__scorer = scorer if scorer is not None else WeightedScorer()
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
    def __sort_key(decision: RoutingDecision) -> tuple:
        return (list(Outcome).index(decision.outcome), -decision.score)

    @staticmethod
    def __rejected_as_invalid(record, error: InvalidRecordError) -> RoutingDecision:
        name = record.get("recipe") if isinstance(record, dict) else None
        recipe = name if isinstance(name, str) else "Unknown Recipe"

        return RoutingDecision(
            recipe, Outcome.REJECT, f"invalid AI record: {error}", 0.0, {}, {}
        )
