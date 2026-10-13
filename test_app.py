# test_app.py
import os

# Import your modules
import data_manager
import logic_manager
import ai_manager


# ==========================================
# 1. LOGIC MANAGER TESTS
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

    # ==========================================
# 2. DATA MANAGER PERSISTENCE TESTS
# ==========================================
def test_data_manager_save_and_load_success():
    """Test successful saving and loading of recipe records using flat files."""
    test_recipe_file = "test_recipe_data.csv"
    if os.path.exists(test_recipe_file):
        os.remove(test_recipe_file)

    sample_recipe = {
        "recipe": "Test Omelette",
        "outcome": "accept",
        "score": 90.5,
        "reason": "all business rules passed",
        "ingredients": {"egg": "2", "butter": "10g"},
        "instructions": {"1": {"step": "Beat eggs and fry", "time_taken": "5min"}}
    }
    
    # Save record
    saved = data_manager.save_recipe(sample_recipe, filepath=test_recipe_file)
    assert saved is True, "Failed to save record."

    # Load records back
    records = data_manager.load_recipes(filepath=test_recipe_file)
    assert len(records) == 1, f"Expected 1 record, got {len(records)}"
    assert records[0]["recipe"] == "Test Omelette"

    # Cleanup
    if os.path.exists(test_recipe_file):
        os.remove(test_recipe_file)


def test_data_manager_corrupt_file_handling():
    """Test that data_manager handles corrupted files gracefully without crashing."""
    test_recipe_file = "test_recipe_data.csv"
    with open(test_recipe_file, "w", encoding="utf-8") as f:
        f.write("corrupt,csv,data,without,proper,headers\ninvalid_row")

    records = data_manager.load_recipes(filepath=test_recipe_file)
    assert records == [], "Expected corrupt file to return an empty list."

    if os.path.exists(test_recipe_file):
        os.remove(test_recipe_file)


def test_query_and_filters():
    """Test querying and success filtering functions."""
    records = [
        {"recipe": "Recipe A", "outcome": "accept", "ingredients": {"chicken": "100g"}},
        {"recipe": "Recipe B", "outcome": "reject", "ingredients": {"peanuts": "50g"}},
    ]
    
    successful = data_manager.filter_by_success(records)
    assert len(successful) == 1
    assert successful[0]["recipe"] == "Recipe A"

# ==========================================
# 3. AI MANAGER VALIDATION & PARSING TESTS
# ==========================================
def test_ai_schema_validation_failure():
    """Test that missing required keys in hardcoded AI data are correctly caught and rejected."""
    incomplete_data = {
        "recipe": "Bad Recipe",
    }
    validation_result = ai_manager.validate_response(incomplete_data)
    assert isinstance(validation_result, str)
    assert "Missing keys" in validation_result


def test_ai_parse_response_malformed_json():
    """Test that parse_response safely catches bad JSON strings without crashing."""
    bad_raw_response = "This is not valid json text"
    result = ai_manager.parse_response(bad_raw_response)
    assert isinstance(result, str)
    assert "JSON parsing error" in result