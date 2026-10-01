# === Imports ===
from typing import Any

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