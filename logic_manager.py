# === Imports ===
from typing import Any

def check_ingredient_availability(record: dict) -> dict:
    """
    Rule: only recommend meals/recipes using ingredients the user has, or flag what needs to be bought.
    """
    needed = {i.strip().lower() for i in record.get("ingredients_used", [])}
    have = {i.strip().lower() for i in record.get("available_ingredients", [])}
    missing = sorted(needed - have)
 
    return {
        "rule": "ingredient_availability",
        "passed": len(missing) == 0,
        "missing_ingredients": missing,
    }