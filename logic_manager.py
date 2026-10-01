# === Imports ===
from typing import Any

# == Rule Functions ===
def check_ingredient_availability(record: dict) -> dict:
    """
    Rule: Only recommend meals/recipes using ingredients the user has, or flag what needs to be bought.
    """
    needed = {i.strip().lower() for i in record.get("ingredients_used", [])}
    have = {i.strip().lower() for i in record.get("available_ingredients", [])}
    missing = sorted(needed - have)
 
    return {
        "rule": "ingredient_availability",
        "passed": len(missing) == 0,
        "missing_ingredients": missing,
    }

def check_allergy_restrictions(record: dict) -> dict:
    """
    Rule: Exclude/reject any recipe that conflicts with a stated allergy.
    """
    allergies = {a.strip().lower() for a in record.get("allergies", [])}
    ingredients = {i.strip().lower() for i in record.get("ingredients_used", [])}
    tags = {t.strip().lower() for t in record.get("tags", [])}
    conflicts = sorted((allergies & ingredients) | (allergies & tags))
 
    return {
        "rule": "allergy_restrictions",
        "passed": len(conflicts) == 0,
        "conflicting_allergens": conflicts,
    }

def check_dietary_restrictions(record: dict) -> dict:
    """
    Rule: Recipe must follow the user's selected dietary requirements
    """
    required = {d.strip().lower() for d in record.get("dietary_preferences", [])}
    tags = {t.strip().lower() for t in record.get("tags", [])}
    unmet = sorted(required - tags)
 
    return {
        "rule": "dietary_restrictions",
        "passed": len(unmet) == 0,
        "unmet_preferences": unmet,
    }

def check_cooking_time(record: dict) -> dict:
    """
    Rule: Recipe should match the user's max cooking-time preference
    where possible.
    """
    max_time = record.get("max_cooking_time_minutes")
    estimated = record.get("estimated_cooking_time_minutes", 0)
    within_range = max_time is None or estimated <= max_time
 
    return {
        "rule": "cooking_time",
        "passed": within_range,
        "estimated_minutes": estimated,
        "max_minutes": max_time,
    }

def check_ai_confidence(record: dict, min_confidence: float = 0.6) -> dict:
    """Guards logic_manager against acting on a low-confidence AI response."""
    score_val = record.get("confidence_score", 0.0)
 
    return {
        "rule": "ai_confidence_threshold",
        "passed": score_val >= min_confidence,
        "confidence_score": score_val,
        "threshold": min_confidence,
    }

# ==========================================
# === Required Framework 1/3: Evaluation ===
# ==========================================
def evaluate(record: dict) -> dict:
    """Runs every business rule against the AI-enriched record and returns a
    decision dict: each rule's pass/fail plus details. Does not decide a
    final outcome itself - that's route()'s job."""
    return {
        "recipe_name": record.get("recipe_name"),
        "rule_results": {
            "ingredient_availability": check_ingredient_availability(record),
            "allergy_restrictions": check_allergy_restrictions(record),
            "dietary_restrictions": check_dietary_restrictions(record),
            "cooking_time": check_cooking_time(record),
            "ai_confidence": check_ai_confidence(record),
        },
    }