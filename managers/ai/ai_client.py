# --- Imports --- #
from abc import ABC, abstractmethod


# --- Classes --- #
class AIClient(ABC):
    @abstractmethod
    def generate(self, prompt: str) -> str:
        pass
