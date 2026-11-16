# --- Imports --- #
from abc import ABC, abstractmethod


# --- Classes --- #
class Display(ABC):
    """Abstract base class for display"""

    @abstractmethod
    def display_menu(self, menu):
        pass

    @abstractmethod
    def display_ingredients(self, ingredients):
        pass

    @abstractmethod
    def display_result(self, result):
        pass

    @abstractmethod
    def display_error(self, msg):
        pass

    @abstractmethod
    def display_logs(self, log):
        pass
