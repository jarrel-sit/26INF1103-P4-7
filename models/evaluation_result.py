# --- Imports --- #
from dataclasses import dataclass
from rule_result import RuleResult


# -- Classes --- #
@dataclass
class EvaluationResult:
    outcome: str
    score: float
    reason: str
    rule_results: list[RuleResult]
