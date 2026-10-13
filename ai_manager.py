# --- Imports --- #
from google import genai
from dotenv import load_dotenv
import os, json, time

# --- Load Environment Variables --- #
load_dotenv(dotenv_path="./.env")
API_KEY = os.getenv("GENAI_API_KEY")


# --- Constants --- #
CLIENT = genai.Client(api_key=API_KEY)
REQUIRED_KEYS = {
    "recipe": "str",
    "ingredients": "dict",
    "instructions": "dict",
    "confidence": "int or float",
    "dietary_preferences": "list",
    "hazardous_ingredients": "dict",
    "equipment": "list",
    "insufficient_ingredients": "bool",
}


# --- Functions --- #
def build_prompt(record: dict):
    """
    Function to build the prompt for the API call.
    """

    # Build the prompt string with the provided ingredients
    prompt = f"""You are a recipe generator. Generate a recipe using this list of ingredients and their provided amounts. 
    Not all ingredients/amounts have to be used to completion for each recipe but do not include ingredients or 
    quantities not listed. Take into consideration the user's dietary preferences and allergies inputted below 
    as well. Include the serving sizes and time taken for each recipe. Convert any quantities of online recipes found 
    online to grams and millimeters. Do not include any suggestions to modify the recipes. Include a list of 
    utensils needed, and time taken for each step of the recipe. Include how much of each ingredient is used 
    in each step while describing the step. If there are not enough ingredients to make a legitimate recipe, 
    indicate true in the JSON file, otherwise indicate false. Remove any hazardous or inedible ingredients. 
    and write them at the bottom of the JSON file. Return the confidence level of the recipe recommendation 
    from 0 to 1 for evaluating it's usability. 

    If the recipe detects a conflict in dietary preferences/allergies and ingredients provided, try to avoid using them
    and put them into hazardous ingredients list. If it is possible to avoid the conflict, carry on as per 
    normal and return original outputs.
    
    However, if the recipe has to have ingredients provided that conflicts with dietary preferences/allergies, do not include 
    the conflicting dietary preferences/allergies within the response. The hazardous ingredients should also contain the 
    conflicting ingredients, then the confidence score should be strictly marked down in the case of conflict. 
    
    Ingredients: {', '.join(
        f"{ingredient} ({quantity})" for ingredient, quantity in record['ingredients'].items() 
    )}, 

    Allergies: {', '.join(record['allergies']) if record['allergies'] else 'None'},

    Dietary Preferences: {', '.join(record['dietary_preferences']) if record['dietary_preferences'] else 'None'},

    Serving size: {record['pax'] if record.get('pax') else '1'},
  
    The response should be in JSON format with the following keys and types: 
    {', '.join([f'{key}: {value}' for key, value in REQUIRED_KEYS.items()])}

    Examples of instructions should be formatted as: 
    instructions: {{
        1: {{ step: 'Instruction 1', time_taken: '5min' }}, 
        2: {{ step: 'Instruction 2', time_taken: '2min' }},
    }}

    Examples of dietary preferences/allergies should be formatted as:
    dietary_preferences: ['halal', 'vegetarian']
    allergies: ['fish', 'peanuts']
    """

    return prompt


def call_api(prompt: str = "", max_retries: int = 3, delay: int = 2):
    """
    Function to call the API and handle the response.
    """

    # Retries the API calls, only fail if all tries unsuccessful
    for attempt in range(1, max_retries + 1):
        try:
            response = ""
            interaction = CLIENT.interactions.create(
                model="gemini-3.1-flash-lite",
                input=prompt,
                stream=True,  # Enable streaming to receive partial responses as they are generated
            )

            for event in interaction:
                # Check for error events
                if hasattr(event, "error") and event.error:
                    return f"API Error ({event.error.code}): {event.error.message}"

                # Check if the event contains text delta chunks (successful responses)
                if (
                    hasattr(event, "delta")
                    and hasattr(event.delta, "text")
                    and event.delta.text
                ):
                    response += event.delta.text

            return response

        except Exception as e:
            # Handles retries
            if attempt < max_retries:
                # Wait in increasing timeframes
                time.sleep(delay * attempt)
                continue

            # Catches network drops or client-side issues outside the stream loop
            return f"Transport or connection exception: {e}"


