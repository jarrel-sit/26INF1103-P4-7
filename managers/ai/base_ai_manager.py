# --- Imports --- #
from abc import ABC, abstractmethod
from models import RecipeRequest, AIResult
from .ai_client import AIClient


# --- Classes --- #
class BaseAIManager(ABC):
    def __init__(self, client: AIClient):
        self._client = client

    @abstractmethod
    def process(self, request: RecipeRequest) -> AIResult:
        pass
