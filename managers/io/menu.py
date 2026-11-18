# --- Imports --- #
from abc import ABC, abstractmethod
from .display import Display
from .menu_validator import MenuValidator


# --- Classes --- #
class Menu(ABC):
    """Abstract base class for menu and its children classes"""

    def __init__(self, choices: int, validator: MenuValidator, displayer: Display):
        self.choices = choices
        self._validator = validator
        self._displayer = displayer

    @abstractmethod
    def display_menu_text(self) -> None:
        """Displays the menu options to the user."""
        pass

    def get_choice(self) -> str:
        """Prompts the user for a menu choice and validates it."""
        while True:
            user_choice = input("> ").strip()
            success = self.validate_choice(user_choice)
            if success:
                self.choice = user_choice
                return self.choice
            else:
                self._displayer.display_error("Invalid Option, please choose again")

    def validate_choice(self, user_choice: str) -> bool:
        """Validates the user's menu choice."""
        return self._validator.validate(choice=user_choice, option_count=self.choices)

    def execute(self) -> str:
        """Displays the menu and gets a validated choice from the user."""
        self.display_menu_text()
        return self.get_choice()
