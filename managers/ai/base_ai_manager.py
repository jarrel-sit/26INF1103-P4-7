# --- Imports --- #
from abc import ABC, abstractmethod
from models import RecipeRequest, AIResult


# --- Classes --- #
class BaseAIManager(ABC):
    @abstractmethod
    def process(self, request: RecipeRequest) -> AIResult:
        pass
