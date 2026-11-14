# test_logic_manager.py
# Unit tests for the OOP Logic Manager. They run with no live AI API: every
# "AI response" below is a hardcoded sample record.
import copy
import inspect

import pytest

import logic_manager
from logic_manager import (
    AIConfidenceRule,
    AllergyRule,
    BaseRule,
    CookingTimeRule,
    DietaryRule,
    Evaluation,
    IngredientAvailabilityRule,
    InvalidRecordError,
    IRule,
    IScorer,
    LogicManager,
    LogicManagerError,
    Outcome,
    Quantity,
    RecipeRecord,
    RecordValidator,
    RoutingDecision,
    RuleEvaluator,
    RuleResult,
    ScoringWeights,
    Severity,
    WeightedScorer,
)


# ==========================================
# Helpers
# ==========================================
def make_record(**overrides):
    """A fully compliant sample AI-enriched record. Override fields per test."""
    record = {
        "recipe": "Simple Chicken Rice",
        "ingredients": {"chicken": "200g", "rice": "150g"},
        "available_ingredients": {"chicken": "300g", "rice": "200g"},
        "ingredients_used": ["chicken", "rice"],
        "allergies": [],
        "dietary_preferences": [],
        "max_cooking_time_minutes": 45,
        "estimated_cooking_time_minutes": 30,
        "confidence": 0.95,
        "instructions": {"1": {"step": "Cook chicken and rice", "time_taken": "20min"}},
    }
    record.update(overrides)
    return record


@pytest.fixture
def manager():
    return LogicManager()


@pytest.fixture
def typed_record():
    return RecordValidator().validate(make_record())


# ==========================================
# 1. BUSINESS RULES + ROUTING
# ==========================================
def test_compliant_record_is_accepted(manager):
    decision = manager.route(make_record())
    assert decision.outcome is Outcome.ACCEPT
    assert decision.reason == "all business rules passed"
    assert decision.score == 97.5


def test_allergy_conflict_rejects_even_with_high_confidence(manager):
    decision = manager.route(
        make_record(
            ingredients={"peanuts": "50g"},
            available_ingredients={"peanuts": "100g"},
            ingredients_used=["peanuts"],
            allergies=["Peanuts"],  # case-insensitive match
            confidence=0.99,
        )
    )
    assert decision.outcome is Outcome.REJECT
    assert decision.reason == "allergy conflict"
    assert decision.score == 99.5  # a high score does not rescue a safety failure
    assert decision.evaluation.result_for("allergy_restrictions").details == {
        "conflicting_allergens": ["peanuts"]
    }


def test_low_confidence_rejects(manager):
    decision = manager.route(make_record(confidence=0.59))
    assert decision.outcome is Outcome.REJECT
    assert decision.reason == "AI confidence too low"


def test_confidence_exactly_at_threshold_passes(manager):
    assert manager.route(make_record(confidence=0.6)).outcome is Outcome.ACCEPT


def test_allergy_reason_takes_priority_over_low_confidence(manager):
    decision = manager.route(
        make_record(ingredients={"egg": "1"}, allergies=["egg"], confidence=0.1)
    )
    assert decision.outcome is Outcome.REJECT
    assert decision.reason == "allergy conflict"


@pytest.mark.parametrize(
    "allergic, confidence, expected",
    [
        (False, 0.9, Outcome.ACCEPT),  # neither condition
        (True, 0.9, Outcome.REJECT),  # allergy conflict only
        (False, 0.3, Outcome.REJECT),  # low AI confidence only
        (True, 0.3, Outcome.REJECT),  # both
    ],
)
def test_multi_condition_reject_rule(manager, allergic, confidence, expected):
    """Phase 1 multi-condition rule: reject if allergy conflict (AI ingredients
    vs user allergies) OR AI confidence below threshold."""
    record = make_record(
        allergies=["rice"] if allergic else [], confidence=confidence
    )
    assert manager.route(record).outcome is expected


def test_missing_ingredient_is_flagged(manager):
    decision = manager.route(
        make_record(available_ingredients={"chicken": "300g"})
    )
    assert decision.outcome is Outcome.FLAG
    assert decision.reason == "missing or insufficient ingredients"
    assert decision.evaluation.result_for("ingredient_availability").details == {
        "missing_ingredients": ["rice"]
    }


def test_insufficient_quantity_is_flagged(manager):
    decision = manager.route(
        make_record(available_ingredients={"chicken": "100g", "rice": "200g"})
    )
    assert decision.outcome is Outcome.FLAG
    assert decision.evaluation.result_for("ingredient_availability").details == {
        "missing_ingredients": ["chicken"]
    }


def test_availability_skips_comparison_when_units_differ(manager):
    # Phase 1 behaviour, kept on purpose: amounts are only compared when the
    # units match (or one side has no unit), so 2kg vs 200g is not flagged.
    decision = manager.route(
        make_record(ingredients={"rice": "200g"}, available_ingredients={"rice": "2kg"})
    )
    assert decision.evaluation.result_for("ingredient_availability").passed


