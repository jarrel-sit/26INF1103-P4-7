# --- Imports --- #
from abc import abstractmethod
from .repository import Repository


# --- Classes --- #
class RecipeRepository(Repository):
    """Contract for storing and querying evaluated recipes."""

    @abstractmethod
    def find_all(self) -> list:
        """Returns all recipes as a list of RoutingDecision objects."""
        pass

    @abstractmethod
    def find_successful(self) -> list:
        """Returns all recipes with an outcome of 'accept' as a list of RoutingDecision objects."""
        pass

    @abstractmethod
    def find_by_ingredient(self, name: str) -> list:
        """Returns all recipes that contain the given ingredient name (case-insensitive) as a list of RoutingDecision objects."""
        pass
