# --- Imports --- #
from dataclasses import dataclass


# --- Classes --- #
@dataclass
class ValidationResult:
    is_valid: bool
    errors: list[str]