def test_over_time_is_flagged(manager):
    decision = manager.route(
        make_record(max_cooking_time_minutes=20, estimated_cooking_time_minutes=30)
    )
    assert decision.outcome is Outcome.FLAG
    assert decision.reason == "exceeds max cooking time"


def test_no_time_limit_means_cooking_time_passes(manager):
    record = make_record(estimated_cooking_time_minutes=999)
    del record["max_cooking_time_minutes"]
    assert manager.route(record).outcome is Outcome.ACCEPT


def test_dietary_rule_flags_when_diet_name_is_an_ingredient(manager):
    # Phase 1 rule, kept as-is: it matches the diet name against ingredient names.
    decision = manager.route(
        make_record(
            ingredients={"vegan": "10g"},
            available_ingredients={"vegan": "10g"},
            dietary_preferences=["Vegan"],
        )
    )
    assert decision.outcome is Outcome.FLAG
    assert decision.reason == "dietary preference not met"


def test_several_advisory_failures_are_combined_in_rule_order(manager):
    decision = manager.route(
        make_record(
            ingredients={"vegan": "10g", "rice": "150g"},
            available_ingredients={"vegan": "10g"},
            dietary_preferences=["vegan"],
            max_cooking_time_minutes=10,
            estimated_cooking_time_minutes=30,
        )
    )
    assert decision.outcome is Outcome.FLAG
    assert decision.reason == (
        "missing or insufficient ingredients, "
        "dietary preference not met, "
        "exceeds max cooking time"
    )


def test_evaluate_runs_all_five_rules_in_order(manager):
    evaluation = manager.evaluate(make_record())
    assert isinstance(evaluation, Evaluation)
    assert [r.rule_name for r in evaluation.results] == [
        "ingredient_availability",
        "allergy_restrictions",
        "dietary_restrictions",
        "cooking_time",
        "ai_confidence",
    ]
    assert evaluation.all_passed()


def test_route_dict_keeps_the_phase_1_shape(manager):
    """data_manager / io_manager read the decision with .get(), so the dict
    shape must not change."""
    result = manager.route(make_record()).to_dict()
    assert set(result) == {
        "recipe", "outcome", "reason", "score",
        "rule_results", "ingredients", "instructions",
    }
    assert result["outcome"] == "accept" and isinstance(result["outcome"], str)
    assert set(result["rule_results"]) == {
        "ingredient_availability", "allergy_restrictions",
        "dietary_restrictions", "cooking_time", "ai_confidence",
    }
    assert result["rule_results"]["ai_confidence"] == {
        "rule": "ai_confidence_threshold",
        "passed": True,
        "confidence": 0.95,
        "threshold": 0.6,
    }
    assert result["instructions"] == make_record()["instructions"]


# ==========================================
# 2. SCORING
# ==========================================
def test_score_full_marks_when_everything_fits(manager):
    assert manager.score(make_record(confidence=1.0)) == 100.0


def test_score_blends_confidence_ingredients_and_time(manager):
    # confidence 0.8 -> 0.40 ; half the used ingredients on hand -> 0.35*0.5 ;
    # 45 min vs 30 min limit -> time ratio 0.5 -> 0.15*0.5   => 65.0
    record = make_record(
        confidence=0.8,
        available_ingredients={"chicken": "300g"},
        estimated_cooking_time_minutes=45,
        max_cooking_time_minutes=30,
    )
    assert manager.score(record) == 65.0


def test_score_time_penalty_never_goes_below_zero(manager):
    record = make_record(
        confidence=1.0, estimated_cooking_time_minutes=500, max_cooking_time_minutes=30
    )
    assert manager.score(record) == 85.0  # 0.5 + 0.35 + 0 -> time ratio floored at 0


def test_score_without_ingredients_used_counts_as_complete(manager):
    record = make_record(confidence=1.0)
    del record["ingredients_used"]
    assert manager.score(record) == 100.0


def test_custom_weights_change_the_score():
    scorer = WeightedScorer(confidence=1.0, ingredients=0.0, time=0.0)
    manager = LogicManager(scorer=scorer)
    assert manager.score(make_record(confidence=0.7)) == 70.0


@pytest.mark.parametrize("weights", [(0.5, 0.5, 0.5), (-0.5, 1.0, 0.5), (0.2, 0.2, 0.2)])
def test_scoring_weights_must_be_non_negative_and_sum_to_one(weights):
    with pytest.raises(ValueError):
        ScoringWeights(*weights)


# ==========================================
# 3. BATCH ROUTING
# ==========================================
def test_route_batch_ranks_accept_then_flag_then_reject_by_score(manager):
    reject = make_record(recipe="D-reject", allergies=["rice"], confidence=0.99)
    flag = make_record(recipe="C-flag", available_ingredients={"chicken": "300g"})
    accept_low = make_record(recipe="B-accept", confidence=0.7)
    accept_high = make_record(recipe="A-accept", confidence=0.95)

    ranked = manager.route_batch([reject, flag, accept_low, accept_high])

    assert [d.recipe for d in ranked] == ["A-accept", "B-accept", "C-flag", "D-reject"]
    assert [d.score for d in ranked[:3]] == [97.5, 85.0, 80.0]


