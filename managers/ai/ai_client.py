# --- Imports --- #
from abc import ABC, abstractmethod


# --- Classes --- #
class AIClient(ABC):
    """Abstract base class for AI clients. Subclasses implement generate to call the AI API."""

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Generates a response from the AI API based on the given prompt."""
        pass
