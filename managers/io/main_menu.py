# --- Imports --- #
from .menu import Menu
from .display import Display
from .menu_validator import MenuValidator


# --- Classes --- #
class MainMenu(Menu):
    def __init__(self, validator: MenuValidator, displayer: Display):
        super().__init__(choices=6, validator=validator, displayer=displayer)

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
|  6. Exit                      |
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
