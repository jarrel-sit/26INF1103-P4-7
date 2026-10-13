"""
data_manager.py

The "Data Manager" for the AI Recipe Planner - acts as the system's memory
across runs.

Responsibilities (per the architecture spec):
    1. Save processed records to a CSV spreadsheet.
    2. Load all records on startup.
    3. Provide at least one filter/query function.
    4. Handle missing or corrupt files without crashing.

A "record" here is one saved session: the ingredients the user entered
via io_manager.ingredient_input(). Each ingredient is stored as its own
row in the spreadsheet, tagged with a shared session_id and timestamp,
e.g.:

    session_id, timestamp,            ingredient, quantity
    1,          2026-09-25 10:00:00,  sugar,      100g
    1,          2026-09-25 10:00:00,  flour,      200g

(Diet and allergy info are left out for now - can be added back as
extra columns later if needed.)
"""

import csv, json
import os
from datetime import datetime

# Default location of the spreadsheet (CSV) that acts as persistent storage.
DEFAULT_FILEPATH = "ingredients_data.csv"
DEFAULT_RECIPES_FILEPATH = "recipe_data.csv"

# Column headers for the CSV spreadsheet.
FIELDNAMES = ["session_id", "timestamp", "ingredient", "quantity"]
RECIPE_FIELDNAMES = [
    "recipe",
    "outcome",
    "score",
    "reason",
    "ingredients",
    "instructions",
]


# ---------------------------------------------------------------------------
# 2. Load all records on startup (+ 4. handle missing/corrupt files)
# ---------------------------------------------------------------------------


