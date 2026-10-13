# test_app.py
import os

# Import your modules
import data_manager
import logic_manager
import ai_manager


# ==========================================
# 1. LOGIC MANAGER TESTS (Core Requirement 5.3)
# ==========================================
def test_logic_manager_success_routing():
    """Test that a fully compliant hardcoded AI response is evaluated and routed as 'accept'."""
    record = {
        "recipe": "Simple Chicken Rice",
        "ingredients": {"chicken": "200g", "rice": "150g"},
        "available_ingredients": {"chicken": "300g", "rice": "200g"},
        "allergies": [],
        "dietary_preferences": [],
        "max_cooking_time_minutes": 45,
        "estimated_cooking_time_minutes": 30,
        "confidence": 0.95,
        "ingredients_used": ["chicken", "rice"],
        "instructions": {"1": {"step": "Cook chicken and rice", "time_taken": "20min"}}
    }
    result = logic_manager.route(record)
    assert result["outcome"] == "accept", f"Expected 'accept', got {result['outcome']}"
    assert result["score"] >= 80.0

def test_logic_manager_allergy_failure():
    """Test that an allergy conflict forces a 'reject' outcome."""
    record = {
        "recipe": "Peanut Crunch",
        "ingredients": {"peanuts": "50g"},
        "available_ingredients": {"peanuts": "100g"},
        "allergies": ["peanuts"],
        "dietary_preferences": [],
        "max_cooking_time_minutes": 30,
        "estimated_cooking_time_minutes": 15,
        "confidence": 0.99,
        "instructions": {"1": {"step": "Mix peanuts", "time_taken": "5min"}}
    }
    result = logic_manager.route(record)
    assert result["outcome"] == "reject"
    assert "allergy conflict" in result["reason"].lower()