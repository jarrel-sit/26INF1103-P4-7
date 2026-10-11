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

import csv
import os
from datetime import datetime

# Default location of the spreadsheet (CSV) that acts as persistent storage.
DEFAULT_FILEPATH = "ingredients_data.csv"

# Column headers for the CSV spreadsheet.
FIELDNAMES = ["session_id", "timestamp", "ingredient", "quantity"]


# ---------------------------------------------------------------------------
# 2. Load all records on startup (+ 4. handle missing/corrupt files)
# ---------------------------------------------------------------------------

def load_records(filepath=DEFAULT_FILEPATH):
    """
    Loads all saved records from the CSV spreadsheet.

    Returns a list of dictionaries (one per ingredient row). If the file
    does not exist yet, it is created with just a header row and an empty
    list is returned. If the file exists but is corrupt/unreadable/has a
    bad header, the problem is reported and an empty list is returned
    instead of crashing the program.
    """
    if not os.path.exists(filepath):
        print(f"[Data Manager] No existing data file found at '{filepath}'. Creating a new one.")
        _create_empty_file(filepath)
        return []

    records = []
    try:
        with open(filepath, mode="r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            if reader.fieldnames is None or set(reader.fieldnames) != set(FIELDNAMES):
                print(f"[Data Manager] Warning: '{filepath}' has an unexpected or missing "
                      f"header and appears corrupted. Starting with an empty record set.")
                return []

            for row_number, row in enumerate(reader, start=2):  # row 1 is the header
                try:
                    if not row.get("ingredient") or not row.get("quantity"):
                        raise ValueError("missing ingredient/quantity")
                    records.append(row)
                except (ValueError, KeyError) as row_error:
                    print(f"[Data Manager] Warning: skipping corrupt row {row_number} "
                          f"in '{filepath}' ({row_error}).")
                    continue

    except (csv.Error, OSError, UnicodeDecodeError) as file_error:
        print(f"[Data Manager] Warning: could not read '{filepath}' ({file_error}). "
              f"Treating it as empty/corrupt and starting fresh.")
        return []

    print(f"[Data Manager] Loaded {len(records)} ingredient record(s) from '{filepath}'.")
    return records


def _create_empty_file(filepath):
    """Creates a new CSV spreadsheet with just the header row."""
    try:
        with open(filepath, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
            writer.writeheader()
    except OSError as error:
        print(f"[Data Manager] Error: could not create data file '{filepath}' ({error}).")


# ---------------------------------------------------------------------------
# 1. Save processed records to CSV
# ---------------------------------------------------------------------------

def save_ingredients(ingredients_list, filepath=DEFAULT_FILEPATH):
    """
    Saves a processed set of ingredients (as produced by
    io_manager.ingredient_input()) into the CSV spreadsheet, one row per
    ingredient, tagged with a shared session_id and timestamp.

    ingredients_list: dict like {"sugar": "100g", "flour": "200g"}
    filepath: path to the CSV spreadsheet

    Returns True if the save succeeded, False otherwise (never raises).
    """
    if not ingredients_list:
        print("[Data Manager] Nothing to save - ingredients list is empty.")
        return False

    if not os.path.exists(filepath):
        _create_empty_file(filepath)

    session_id = _next_session_id(filepath)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        with open(filepath, mode="a", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
            for name, quantity in ingredients_list.items():
                writer.writerow({
                    "session_id": session_id,
                    "timestamp": timestamp,
                    "ingredient": name,
                    "quantity": quantity,
                })
    except OSError as error:
        print(f"[Data Manager] Error: could not save to '{filepath}' ({error}).")
        return False

    print(f"[Data Manager] Saved {len(ingredients_list)} ingredient(s) to '{filepath}' "
          f"(session {session_id}).")
    return True


def _next_session_id(filepath):
    """Works out the next session_id to use, based on existing records."""
    records = load_records(filepath)
    ids = []
    for row in records:
        try:
            ids.append(int(row.get("session_id", 0)))
        except (ValueError, TypeError):
            continue
    return max(ids, default=0) + 1


# ---------------------------------------------------------------------------
# 3. Filter / query functions
# ---------------------------------------------------------------------------

def filter_by_ingredient(records, ingredient_name):
    """Returns all rows matching a given ingredient name (case-insensitive)."""
    ingredient_name = ingredient_name.strip().lower()
    return [row for row in records if row.get("ingredient", "").lower() == ingredient_name]


def filter_by_session(records, session_id):
    """Returns all rows belonging to a specific saved session."""
    return [row for row in records if str(row.get("session_id")) == str(session_id)]


def get_unique_ingredients(records):
    """Returns a sorted list of every distinct ingredient ever saved."""
    return sorted({row.get("ingredient", "") for row in records if row.get("ingredient")})


# ---------------------------------------------------------------------------
# Demo / integration with io_manager
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    from io_manager import ingredient_input

    # 2. Load whatever memory already exists from previous runs.
    existing_records = load_records()

    # Collect this session's ingredients via io_manager.
    user_ingredients = ingredient_input()

    # 1. Save this session's processed ingredients to the spreadsheet.
    save_ingredients(user_ingredients)

    # 3. Demonstrate a query: show every past session that used "sugar".
    all_records = load_records()
    sugar_rows = filter_by_ingredient(all_records, "sugar")
    if sugar_rows:
        print(f"\n[Data Manager] Found {len(sugar_rows)} past record(s) using 'sugar':")
        for row in sugar_rows:
            print(f"  - Session {row['session_id']} ({row['timestamp']}): {row['quantity']}")