def load(filepath, fieldnames, row_processor=None, logger=None):
    """
    Loads all saved records from the CSV spreadsheet specified.
    """

    if not os.path.exists(filepath):
        if logger:
            logger(
                f"[Data Manager] No existing data file found at '{filepath}'. Creating a new one."
            )

        _create_empty_file(filepath, fieldnames, logger=logger)
        return []

    records = []

    try:
        with open(filepath, mode="r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            if reader.fieldnames is None or set(reader.fieldnames) != set(fieldnames):
                if logger:
                    logger(
                        f"[Data Manager] Warning: '{filepath}' has an unexpected or missing "
                        f"header and appears corrupted. Starting with an empty record set."
                    )

                return []

            for row_number, row in enumerate(reader, start=2):  # row 1 is the header
                try:
                    if row_processor:
                        row = row_processor(row)

                    if row is not None:
                        records.append(row)

                except (ValueError, KeyError, json.JSONDecodeError) as row_error:
                    if logger:
                        logger(
                            f"[Data Manager] Warning: skipping corrupt row {row_number} "
                            f"in '{filepath}' ({row_error})."
                        )

                    continue

    except (csv.Error, OSError, UnicodeDecodeError) as file_error:
        if logger:
            logger(
                f"[Data Manager] Warning: could not read '{filepath}' ({file_error}). "
                f"Treating it as empty/corrupt and starting fresh."
            )

        return []

    if logger:
        logger(f"[Data Manager] Loaded {len(records)} record(s) from '{filepath}'.")

    return records


def load_ingredients(filepath=DEFAULT_FILEPATH, fieldnames=FIELDNAMES, logger=None):
    """Loads all ingredients from the CSV spreadsheet."""

    def process_ingredients_row(row):
        if not row.get("ingredient") or not row.get("quantity"):
            raise ValueError("missing ingredient/quantity")

        return row

    ingredients = load(filepath, fieldnames, process_ingredients_row, logger)

    return ingredients


def load_recipes(
    filepath=DEFAULT_RECIPES_FILEPATH, fieldnames=RECIPE_FIELDNAMES, logger=None
):
    """Loads all evaluated recipe records from the CSV spreadsheet."""

    def process_recipes_row(row):
        row["score"] = float(row.get("score", 0.0))
        row["ingredients"] = json.loads(row.get("ingredients", "[]"))
        row["instructions"] = json.loads(row.get("instructions", "[]"))
        return row

    recipes = load(filepath, fieldnames, process_recipes_row, logger)

    return recipes


def _create_empty_file(filepath, fieldnames=FIELDNAMES, logger=None):
    """Creates a new CSV spreadsheet with just the header row."""
    try:
        with open(filepath, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames)
            writer.writeheader()

    except OSError as error:
        if logger:
            logger(
                f"[Data Manager] Error: could not create data file '{filepath}' ({error})."
            )


# ---------------------------------------------------------------------------
# 1. Save processed records to CSV
# ---------------------------------------------------------------------------


def save(filepath, fieldnames, data, mode="a", logger=None):
    """Saves all records to specified CSV spreadsheet."""

    if not os.path.exists(filepath):
        _create_empty_file(filepath, logger)

    try:
        with open(filepath, mode=mode, newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)

            if mode == "w":
                writer.writeheader()
                writer.writerows(data)

            else:
                writer.writerow(data)

    except OSError as error:
        if logger:
            logger(f"[Data Manager] Error: could not save to '{filepath}' ({error}).")

        return False

    return True


def save_ingredients(
    ingredients_list, filepath=DEFAULT_FILEPATH, fieldnames=FIELDNAMES, logger=None
):
    """
    Saves a processed set of ingredients (as produced by
    io_manager.ingredient_input()) into the CSV spreadsheet, one row per
    ingredient, tagged with a shared session_id and timestamp.

    ingredients_list: dict like {"sugar": "100g", "flour": "200g"}
    filepath: path to the CSV spreadsheet

    Returns True if the save succeeded, False otherwise (never raises).
    """
    if not ingredients_list:
        if logger:
            logger("[Data Manager] Nothing to save - ingredients list is empty.")

        return False

    session_id = _next_session_id(filepath)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ingredients = load_ingredients(filepath, logger=logger)

    existing_ingredients = {
        str(row.get("ingredient")).strip().lower(): row for row in ingredients
    }

    for ingredient, quantity in ingredients_list.items():
        ingredient = str(ingredient).strip().lower()

        if ingredient in existing_ingredients:
            existing_ingredients[ingredient]["quantity"] = quantity
            existing_ingredients[ingredient]["timestamp"] = timestamp

        else:
            ingredients.append(
                {
                    "session_id": session_id,
                    "timestamp": timestamp,
                    "ingredient": ingredient,
                    "quantity": quantity,
                }
            )

    success = save(filepath, fieldnames, ingredients, mode="w", logger=logger)

    if success and logger:
        logger(
            f"[Data Manager] Saved {len(ingredients_list)} ingredient(s) to '{filepath}' "
            f"(session {session_id})."
        )

    return success


def _next_session_id(filepath):
    """Works out the next session_id to use, based on existing records."""
    records = load_ingredients(filepath)
    ids = []
    for row in records:
        try:
            ids.append(int(row.get("session_id", 0)))

        except (ValueError, TypeError):
            continue

    return max(ids, default=0) + 1


def save_recipe(
    recipe, filepath=DEFAULT_RECIPES_FILEPATH, fieldnames=RECIPE_FIELDNAMES, logger=None
):
    """
    Appends a fully evaluated recipe (from logic_manager) to persistent storage.
    Returns True if save succeeded, False otherwise.
    """
    if not recipe or not isinstance(recipe, dict):
        return False

    formatted_recipe = {
        "recipe": recipe.get("recipe", "Unknown Recipe"),
        "outcome": recipe.get("outcome", "unknown"),
        "score": recipe.get("score", 0.0),
        "reason": recipe.get("reason", ""),
        "ingredients": json.dumps(recipe.get("ingredients", [])),
        "instructions": json.dumps(recipe.get("instructions", [])),
    }

    success = save(filepath, fieldnames, formatted_recipe, mode="a", logger=logger)

    if success and logger:
        logger(f"[Data Manager] Saved recipes to '{filepath}'.")

    return success


# ---------------------------------------------------------------------------
# 3. Filter / query functions
# ---------------------------------------------------------------------------


def filter_by_ingredient(records, ingredient_name):
    """Returns all rows matching a given ingredient name (case-insensitive)."""
    ingredient_name = ingredient_name.strip().lower()

    def matches(record):
        ingredients = record.get("ingredients")

        for name in ingredients:
            if ingredient_name in str(name).strip().lower():
                return True

        return False

    return query(matches, records)


def filter_by_session(records, session_id):
    """Returns all rows belonging to a specific saved session."""
    target = str(session_id).strip()
    return query(lambda row: str(row.get("session_id", "")).strip() == target, records)


def filter_by_success(records):
    """Returns all matching recipe rows with successful evaluation via business rules."""
    return query(lambda record: record.get("outcome") == "accept", records)


def query(filter_fn, records):
    """
    Accepts a filter function and returns all matching records.
    Example: query(lambda r: r["outcome"] == "accept")
    """
    return [record for record in records if filter_fn(record)]
