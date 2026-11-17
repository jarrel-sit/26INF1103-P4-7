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
        ingredients = self._collect_ingredients(available_ingredients)

        return RecipeRequest(
            ingredients=ingredients,
            available_ingredients=available_ingredients,
            allergies=allergy,
            dietary_preferences=diet,
            pax=1,
        )

    # Recieves input for diet
    def _collect_diet(self):
        self.user_diet = None
        while True:
            diet = (
                input(
                    "Do you have any dietary restrictions? Input none if not applicable: \n"
                )
                .lower()
                .strip()
            )
            success = self.__validator.validate_diet(diet, self.dietlist)

            if success:
                self.user_diet = diet
                return self.user_diet
            elif not success and diet == "none":
                self.user_diet = None
            else:
                continue
            return

    # Recieves input for allergy
    def _collect_allergy(self):
        self.user_allergies = []
        while True:
            allergy = (
                input(
                    "Do you have any allergies? Input if any, input done when there are no more allergies to be input: \n"
                )
                .lower()
                .strip()
            )
            success = self.__validator.validate_allergy(allergy, self.allergylist)

            if success:
                self.user_allergies.append(allergy)
                print(self.user_allergies)
            elif not success and allergy == "done":
                return self.user_allergies
            

    # Recieves input for ingredients
    def _collect_ingredients(self, available_ingredients: list[str] = None):
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
