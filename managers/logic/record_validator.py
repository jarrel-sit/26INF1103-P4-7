from .exceptions import InvalidRecordError
from .recipe_record import RecipeRecord

# RecordValidator ====

class RecordValidator:
    """Single job: turn the raw merged dict (user input + AI response) into a
    RecipeRecord, or raise InvalidRecordError explaining what is wrong.
    Guards the business rules against acting on a malformed AI response."""

    def validate(self, raw: dict) -> RecipeRecord:
        if not isinstance(raw, dict):
            raise InvalidRecordError("record", "must be a dict")

        return RecipeRecord(
            recipe=self.__require(raw, "recipe", str),
            ingredients=self.__str_key_dict(raw, "ingredients", required=True),
            confidence=self.__check_confidence(raw.get("confidence")),
            available_ingredients=self.__str_key_dict(raw, "available_ingredients"),
            ingredients_used=self.__str_list(raw, "ingredients_used"),
            allergies=self.__str_list(raw, "allergies"),
            dietary_preferences=self.__str_list(
                raw, "dietary_preferences", allow_text=True
            ),
            max_cooking_time=self.__number(
                raw, "max_cooking_time_minutes", default=None, allow_none=True
            ),
            estimated_cooking_time=self.__number(
                raw, "estimated_cooking_time_minutes", default=0
            ),
            instructions=self.__str_key_dict(raw, "instructions"),
        )

    # --- Private helpers ---
    def __require(self, raw: dict, field: str, expected_type: type):
        if field not in raw:
            raise InvalidRecordError(field, "is missing")

        value = raw[field]
        if not isinstance(value, expected_type):
            raise InvalidRecordError(field, f"must be a {expected_type.__name__}")

        return value

    def __str_key_dict(self, raw: dict, field: str, required: bool = False) -> dict:
        value = self.__require(raw, field, dict) if required else raw.get(field, {})

        if not isinstance(value, dict):
            raise InvalidRecordError(field, "must be a dict")

        if not all(isinstance(key, str) for key in value):
            raise InvalidRecordError(field, "must only have text keys")

        return value

    def __str_list(self, raw: dict, field: str, allow_text: bool = False) -> list:
        value = raw.get(field, [])

        # io_manager.diet() returns one text value ("" or "vegan"), not a list
        if allow_text and isinstance(value, str):
            return [value.strip()] if value.strip() else []

        if not isinstance(value, list):
            raise InvalidRecordError(field, "must be a list")

        if not all(isinstance(item, str) for item in value):
            raise InvalidRecordError(field, "must only contain text")

        return value

    def __number(self, raw: dict, field: str, default, allow_none: bool = False):
        value = raw.get(field, default)

        if value is None and allow_none:
            return None

        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise InvalidRecordError(field, "must be a number")

        return value

    def __check_confidence(self, value) -> float:
        message = "must be a number between 0 and 1"

        if value is None:
            raise InvalidRecordError("confidence", "is missing")

        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise InvalidRecordError("confidence", message)

        if not 0 <= value <= 1:
            raise InvalidRecordError("confidence", message)

        return value