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
|  5. Exit                      |
|                               |
=================================""",
        )
