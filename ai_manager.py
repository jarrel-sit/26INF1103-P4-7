# --- Imports --- #
from google import genai
from dotenv import load_dotenv
import os, json, time
from abc import ABC, abstractmethod
from models import (
    GeneratedRecipe,
    Instruction,
    RecipeRequest,
    AIResult,
    ValidationResult,
)

# --- Load Environment Variables --- #
load_dotenv(dotenv_path="./.env")
API_KEY = os.getenv("GENAI_API_KEY")


# ==========================================
class AIClient(ABC):
    @abstractmethod
    def generate(self, prompt: str) -> str:
        pass


class GeminiClient(AIClient):
    def __init__(self, api_key: str):
        self._client = genai.Client(api_key=api_key)
        self._model = "gemini-3.1-flash-lite"


    def generate(self, prompt: str) -> str:
        # Implementation for calling the underlying client
        interaction =self._client.interactions.create(
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




class RecipeValidator:
    def validate(self, response: GeneratedRecipe) -> ValidationResult:
        errors: list[str] = []

        if not isinstance(response.name, str) or not response.name.strip():
            errors.append("Recipe name is missing or not a non-empty string.")

        if not isinstance(response.ingredients, dict):
            errors.append(
                "Ingredients value is missing or not of the expected type (dict)."
            )

        if not isinstance(response.instructions, dict):
            errors.append(
                "Instructions value is missing or not of the expected type (dict)."
            )
        else:
            for step_key, instruction_obj in response.instructions.items():
                if not isinstance(step_key, str) or not step_key.isdigit():
                    errors.append(f"Step '{step_key}' key is not a numeric string.")

                if not isinstance(instruction_obj, Instruction):
                    errors.append(
                        f"Value of step '{step_key}' is not an Instruction object."
                    )
                else:
                    if (
                        not isinstance(instruction_obj.step, str)
                        or not instruction_obj.step.strip()
                    ):
                        errors.append(
                            f"Field 'step' in step '{step_key}' must be a non-empty string."
                        )

                    if (
                        not isinstance(instruction_obj.time_taken, str)
                        or not instruction_obj.time_taken.strip()
                    ):
                        errors.append(
                            f"Field 'time_taken' in step '{step_key}' must be a non-empty string."
                        )

        if (
            response.confidence is None
            or not isinstance(response.confidence, (int, float))
            or response.confidence < 0
            or response.confidence > 1
        ):
            errors.append("Confidence value must be a number between 0 and 1.")

        if not isinstance(response.equipment, list):
            errors.append(
                "Equipment value is missing or not of the expected type (list)."
            )

        if not isinstance(response.insufficient_ingredients, bool):
            errors.append("Insufficient Ingredients value must be a boolean.")

        return ValidationResult(is_valid=len(errors) == 0, errors=errors)


class BaseAIManager(ABC):
    @abstractmethod
    def process(self, request: RecipeRequest) -> AIResult:
        pass


class GeminiAIManager(BaseAIManager):
    def __init__(
        self, client: AIClient, validator: RecipeValidator, max_retries: int = 3
    ):
        self._client = client
        self._validator = validator
        self._max_retries = max_retries

    def process(self, request: RecipeRequest) -> AIResult:
        prompt = self._build_prompt(request)
        raw_response = self.call_api(prompt)
        recipe = self._parse_response(raw_response)

        validation = self._validator.validate(recipe)
        if validation.is_valid:
            return AIResult(success=True, recipe=recipe)
        else:
            return AIResult(success=False, error=", ".join(validation.errors))

    def _build_prompt(self, request: RecipeRequest) -> str:
        """
        Function to build the prompt for the API call.
        """
        ingredients_str = ", ".join(
            f"{ingredient} ({quantity})"
            for ingredient, quantity in request.ingredients.items()
        )
        allergies_str = ", ".join(request.allergies) if request.allergies else "None"
        dietary_preferences_str = (
            ", ".join(request.dietary_preferences)
            if request.dietary_preferences
            else "None"
        )
        pax_str = str(request.pax) if request.pax else "1"

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
        
        Ingredients: {ingredients_str}, 

        Allergies: {allergies_str},

        Dietary Preferences: {dietary_preferences_str},

        Serving size: {pax_str},
      
        The response should be in JSON format with the following keys and types: 
        {', '.join([f'{key}: {value}' for key, value in REQUIRED_KEYS.items()])}
        Examples of instructions should be formatted as: 
            "instructions": {{
                "1": {{ "step": 'Instruction 1', "time_taken": '5min' }}, 
                "2": {{ "step": 'Instruction 2', "time_taken": '2min' }},
            }}
            """
        return prompt
    
    def call_api(self, prompt: str = "", max_retries: int = 3, delay: int = 2) -> str:
        # Retries the API calls, only fail if all tries unsuccessful
        for attempt in range(1, max_retries + 1):
            try:
                response = self._client.generate(prompt)
                return response
            except Exception as e:
                # Handles retries
                if attempt < max_retries:
                    # Wait in increasing timeframes
                    time.sleep(delay * attempt)
                    continue
    
                # Catches network drops or client-side issues outside the stream loop
                return f"Transport or connection exception: {e}"
    def _parse_response(self, raw: str) -> GeneratedRecipe:
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
            raw = raw[4:]
    
        # Parse the response as JSON and handle any parsing errors
        try:
            response = json.loads(raw)
            instructions_dict = {
                key: Instruction(**value) for key, value in response.get("instructions", {}).items()
            }
            return GeneratedRecipe(
                name=response.get("recipe", ""),
                ingredients=response.get("ingredients", {}),
                instructions=response.get("instructions", {}),
                confidence=response.get("confidence", 0),
                dietary_preferences=response.get("dietary_preferences", []),
                hazardous_ingredients=response.get("hazardous_ingredients", {}),
                equipment=response.get("equipment", []),
                insufficient_ingredients=response.get("insufficient_ingredients", False)
            )

        except json.JSONDecodeError as e:
            return f"JSON parsing error: {e} \nResponse content: {raw}"
    



# --- Constants --- #
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
