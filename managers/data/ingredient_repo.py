# --- Imports --- #
from abc import abstractmethod
from .repository import Repository


# --- Classes --- #
class IngredientRepository(Repository):
    """Contract for storing and loading the user's ingredients."""

    @abstractmethod
    def find_all(self):
        pass

    @abstractmethod
    def delete(self, name):
        pass
