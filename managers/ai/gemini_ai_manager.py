# --- Imports --- #
import time, json
from models import RecipeRequest, AIResult, GeneratedRecipe, Instruction
from .base_ai_manager import BaseAIManager
from .gemini_client import GeminiClient
from .recipe_validator import RecipeValidator


# --- Classes --- #
class GeminiAIManager(BaseAIManager):
    def __init__(
        self, client: GeminiClient, validator: RecipeValidator, max_retries: int = 3
    ):
        self._client = client
        self._validator = validator
        self._max_retries = max_retries
        self.required_keys = {
            "recipe": "str",
            "ingredients": "dict",
            "instructions": "dict",
            "confidence": "int or float",
            "dietary_preferences": "list",
            "hazardous_ingredients": "dict",
            "equipment": "list",
            "insufficient_ingredients": "bool",
        }

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
        {', '.join([f'{key}: {value}' for key, value in self.required_keys.items()])}
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

    def _parse_response(self, raw: str) -> GeneratedRecipe | str:
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
                key: Instruction(**value)
                for key, value in response.get("instructions", {}).items()
            }
            return GeneratedRecipe(
                name=response.get("recipe", ""),
                ingredients=response.get("ingredients", {}),
                instructions=response.get("instructions", {}),
                confidence=response.get("confidence", 0),
                dietary_preferences=response.get("dietary_preferences", []),
                hazardous_ingredients=response.get("hazardous_ingredients", {}),
                equipment=response.get("equipment", []),
                insufficient_ingredients=response.get(
                    "insufficient_ingredients", False
                ),
            )

        except json.JSONDecodeError as e:
            return f"JSON parsing error: {e} \nResponse content: {raw}"
