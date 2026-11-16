# --- Imports --- #
import re


# --- Classes --- #
class RecipeRequestValidator:
    """Validates all the inputs needed for the recipe"""

    # Validation for diet
    def validate_diet(self, diet, dietlist):
        if diet in dietlist:
            print(
                f"Taken note of {diet} dietary restriction, we will ensure that generated recipes adhere to {diet} dietary restrictions."
            )
            return True

    # Validation for allergy
    def validate_allergy(self, allergy, allergylist):
        if allergy in allergylist:
            print(
                f"Taken note of {allergy} allergy, we will not include {allergy} in your generated recipes"
            )
            return True

    # Validation for ingredients
    def validate_ingredients(self, ingredient, available_ingredients):
        pattern = r"([A-Za-z]+(?:\s[A-Za-z]+)*)\s*(\d+)\s*(g|ml)"
        match = re.match(pattern, ingredient)
        if match and re.search(r"[^\w\s]", ingredient) is None:
            name = match.group(1)
            if (
                match.group(2).isnumeric()
                and match.group(3) == "ml"
                or match.group(3) == "g"
            ):
                if self.validate_quantity(name, match.group(2), available_ingredients):
                    quantity = match.group(2) + match.group(3)
                    print(
                        f"Valid input received. {name.title()} {quantity} has been added to the ingredients list."
                    )
                    ingredient = {name: quantity}

                    return ingredient

            else:
                print(
                    "Invalid item detected. Please ensure that ingredient entered follows the proper format."
                )

    def validate_quantity(self, ingredient, quantity, available_ingredients):
        """Validates the quantity of the ingredient input by the user."""
        if ingredient in available_ingredients:
            available_quantity = available_ingredients[ingredient]
            if quantity.isdigit() and int(quantity) <= int(
                re.search(r"\d+", available_quantity).group()
            ):
                return True

        print(
            f"Invalid quantity for {ingredient.title()}. Please ensure the quantity is within available stock."
        )
        return False
