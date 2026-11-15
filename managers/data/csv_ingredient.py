from datetime import datetime

from data_manager import (
    IngredientRepository,
    DEFAULT_FILEPATH,
    FIELDNAMES,
    load_ingredients,
    save,
    add_quantities,
)


class CsvIngredientRepository(IngredientRepository):
    def __init__(self, filepath=DEFAULT_FILEPATH, logger=None):
        self.__filepath = filepath
        self.__logger = logger

    def __next_session_id(self, rows):
        """Next session_id, based on rows already loaded."""
        ids = []
        for row in rows:
            try:
                ids.append(int(row.get("session_id", 0)))
            except (ValueError, TypeError):
                continue
        return max(ids, default=0) + 1

    def find_all(self):
        """Returns {ingredient: quantity} for everything saved."""
        rows = load_ingredients(self.__filepath, logger=self.__logger)
        return {row["ingredient"]: row["quantity"] for row in rows}

    def save_all(self, ingredients):
        """Adds new ingredients and adds up quantities of existing ones."""
        if not ingredients:
            return False

        rows = load_ingredients(self.__filepath, logger=self.__logger)
        session_id = self.__next_session_id(rows)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        existing = {str(r["ingredient"]).strip().lower(): r for r in rows}

        for name, quantity in ingredients.items():
            name = str(name).strip().lower()
            if name in existing:
                existing[name]["quantity"] = add_quantities(
                    existing[name]["quantity"], quantity
                )
                existing[name]["timestamp"] = timestamp
            else:
                rows.append({
                    "session_id": session_id,
                    "timestamp": timestamp,
                    "ingredient": name,
                    "quantity": quantity,
                })

        return save(self.__filepath, FIELDNAMES, rows, mode="w", logger=self.__logger)

    def delete(self, name):
        name = str(name).strip().lower()
        rows = load_ingredients(self.__filepath, logger=self.__logger)
        remaining = [r for r in rows if str(r["ingredient"]).strip().lower() != name]

        if len(remaining) == len(rows):      # nothing matched
            return False
        return save(self.__filepath, FIELDNAMES, remaining,
                    mode="w", logger=self.__logger)