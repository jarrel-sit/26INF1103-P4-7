# === Imports ===
import math
import re
from abc import ABC, abstractmethod
from enum import Enum
from typing import Iterable


# ===========================================================================
# === Exceptions ============================================================
# ===========================================================================
class LogicManagerError(Exception):
    """Base class for every error the Logic Manager raises on purpose."""


class InvalidRecordError(LogicManagerError):
    """Raised when an AI-enriched record is missing a field, or a field has
    the wrong type or an out-of-range value."""

    def __init__(self, field: str, message: str):
        super().__init__(f"'{field}' {message}")
        self.__field = field

    @property
    def field(self) -> str:
        """Name of the offending field."""
        return self.__field


# ===========================================================================
# === Enumerations ==========================================================
# ===========================================================================
class Severity(Enum):
    """What a failed rule means for the final outcome."""

    BLOCKING = "blocking"  # a failure here REJECTS the recipe (safety / trust)
    ADVISORY = "advisory"  # a failure here FLAGS the recipe (user should check)


class Outcome(Enum):
    """The three outcome paths. Values match the Phase 1 strings, so saved
    CSV rows and io_manager comparisons such as `== "accept"` keep working."""

    ACCEPT = "accept"
    FLAG = "flag"
    REJECT = "reject"


# ===========================================================================
# === Value object: Quantity ================================================
# ===========================================================================
class Quantity:
    """An amount plus a unit, e.g. 200 g. Replaces Phase 1 parse_quantity()."""

    _PATTERN = re.compile(r"^([\d.]+)\s*([a-zA-Z]*)$")

    def __init__(self, amount: float = 0.0, unit: str = ""):
        self.__amount = float(amount)
        self.__unit = unit

    @staticmethod
    def parse(raw) -> "Quantity":
        """Builds a Quantity from raw AI/user text such as '200g' or '2'.
        Anything unreadable becomes 0 with no unit - never raises."""

        # In case in the future quantity is returned as a numerical value
        if not isinstance(raw, str):
            try:
                return Quantity(float(raw))
            except (ValueError, TypeError, OverflowError):
                return Quantity()

        match = Quantity._PATTERN.match(raw.strip())
        if match:
            try:
                return Quantity(float(match.group(1)), match.group(2).lower())
            except ValueError:
                return Quantity()

        return Quantity()

    @property
    def amount(self) -> float:
        return self.__amount

    @property
    def unit(self) -> str:
        return self.__unit

    def is_comparable_to(self, other: "Quantity") -> bool:
        """Same unit, or at least one side has no unit stated."""
        return self.__unit == other.unit or not self.__unit or not other.unit

    def covers(self, needed: "Quantity") -> bool:
        """True if this amount is enough to supply `needed`."""
        return self.__amount >= needed.amount

    def __eq__(self, other):
        if not isinstance(other, Quantity):
            return NotImplemented
        return (self.__amount, self.__unit) == (other.amount, other.unit)

    def __hash__(self):
        return hash((self.__amount, self.__unit))

    def __repr__(self):
        return f"Quantity({self.__amount}, {self.__unit!r})"


# ===========================================================================
# === Typed record ==========================================================
# ===========================================================================
class RecipeRecord:
    """A validated, read-only view of one AI-enriched recipe record.
    Owns the Quantity objects parsed from its ingredient amounts."""

    def __init__(
        self,
        recipe: str,
        ingredients: dict,
        confidence: float,
        available_ingredients: dict = None,
        ingredients_used: list = None,
        allergies: list = None,
        dietary_preferences: list = None,
        max_cooking_time=None,
        estimated_cooking_time=0,
        instructions: dict = None,
    ):
        self.__recipe = recipe
        self.__ingredients = dict(ingredients)
        self.__available_ingredients = dict(available_ingredients or {})
        self.__ingredients_used = list(ingredients_used or [])
        self.__allergies = list(allergies or [])
        self.__dietary_preferences = list(dietary_preferences or [])
        self.__max_cooking_time = max_cooking_time
        self.__estimated_cooking_time = estimated_cooking_time
        self.__confidence = confidence
        self.__instructions = dict(instructions or {})

        # Composition: the record creates (and owns) its Quantity objects
        self.__required_quantities = {
            name: Quantity.parse(raw) for name, raw in self.__ingredients.items()
        }
        self.__available_quantities = {
            name: Quantity.parse(raw)
            for name, raw in self.__available_ingredients.items()
        }

    # Read-only access: callers get copies, so nobody can mutate the record
    @property
    def recipe(self) -> str:
        return self.__recipe

    @property
    def ingredients(self) -> dict:
        return dict(self.__ingredients)

    @property
    def available_ingredients(self) -> dict:
        return dict(self.__available_ingredients)

    @property
    def ingredients_used(self) -> list:
        return list(self.__ingredients_used)

    @property
    def allergies(self) -> list:
        return list(self.__allergies)

    @property
    def dietary_preferences(self) -> list:
        return list(self.__dietary_preferences)

    @property
    def confidence(self) -> float:
        return self.__confidence

    @property
    def cooking_time_limit(self):
        """The user's max cooking time in minutes, or None if there isn't one."""
        return self.__max_cooking_time

    @property
    def estimated_cooking_time(self):
        return self.__estimated_cooking_time

    @property
    def instructions(self) -> dict:
        return dict(self.__instructions)

    @property
    def required_quantities(self) -> dict:
        """Ingredient name -> Quantity the recipe calls for."""
        return dict(self.__required_quantities)

    @property
    def available_quantities(self) -> dict:
        """Ingredient name -> Quantity the user has."""
        return dict(self.__available_quantities)


