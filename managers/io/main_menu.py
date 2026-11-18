# --- Imports --- #
from .menu import Menu
from .display import Display
from .menu_validator import MenuValidator
import re


# --- Classes --- #
class MainMenu(Menu):
    def __init__(self, validator: MenuValidator, displayer: Display):
        super().__init__(choices=8, validator=validator, displayer=displayer)

    def display_menu_text(self):
        self._displayer.display_menu(
            """
=================================
|           Main Menu           |
|-------------------------------|
|                               |
|  1. Add new ingredients       |
|  2. List current ingredients  |
|  3. Recommend me a recipe!    |
|  4. View past recipes         |
|  5. Delete an ingredient      |
|  6. Edit ingredient quantity  |
|  7. Configure rule settings   |
|  8. Exit                      |
|                               |
=================================""",
        )

    def select_to_delete(self, ingredients: dict) -> str | None:
        """Prompts the user to select an ingredient to delete from a list."""
        self._displayer.display_menu(
            "\nSelect an ingredient to delete:\n"
            + "\n".join(
                f"{i + 1}. {ingredient}" for i, ingredient in enumerate(ingredients)
            )
            + f"\n{len(ingredients) + 1}. Cancel",
        )

        original_choice = self.choices
        self.choices = len(ingredients) + 1  # Update choices for validation

        choice = self.get_choice()

        if choice == str(self.choices):  # Cancel option
            output = None

        else:
            output = list(ingredients.keys())[int(choice) - 1]

        self.choices = original_choice  # Restore original choices
        return output

    def select_to_update(self, available: dict):
        """Returns (name, quantity), or (None, None) if cancelled or invalid."""
        name = input(
            "Enter the ingredient name to update (leave empty to cancel): "
        ).strip().lower()
        if not name:
            return None, None

        if name not in available:
            print(f"'{name}' is not in your ingredients.")
            return None, None

        quantity = input("Enter the new quantity (e.g., '250g'): ").strip().lower()
        if not re.fullmatch(r"\d+(?:\.\d+)?(g|ml)", quantity):
            print("Invalid quantity. Use a number followed by g or ml, e.g. 250g.")
            return None, None

        return name, quantity
