# --- Imports --- #
from abc import abstractmethod
import re
from .repository import Repository


# --- Classes --- #
class IngredientRepository(Repository):
    """Contract for storing and loading the user's ingredients."""

    @abstractmethod
    def find_all(self) -> list:
        """Returns all ingredients as a list of dictionaries."""
        pass

    @abstractmethod
    def delete(self, name: str) -> bool:
        """Deletes an ingredient by name. Returns True if the deletion succeeded."""
        pass

    @abstractmethod
    def update(self, name: str, quantity: str) -> bool:
        """Updates the quantity of an ingredient. Returns True if the update succeeded."""
        pass

    @staticmethod
    def add_quantities(old: str, new: str) -> str:
        """'100g' + '100g' -> '200g'. If the units differ, the new quantity replaces the old."""
        old_match = re.match(r"^(\d+(?:\.\d+)?)([a-zA-Z]*)$", str(old).strip())
        new_match = re.match(r"^(\d+(?:\.\d+)?)([a-zA-Z]*)$", str(new).strip())

        if old_match and new_match and old_match.group(2) == new_match.group(2):
            total = float(old_match.group(1)) + float(new_match.group(1))
            return f"{total:g}{new_match.group(2)}"

        return new
