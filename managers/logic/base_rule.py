from abc import abstractmethod
from typing import Optional
from .i_rule import IRule
from .recipe_record import RecipeRecord
from .rule_finding import RuleFinding
from .severity import Severity

# BaseRule ==== Abstract class holding the behaviour every rule shares (name, severity, and building the RuleFinding)

class BaseRule(IRule):
    """Abstract class holding the behaviour every rule shares (name, severity,
    and building the RuleFinding). Subclasses only supply the rule itself."""

    def __init__(self, name: str, severity: Severity, result_label: Optional[str] = None):
        self._name = name
        self._severity = severity
        self._result_label = result_label or name

    @property
    def name(self) -> str:
        return self._name

    @property
    def severity(self) -> Severity:
        return self._severity

    def evaluate(self, record: RecipeRecord) -> RuleFinding:
        # Template method: shared steps here, the rule-specific part in _check()
        details = dict(self._check(record))
        passed = bool(details.pop("passed"))

        return RuleFinding(
            self._name,
            passed,
            details,
            self._severity,
            self.failure_reason(),
            self._result_label,
        )

    @abstractmethod
    def _check(self, record: RecipeRecord) -> dict:
        """Return {"passed": bool, ...any details to report}."""

    @abstractmethod
    def failure_reason(self) -> str:
        """Short text used in the routing reason when this rule fails."""