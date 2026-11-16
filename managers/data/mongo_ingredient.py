# --- Imports --- #
from datetime import datetime
from pymongo.errors import PyMongoError
from .mongo_repository import MongoRepository
from .ingredient_repo import IngredientRepository
from .quantity import add_quantities


# --- Classes --- #
class MongoIngredientRepository(MongoRepository, IngredientRepository):
    def __init__(self, uri, db_name, logger=None):
        super().__init__(uri, db_name, "ingredients", logger=logger)

    def find_all(self):
        """Returns {ingredient: quantity} for everything saved."""
        return {row["ingredient"]: row["quantity"] for row in self.load()}

    def save(self, ingredients):
        """Adds new ingredients and adds up quantities of existing ones."""
        if not ingredients:
            return False

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            for name, quantity in ingredients.items():
                name = str(name).strip().lower()
                existing = self._collection.find_one({"_id": name})

                if existing:
                    quantity = add_quantities(existing["quantity"], quantity)

                # upsert: insert if the ingredient is new, otherwise update it
                self._collection.update_one(
                    {"_id": name},
                    {"$set": {"quantity": quantity, "updated": timestamp}},
                    upsert=True,
                )

        except PyMongoError as error:
            self._log(f"[Data Manager] Database error: {error}")
            return False

        return True

    def delete(self, name):
        """Deletes the ingredient with the given name. Returns True if one was deleted."""
        name = str(name).strip().lower()

        try:
            result = self._collection.delete_one({"_id": name})
        except PyMongoError as error:
            self._log(f"[Data Manager] Database error: {error}")
            return False

        return result.deleted_count > 0

    def _process_document(self, document):
        """Turns a stored document into an ingredient record."""
        return {
            "ingredient": document["_id"],
            "quantity": document["quantity"],
            "timestamp": document.get("updated", ""),
        }