def parse_response(raw: str):
    """
    Function to parse the response from the API.
    """

    if not raw:
        return "No response received from the API."

    # Check for markdown formatting issues in the response, and fix them if necessary
    if raw.startswith("```") or raw.endswith("```"):
        raw = raw.strip("```").strip()

    # Remove `json` header to parse
    if raw.startswith("json"):
        cleaned = raw[4:]

    # Parse the response as JSON and handle any parsing errors
    try:
        return json.loads(cleaned)

    except json.JSONDecodeError as e:
        return f"JSON parsing error: {e} \nResponse content: {cleaned}"


def validate_response(data: dict):
    """
    Function to validate the parsed response from the API.
    """
    error_header = "Validation Error:"

    # Validate that the parsed response is a dictionary and contains all required keys
    if not isinstance(data, dict):
        return f"{error_header} Parsed response is not a dictionary."

    missing_keys = [key for key in REQUIRED_KEYS.keys() if key not in data]

    if missing_keys:
        return f"{error_header} Missing keys in the response: {', '.join(missing_keys)}"

    # Validate each required key for presence and correct type
    error_message = "is missing or not of the expected type."

    recipe = data.get("recipe")
    ingredients = data.get("ingredients")
    instructions = data.get("instructions")
    confidence = data.get("confidence")
    equipment = data.get("equipment")
    insufficient_ingredients = data.get("insufficient_ingredients")
    diet = data.get("dietary_preferences")

    if recipe is None or not isinstance(recipe, str) or recipe.strip() == "":
        return f"{error_header} Recipe value {error_message}"

    if ingredients is None or not isinstance(ingredients, dict):
        return f"Ingredients value {error_message}"

    if instructions is None or not isinstance(instructions, dict):
        return f"{error_header} Instructions value {error_message}"

    else:
        for key, value in instructions.items():
            if not isinstance(key, str) or not key.isdigit():
                return f"{error_header} Step '{key}' is not a number."

            if not isinstance(value, dict):
                return f"{error_header} Value of step '{key}' is not a dictionary."

            required_subkeys = {"step", "time_taken"}
            missing_keys = required_subkeys - value.keys()

            if missing_keys:
                return f"{error_header} Step '{key}' is missing required fields: {list(missing_keys)}."

            for subkey in required_subkeys:
                if not isinstance(value[subkey], str) or not value[subkey].strip():
                    return f"{error_header} Field '{subkey}' in step '{key}' must be a non-empty string."

    if (
        confidence is None
        or not isinstance(confidence, (int, float))
        or confidence < 0
        or confidence > 1
    ):
        return f"{error_header} Confidence value {error_message}"

    if equipment is None or not isinstance(equipment, list):
        return f"{error_header} Equipment value {error_message}"

    if not isinstance(insufficient_ingredients, bool):
        return f"{error_header} Insufficient Ingredients value {error_message}"

    if not isinstance(diet, list):
        return f"{error_header} Dietary Preferences value {error_message}"

    return data


def process(record: dict):
    """
    Combines the entire AI pipeline into a single function.
    """

    prompt = build_prompt(record)
    raw_response = call_api(prompt)

    if (
        not raw_response
        or raw_response.startswith("API Error")
        or raw_response.startswith("\nTransport or connection exception")
    ):
        return False, raw_response

    parsed_response = parse_response(raw_response)

    if isinstance(parsed_response, str):
        return False, parsed_response

    validated_response = validate_response(parsed_response)
    if isinstance(validated_response, str):
        return False, validated_response

    return True, validated_response
