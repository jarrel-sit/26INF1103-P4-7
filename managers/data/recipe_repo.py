# --- Imports --- #
from abc import abstractmethod
from .repository import Repository


# --- Classes --- #
class RecipeRepository(Repository):
    """Contract for storing and querying evaluated recipes."""

    @abstractmethod
    def find_all(self) -> list:
        pass

    @abstractmethod
    def find_successful(self) -> list:
        pass

    @abstractmethod
    def find_by_ingredient(self, name) -> list:
        pass
