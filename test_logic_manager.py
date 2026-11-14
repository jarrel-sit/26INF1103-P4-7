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


