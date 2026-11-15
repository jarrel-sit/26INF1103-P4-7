
from abc import ABC, abstractmethod


class RecipeRepository(ABC):
    """Contract for storing and querying evaluated recipes."""

    @abstractmethod
    def save(self, recipe, result):
        pass

    @abstractmethod
    def find_all(self):
        pass

    @abstractmethod
    def find_successful(self):
        pass

    @abstractmethod
    def find_by_ingredient(self, name):
        pass