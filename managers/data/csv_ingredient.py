# --- Imports --- #
from datetime import datetime
from .csv_repository import CsvRepository
from .ingredient_repo import IngredientRepository


# --- Classes --- #
class CsvIngredientRepository(CsvRepository, IngredientRepository):
    """Ingredient repository that stores data in a CSV file."""

    def __init__(self, filepath: str, fieldnames: list, logger=None):
        super().__init__(filepath, fieldnames, mode="w", logger=logger)

    def __next_session_id(self, rows: list) -> int:
        """Next session_id, based on rows already loaded."""
        ids = []
        for row in rows:
            try:
                ids.append(int(row.get("session_id", 0)))
            except (ValueError, TypeError):
                continue
        return max(ids, default=0) + 1

    def find_all(self) -> dict:
        """Returns {ingredient: quantity} for everything saved."""
        rows = self.load()
        return {row["ingredient"]: row["quantity"] for row in rows}

    def save(self, ingredients: dict) -> bool:
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
                existing[name]["quantity"] = self.add_quantities(
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

    def __filter_exclude_ingredient(self, name: str) -> list:
        """Returns all rows except those with the given ingredient name using query()."""
        name = str(name).strip().lower()
        return self.query(lambda r: str(r["ingredient"]).strip().lower() != name)

    def delete(self, name: str) -> bool:
        """Deletes all rows with the given ingredient name. Returns True if any rows were deleted."""
        remaining = self.__filter_exclude_ingredient(name)

        if len(remaining) == len(self.load()):
            # No rows were deleted
            return False

        return super().save(remaining)

    def _process_data_row(self, row: dict) -> dict:
        """Processes a row of data loaded from the CSV file. Validates that the row has the expected fields and formats.
        Raises ValueError if the row is invalid."""

        if not row.get("ingredient") or not row.get("quantity"):
            raise ValueError("missing ingredient/quantity")

        return row

    def update(self, name: str, quantity: str) -> bool:
        """Sets an ingredient's quantity to the given value (replaces, does not add).
        Returns True if the ingredient existed and was updated."""
        name = str(name).strip().lower()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        rows = self.load()

        found = False
        for row in rows:
            if str(row["ingredient"]).strip().lower() == name:
                row["quantity"] = quantity
                row["timestamp"] = timestamp
                found = True

        if not found:
            return False

        return super().save(rows)
