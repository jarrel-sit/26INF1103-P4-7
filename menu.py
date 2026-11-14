#Imports
from abc import ABC, abstractmethod
from display import Display
#Menu and its Children Classes (Main Menu and Submenu)
class Menu(ABC):
     def __init__(self, choices):
          self.choices = choices
          self._validator = MenuValidator
          self._displayer = Display

     @abstractmethod
     def display_menu_text(self):
          pass

     def get_choice(self):
          user_choice = input("> ")
          success = self.validate_choice(user_choice)
          if success:
               self.choice = user_choice
               return self.choice
          else:
               self._displayer.display_error(self, "Invalid Option, please choose again")

     def validate_choice(self, user_choice):
          self._validator.validate(user_choice, self.choices)
          pass

     def execute(self):
          self.display_menu_text()
          self.get_choice()

#MainMenu Child Class
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

#SubMenu Child Class
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
          

#Validator for Menu Choices
class MenuValidator:
     def validate(choice: str, option_count: int):
          if choice.isdigit() and int(choice) > 0 and int(choice) <= option_count:
               return True