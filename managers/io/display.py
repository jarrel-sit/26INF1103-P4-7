# --- Imports --- #
from abc import ABC, abstractmethod
from managers.logic import RoutingDecision


# --- Classes --- #
class Display(ABC):
    """Abstract base class for display"""

    @abstractmethod
    def display_menu(self, menu: str) -> None:
        """Displays a menu to the user."""
        pass

    @abstractmethod
    def display_ingredients(self, ingredients: dict) -> None:
        """Displays the current list of available ingredients."""
        pass

    @abstractmethod
    def display_result(self, result: RoutingDecision) -> None:
        """Displays the details of a generated recipe, including its outcome, score, reason, ingredients, and instructions."""
        pass

    @abstractmethod
    def display_error(self, msg: str) -> None:
        """Displays error messages."""
        pass

    @abstractmethod
    def display_logs(self, log: str) -> None:
        """Displays verbose log messages."""
        pass
