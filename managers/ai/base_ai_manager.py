# --- Imports --- #
from abc import ABC, abstractmethod
from models import RecipeRequest, AIResult
from .ai_client import AIClient


# --- Classes --- #
class BaseAIManager(ABC):
    """Abstract base class for AI managers. Subclasses implement process to handle recipe requests and return AI results."""
    def __init__(self, client: AIClient):
        # Store the AI client for making API calls
        self._client = client

    @abstractmethod
    def process(self, request: RecipeRequest) -> AIResult:
        """Processes a recipe request and returns an AIResult."""
        pass
