# --- Imports --- #
import re
from datetime import datetime
from .csv_repository import CsvRepository
from .ingredient_repo import IngredientRepository


# --- Classes --- #
class CsvIngredientRepository(CsvRepository, IngredientRepository):
    def __init__(self, filepath, fieldnames, logger=None):
        super().__init__(filepath, fieldnames, mode="w", logger=logger)

    def __next_session_id(self, rows):
        """Next session_id, based on rows already loaded."""
        ids = []
        for row in rows:
            try:
                ids.append(int(row.get("session_id", 0)))
            except (ValueError, TypeError):
                continue
        return max(ids, default=0) + 1

    @staticmethod
    def __add_quantities(old, new):
        """'100g' + '100g' -> '200g'. If the units differ, the new quantity replaces the old."""
        old_match = re.match(r"^(\d+(?:\.\d+)?)([a-zA-Z]*)$", str(old).strip())
        new_match = re.match(r"^(\d+(?:\.\d+)?)([a-zA-Z]*)$", str(new).strip())

        if old_match and new_match and old_match.group(2) == new_match.group(2):
            total = float(old_match.group(1)) + float(new_match.group(1))
            return f"{total:g}{new_match.group(2)}"

        return new

    def find_all(self):
        """Returns {ingredient: quantity} for everything saved."""
        rows = self.load()
        return {row["ingredient"]: row["quantity"] for row in rows}

    def save(self, ingredients):
        """Adds new ingredients and adds up quantities of existing ones."""
        if not ingredients:
            return False

        rows = self.load()
        session_id = self.__next_session_id(rows)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        existing = {str(r["ingredient"]).strip().lower(): r for r in rows}

        for name, quantity in ingredients.items():
            name = str(name).strip().lower()

            if name in existing:
                # Add the new quantity to the existing quantity;
                # TODO: what if user wants to replace instead of add?
                # Maybe add a flag to indicate this.
                existing[name]["quantity"] = self.__add_quantities(
                    existing[name]["quantity"], quantity
                )
                existing[name]["timestamp"] = timestamp

            else:
                rows.append(
                    {
                        "session_id": session_id,
                        "timestamp": timestamp,
                        "ingredient": name,
                        "quantity": quantity,
                    }
                )

        return super().save(rows)

    def __filter_exclude_ingredient(self, name):
        """Returns all rows except those with the given ingredient name using query()."""
        name = str(name).strip().lower()
        return self.query(lambda r: str(r["ingredient"]).strip().lower() != name)

    def delete(self, name):
        """Deletes all rows with the given ingredient name. Returns True if any rows were deleted."""
        remaining = self.__filter_exclude_ingredient(name)

        if len(remaining) == len(self.load()):
            # No rows were deleted
            return False

        return super().save(remaining)

    def _process_data_row(self, row):
        """Processes a row of data loaded from the CSV file. Validates that the row has the expected fields and formats.
        Raises ValueError if the row is invalid."""

        if not row.get("ingredient") or not row.get("quantity"):
            raise ValueError("missing ingredient/quantity")

        return row
