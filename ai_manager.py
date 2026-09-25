# --- Imports --- #
from google import genai
from google.genai import errors
from dotenv import load_dotenv
import os
import json

# --- Load Environment Variables --- #
load_dotenv(dotenv_path="./.env")
API_KEY = os.getenv("GENAI_API_KEY")


# --- Constants --- #
CLIENT = genai.Client(api_key=API_KEY)
REQUIRED_KEYS = [
    "recipe",
    "ingredients",
    "instructions",
    "confidence",
    "hazardous_ingredients",
    "equipment",
    "serving_size"
]  # placeholder for now, to be updated with actual input from user if necessary


# --- Functions --- #
def build_prompt(record: dict):
    """
    Function to build the prompt for the API call.
    """

    # Build the prompt string with the provided ingredients
    # TODO: Revamp prompt to include any additional input fields if necessary
    prompt = f"""You are a recipe generator. Generate a list of recipes using this list of ingredients and their provided amounts. 
    Not all ingredients/amounts have to be used to completion for each recipe but do not include ingredients or 
    quantities not listed. Take into consideration the user's diets and allergies inputted below as well. 
    Include the serving sizes and time taken for each recipe. Convert any quantities of online recipes found 
    online to grams and millimeters. Do not include any suggestions to modify the recipes. Include a list of 
    utensils needed, and time taken for each step of the recipe. Remove any hazardous or inedible ingredients 
    and write them at the bottom of the JSON file. Return the confidence level of the recipe recommendation 
    from 0 to 1 for evaluating it's usability.
    
    Ingredients: {', '.join(
        f"{ingredient} ({amount})" for ingredient, amount in zip(record['ingredients'], record['amount']) 
    )}, 

    Serving size: {record['pax']}
  
    The response should be in JSON format with the following keys: 
    'recipe', 'ingredients', 'instructions', 'confidence', 'hazardous_ingredients' and 'equipment'.
    """

    return prompt


def call_api(prompt: str = ""):
    """
    Function to call the API and handle the response.
    """

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
                print(f"Error Code: {event.error.code}")
                return event.error.message

            # Check if the event contains text delta chunks (successful responses)
            if (
                hasattr(event, "delta")
                and hasattr(event.delta, "text")
                and event.delta.text
            ):
                response += event.delta.text

        return response

    except Exception as e:
        # Catches network drops or client-side issues outside the stream loop
        return f"\nTransport or connection exception: {e}"


def parse_response(raw: str):
    """
    Function to parse the response from the API.
    """

    if not raw:
        return "No response received from the API."

    # Check for markdown formatting issues in the response, and fix them if necessary
    if raw.startswith("```") or raw.endswith("```"):
        raw = raw.strip("```").strip()

    # Parse the response as JSON and handle any parsing errors
    try:
        return json.loads(raw)

    except json.JSONDecodeError as e:
        return f"JSON parsing error: {e} \nResponse content: {raw}"


def validate_response(data: dict):
    """
    Function to validate the parsed response from the API.
    """

    # Validate that the parsed response is a dictionary and contains all required keys
    if not isinstance(data, dict):
        return "Parsed response is not a dictionary."

    missing_keys = [key for key in REQUIRED_KEYS if key not in data]

    if missing_keys:
        return f"Missing keys in the response: {', '.join(missing_keys)}"

    # Validate each required key for presence and correct type
    error_message = "is missing or not of the expected type."

    if (
        data.get("recipe") is None
        or not isinstance(data.get("recipe"), str)
        or data.get("recipe").strip() == ""
    ):
        return f"Recipe value {error_message}"

    if (
        data.get("ingredients") is None
        or not isinstance(data.get("ingredients"), str)
        or data.get("ingredients").strip() == ""
    ):
        return f"Ingredients value {error_message}."

    if (
        data.get("instructions") is None
        or not isinstance(data.get("instructions"), str)
        or data.get("instructions").strip() == ""
    ):
        return f"Instructions value {error_message}"

    if data.get("confidence") is None or not isinstance(
        data.get("confidence"), (int, float)
    ):
        return f"Confidence value {error_message}"

    return data


print(
    call_api(
        build_prompt(
            {"ingredients": ["chicken", "rice"], "amount": ["100g", "1kg"], "pax": 2}
        )
    )
)
