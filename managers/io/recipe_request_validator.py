# --- Imports --- #
import re
from .cli_display import CLIDisplay

# --- Classes --- #
class RecipeRequestValidator:
    """Validates all the inputs needed for the recipe"""

    def __init__(self):
        self.input_pattern = r"([A-Za-z]+(?:\s[A-Za-z]+)*)\s*(\d+)\s*(g|ml)$"
        self.quantity_pattern = r"(\d+)\s*(g|ml)"
        self._display = CLIDisplay()
    # Validation for diet
    def validate_diet(self, diet, dietlist):
        if diet in dietlist:
            self._display.display_logs(f"Taken note of {diet} dietary restriction, we will ensure that generated recipes adhere to {diet} dietary restrictions.")
                #f"Taken note of {diet} dietary restriction, we will ensure that generated recipes adhere to {diet} dietary restrictions."
            return True
        else:
            log = f"We do not recognise this diet type. Ensure you typed it in correctly."
            self._display.display_error(log)

    # Validation for allergy
    def validate_allergy(self, allergy, allergylist):
        if allergy in allergylist:
            log =  f"Taken note of {allergy} allergy, we will not include {allergy} in your generated recipes"
            self._display.display_logs(log)
            return True
        else:
            log = f"We do not recognise this allergy. Ensure you typed it in correctly."
            self._display.display_error(log)

    # Validation for ingredients
    def validate_ingredients(self, ingredient, available_ingredients=None):
        match = re.match(self.input_pattern, ingredient)
        if match and re.search(r"[^\w\s]", ingredient) is None:
            name = match.group(1)
            if (
                match.group(2).isnumeric()
                and match.group(3) == "ml"
                or match.group(3) == "g"
            ):
                if available_ingredients is not None:
                    success = self.validate_quantity(
                        name, match.group(2), match.group(3), available_ingredients
                    )

                else:
                    success = True # When adding new ingredients, we don't need to check against available ingredients

                if success:
                    quantity = match.group(2) + match.group(3)
                    log = f"Valid input received. {name.title()} {quantity} has been added to the ingredients list."
                    self._display.display_logs(log)
                    ingredient = {name: quantity}

                    return ingredient

        else:
            log = "Invalid item detected. Please ensure that ingredient entered follows the proper format."
            self._display.display_error(log)

    def validate_quantity(self, ingredient, quantity, unit, available_ingredients):
        """Validates the quantity of the ingredient input by the user."""
        if ingredient in available_ingredients:
            match = re.match(self.quantity_pattern, available_ingredients[ingredient])

            available_quantity = match.group(1)
            available_unit = match.group(2)

            if (
                quantity.isdigit()
                and unit == available_unit
                and int(quantity) <= int(available_quantity)
            ):
                return True

        self._display.display_error (f"Invalid quantity for {ingredient.title()}. Please ensure the quantity is within available stock.")
        return False
