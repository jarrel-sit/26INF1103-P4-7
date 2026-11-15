
from abc import ABC, abstractmethod


class IngredientRepository(ABC):
    """Contract for storing and loading the user's ingredients."""

    @abstractmethod
    def save_all(self, ingredients):
        pass

    @abstractmethod
    def find_all(self):
        pass

    @abstractmethod
    def delete(self, name):
        pass