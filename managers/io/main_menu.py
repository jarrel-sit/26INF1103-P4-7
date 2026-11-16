# --- Imports --- #
from .menu import Menu

# --- Classes --- #
class MainMenu(Menu):
     def __init__(self):
          super().__init__(choices=6)

     def display_menu_text(self):
          self._displayer.display_menu(self,
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
=================================""")