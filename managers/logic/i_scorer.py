from abc import ABC, abstractmethod
from .recipe_record import RecipeRecord


# IScorer ==== interface for anything that can score a recipe

class IScorer(ABC):
    """Interface (contract) for anything that can score a record from 0-100."""

    @abstractmethod
    def score(self, record: RecipeRecord) -> float:
        """Return a number from 0 to 100."""