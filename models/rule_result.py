# --- Imports --- #
from dataclasses import dataclass


# --- Classes --- #
@dataclass
class RuleResult:
    rule_name: str
    passed: bool
    details: str
