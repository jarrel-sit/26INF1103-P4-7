import re


# Quantity ==== #an amount plus a unit, e.g. 200g

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