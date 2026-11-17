# --- Imports --- #
from .recipe_request_validator import RecipeRequestValidator
from .display import Display
from models import RecipeRequest

# Collects all the inputs needed for the recipe
class RecipeRequestCollector:
    def __init__(
        self,
        validator: RecipeRequestValidator,
        display: Display,
        dietlist=["vegetarian", "vegan", "pescetarian", "halal", "kosher"],
        allergylist=["milk", "soy", "fish", "peanuts", "nuts", "almonds", "eggs"],
    ):
        self.dietlist = dietlist
        self.allergylist = allergylist
        self.__validator = validator
        self._display = display

    # Consolidates diet,allergy and ingredients
    def collect_input(self, available_ingredients: list[str] = None) -> list | None:
        diet = self._collect_diet()
        allergy = self._collect_allergy()

        self._display.display_ingredients(available_ingredients)
        ingredients = self.collect_ingredients(available_ingredients)

        return RecipeRequest(
            ingredients=ingredients,
            available_ingredients=available_ingredients,
            allergies=allergy,
            dietary_preferences=diet,
            pax=1,
        )

    # Recieves input for diet
    def _collect_diet(self):
        self.user_diet = []
        self._display.display_logs("\nList of known diets")
        for i in self.dietlist:
            self._display.display_logs(f"- {i.capitalize()}")
        while True:
            diet = (
                input(
                    "\nDo you have any of these dietary restrictions? Input done when there are no more diets to input: \n"
                )
                .lower()
                .strip()
            )
            success = self.__validator.validate_diet(diet, self.dietlist)

            if diet == "done":
                return self.user_diet

            elif success:
                self.user_diet.append(diet)
        

    # Recieves input for allergy
    def _collect_allergy(self):
        self.user_allergies = []
        self._display.display_logs("\nList of known allergies")
        for i in self.allergylist:
            self._display.display_logs(f"- {i.capitalize()}")
        
        while True:
            allergy = (
                input(
                    "\n Do you have any of these allergies? Input if any, input done when there are no more allergies to be input: \n"
                )
                .lower()
                .strip()
            )
            success = self.__validator.validate_allergy(allergy, self.allergylist)

            if allergy == "done":
                return self.user_allergies
                
            elif success:
                self.user_allergies.append(allergy)
                
            

    # Recieves input for ingredients
    def collect_ingredients(self, available_ingredients: list[str] = None):
        self.user_ingredients = {}
        while True:
            ingredient = input(
                "Input ingredients and quantity, following this format E.g: apple 50g \n"
            ).lower().strip()
            
            
            success = self.__validator.validate_ingredients(
                ingredient, available_ingredients
            )
            if success:
                self.user_ingredients.update(success)
            elif not success and ingredient == "done":
                return self.user_ingredients
