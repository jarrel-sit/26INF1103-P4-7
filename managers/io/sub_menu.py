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

        self._displayer.display_logs(f"  {idx+1}. Cancel")

        # Temporarily match choices to the dynamic list length
        original_choices = self.choices
        self.choices = len(used_ingredients) + 1  # +1 for the cancel option

        choice = self.get_choice()

        if choice == str(self.choices):  # Cancel option
            output = None

        else:
            output = used_ingredients[int(choice) - 1]

        self.choices = original_choices  # Restore original choices
        return output

    def select_recipe(self, recipes: list[RoutingDecision]) -> RoutingDecision | None:
        """Prompts the user to pick a recipe from a displayed list."""
        if not recipes:
            return None

        self._displayer.display_logs(
            f"Enter recipe number to view details (1-{len(recipes)}, or {len(recipes)+1} to cancel): "
        )

        original_choices = self.choices
        self.choices = len(recipes) + 1  # +1 for the cancel option

        choice = self.get_choice()

        if choice == str(self.choices):  # Cancel option
            output = None

        else:
            output = recipes[int(choice) - 1]

        self.choices = original_choices  # Restore original choices
        return output
