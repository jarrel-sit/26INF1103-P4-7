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

# =======================================
# === Required Framework 2/3: Scoring ===
# =======================================
def score(record: dict) -> float:
    """
    Produces a numeric score (0-100) from AI output fields, used to rank
    multiple candidate recipes against each other. Rewards high AI
    confidence, ingredient completeness, and staying under the time budget.
    """
    confidence = record.get("confidence_score", 0.0)
 
    needed = set(record.get("ingredients_used", []))
    have = {i.strip().lower() for i in record.get("available_ingredients", [])}
    needed_lower = {i.strip().lower() for i in needed}
    ingredient_ratio = (
        len(needed_lower & have) / len(needed_lower) if needed_lower else 1.0
    )
 
    max_time = record.get("max_cooking_time_minutes")
    estimated = record.get("estimated_cooking_time_minutes", 0)
    if max_time:
        time_ratio = max(0.0, min(1.0, 1 - (estimated - max_time) / max_time)) \
            if estimated > max_time else 1.0
    else:
        time_ratio = 1.0
 
    # Weighted blend: 
    # AI confidence matters most, 
    # then having the ingredients on hand, 
    # then staying within the time budget.
    weighted = (confidence * 0.5) + (ingredient_ratio * 0.35) + (time_ratio * 0.15)
    return round(weighted * 100, 1)

# =======================================
# === Required Framework 3/3: Routing ===
# =======================================
def route(record: dict) -> dict:
    """
    Combines evaluate() and score() to assign the record to an outcome path:
    "reject", "flag", or "accept".
        - REJECT if there's an allergy conflict OR AI confidence is below
          threshold. Safety/trust issues get no partial credit regardless
          of score.
        - FLAG if ingredients are missing, a dietary preference isn't met,
          or it runs over time - any one of these, or a combination.
        - ACCEPT only if every rule passes.
    """
    decision = evaluate(record)
    results = decision["rule_results"]
    numeric_score = score(record)
 
    allergy_conflict = not results["allergy_restrictions"]["passed"]
    low_confidence = not results["ai_confidence"]["passed"]
    missing_ingredients = not results["ingredient_availability"]["passed"]
    diet_unmet = not results["dietary_restrictions"]["passed"]
    over_time = not results["cooking_time"]["passed"]
 
    if allergy_conflict or low_confidence:
        outcome = "reject"
        reason = "allergy conflict" if allergy_conflict else "AI confidence too low"
    elif missing_ingredients or diet_unmet or over_time:
        outcome = "flag"
        reasons = []
        if missing_ingredients:
            reasons.append("missing ingredients")
        if diet_unmet:
            reasons.append("dietary preference not met")
        if over_time:
            reasons.append("exceeds max cooking time")
        reason = ", ".join(reasons)
    else:
        outcome = "accept"
        reason = "all business rules passed"
 
    return {
        "recipe_name": record.get("recipe_name"),
        "outcome": outcome,
        "reason": reason,
        "score": numeric_score,
        "rule_results": results,
    }
 
def route_batch(records: list) -> list:
    """
    Convenience wrapper: route() a list of candidate records and return
    them ranked accept -> flag -> reject, highest score first within each
    group, so data_manager/io_manager get an ordered list to save/display.
    """
    outcome_order = {"accept": 0, "flag": 1, "reject": 2}
    routed = [route(r) for r in records]
    return sorted(routed, key=lambda r: (outcome_order[r["outcome"]], -r["score"]))