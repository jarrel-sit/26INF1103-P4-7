# Exceptions ====

class LogicManagerError(Exception):
    """Base class for every error the Logic Manager raises on purpose."""


class InvalidRecordError(LogicManagerError):
    """Raised when an AI-enriched record is missing a field, or a field has the wrong type or an out-of-range value."""

    def __init__(self, field: str, message: str):
        super().__init__(f"'{field}' {message}")
        self.__field = field

    @property
    def field(self) -> str:
        """Name of the offending field."""
        return self.__field