def test_route_batch_of_nothing_is_empty(manager):
    assert manager.route_batch([]) == []


def test_route_batch_isolates_a_malformed_record(manager):
    bad = make_record(recipe="Broken", confidence="very high")
    ranked = manager.route_batch([bad, make_record(recipe="Good")])

    assert [d.recipe for d in ranked] == ["Good", "Broken"]
    assert ranked[1].outcome is Outcome.REJECT
    assert ranked[1].reason.startswith("invalid AI record")


# ==========================================
# 4. AI-OUTPUT VALIDATION (error cases)
# ==========================================
@pytest.mark.parametrize(
    "bad_fields, expected_field",
    [
        ({"recipe": 42}, "recipe"),
        ({"ingredients": ["chicken"]}, "ingredients"),
        ({"ingredients": {1: "2g"}}, "ingredients"),
        ({"confidence": "high"}, "confidence"),
        ({"confidence": 1.5}, "confidence"),
        ({"confidence": -0.1}, "confidence"),
        ({"confidence": True}, "confidence"),
        ({"confidence": float("nan")}, "confidence"),
        ({"allergies": "peanuts"}, "allergies"),
        ({"allergies": [1, 2]}, "allergies"),
        ({"dietary_preferences": "vegan"}, "dietary_preferences"),
        ({"available_ingredients": None}, "available_ingredients"),
        ({"ingredients_used": "rice"}, "ingredients_used"),
        ({"max_cooking_time_minutes": "30"}, "max_cooking_time_minutes"),
        ({"estimated_cooking_time_minutes": None}, "estimated_cooking_time_minutes"),
        ({"instructions": None}, "instructions"),
    ],
)
def test_malformed_field_raises_invalid_record_error(manager, bad_fields, expected_field):
    with pytest.raises(InvalidRecordError) as error:
        manager.route(make_record(**bad_fields))
    assert error.value.field == expected_field
    assert expected_field in str(error.value)


@pytest.mark.parametrize("missing", ["recipe", "ingredients", "confidence"])
def test_missing_required_field_raises_invalid_record_error(manager, missing):
    record = make_record()
    del record[missing]
    with pytest.raises(InvalidRecordError) as error:
        manager.route(record)
    assert error.value.field == missing


@pytest.mark.parametrize("not_a_record", [None, "text", 42, ["a"], ()])
def test_non_dict_record_raises_invalid_record_error(manager, not_a_record):
    with pytest.raises(InvalidRecordError) as error:
        manager.route(not_a_record)
    assert error.value.field == "record"


def test_every_public_entry_point_guards_against_bad_records(manager):
    bad = make_record(confidence=2)
    for call in (manager.evaluate, manager.score, manager.route):
        with pytest.raises(InvalidRecordError):
            call(bad)


def test_invalid_record_error_is_a_logic_manager_error():
    assert issubclass(InvalidRecordError, LogicManagerError)


def test_optional_fields_can_be_left_out(manager):
    minimal = {"recipe": "Plain Rice", "ingredients": {"rice": "100g"}, "confidence": 0.9}
    decision = manager.route(minimal)
    assert decision.outcome is Outcome.FLAG  # nothing on hand -> missing ingredient


def test_validation_does_not_modify_the_callers_record(manager):
    record = make_record()
    snapshot = copy.deepcopy(record)
    manager.route(record)
    assert record == snapshot


# ==========================================
# 5. QUANTITY (replaces Phase 1 parse_quantity)
# ==========================================
@pytest.mark.parametrize(
    "raw, amount, unit",
    [
        ("200g", 200.0, "g"),
        ("1.5 KG", 1.5, "kg"),
        ("  40 ml ", 40.0, "ml"),
        ("2", 2.0, ""),
        (5, 5.0, ""),
        (2.5, 2.5, ""),
        ("abc", 0.0, ""),
        ("", 0.0, ""),
        ("1.2.3", 0.0, ""),
        (None, 0.0, ""),
        ([1], 0.0, ""),
    ],
)
def test_quantity_parse(raw, amount, unit):
    quantity = Quantity.parse(raw)
    assert (quantity.amount, quantity.unit) == (amount, unit)


def test_quantity_comparison_helpers():
    assert Quantity(200, "g").is_comparable_to(Quantity(5, "g"))
    assert Quantity(200, "g").is_comparable_to(Quantity(5))  # one side has no unit
    assert not Quantity(200, "g").is_comparable_to(Quantity(5, "ml"))
    assert Quantity(200, "g").covers(Quantity(200, "g"))
    assert not Quantity(100, "g").covers(Quantity(200, "g"))


