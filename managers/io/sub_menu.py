# --- Imports --- #
from .menu import Menu
from .display import Display
from .menu_validator import MenuValidator
from managers.logic import RoutingDecision


# --- Classes --- #
class SubMenu(Menu):
    def __init__(self, validator: MenuValidator, displayer: Display):
        super().__init__(choices=4, validator=validator, displayer=displayer)

    def display_menu_text(self):
        self._displayer.display_menu("""
=================================
|      Past Recipes Submenu     |
|-------------------------------|
|  1. View All Saved Recipes    |
|  2. View Successful Only      |
|  3. Filter by Ingredient      |
|  4. Back to Main Menu         |
=================================""")

    def select_from_used(self, used_ingredients: list[str]) -> str | None:
        """Displays numbered ingredients from past recipes and returns the chosen one."""
        if not used_ingredients:
            self._displayer.display_error("No used ingredients found in past recipes.")
            return None

        self._displayer.display_logs("\nFilter Past Recipes by Ingredient:")
        for idx, name in enumerate(used_ingredients, start=1):
            self._displayer.display_logs(f"  {idx}. {name}")

        self._displayer.display_logs("  0. Cancel")

        while True:
            raw_choice = self.get_choice()

            if raw_choice == "0":
                return None

            if raw_choice.isdecimal():
                index = int(raw_choice) - 1
                if 0 <= index < len(used_ingredients):
                    return used_ingredients[index]

            self._displayer.display_error(
                f"Invalid selection. Enter a number between 0 and {len(used_ingredients)}."
            )

    def select_recipe(self, recipes: list[RoutingDecision]) -> RoutingDecision | None:
        """Prompts the user to pick a recipe from a displayed list."""
        if not recipes:
            return None

        while True:
            choice = input(
                f"Enter recipe number to view details (1-{len(recipes)}, or 0 to cancel): "
            ).strip()

            if choice == "0":
                return None

            if self._validator.validate(choice=choice, option_count=len(recipes)):
                return recipes[int(choice) - 1]

            self._displayer.display_error(
                f"Invalid selection. Enter a number between 0 and {len(recipes)}."
            )
