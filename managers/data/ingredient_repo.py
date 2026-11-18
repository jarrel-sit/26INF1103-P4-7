# --- Imports --- #
from abc import abstractmethod
import re
from .repository import Repository


# --- Classes --- #
class IngredientRepository(Repository):
    """Contract for storing and loading the user's ingredients."""

    @abstractmethod
    def find_all(self):
        pass

    @abstractmethod
    def delete(self, name):
        pass

    @staticmethod
    def add_quantities(old, new):
        """'100g' + '100g' -> '200g'. If the units differ, the new quantity replaces the old."""
        old_match = re.match(r"^(\d+(?:\.\d+)?)([a-zA-Z]*)$", str(old).strip())
        new_match = re.match(r"^(\d+(?:\.\d+)?)([a-zA-Z]*)$", str(new).strip())

        if old_match and new_match and old_match.group(2) == new_match.group(2):
            total = float(old_match.group(1)) + float(new_match.group(1))
            return f"{total:g}{new_match.group(2)}"

        return new
