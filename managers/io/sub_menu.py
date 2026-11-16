# --- Imports --- #
from .menu import Menu


# --- Classes --- #
class SubMenu(Menu):
    def __init__(self):
        super().__init__(choices=4)

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
