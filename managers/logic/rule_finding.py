from typing import Optional

from models import RuleResult
from .severity import Severity

# RuleFinding ====

class RuleFinding:
    """What one rule found. Created by a rule, then owned by an Evaluation."""

    def __init__(
        self,
        rule_name: str,
        passed: bool,
        details: dict,
        severity: Severity,
        failure_reason: str,
        label: Optional[str] = None,
    ):
        self.__rule_name = rule_name
        self.__passed = passed
        self.__details = dict(details)
        self.__severity = severity
        self.__failure_reason = failure_reason
        self.__label = label or rule_name

    @property
    def rule_name(self) -> str:
        return self.__rule_name

    @property
    def passed(self) -> bool:
        return self.__passed

    @property
    def details(self) -> dict:
        return dict(self.__details)

    @property
    def severity(self) -> Severity:
        return self.__severity

    @property
    def failure_reason(self) -> str:
        return self.__failure_reason

    def to_rule_result(self) -> RuleResult:
        """Convert to the team's models.RuleResult (details becomes one text line)."""
        text = ", ".join(f"{key}={value}" for key, value in self.__details.items())

        if not self.__passed:
            text = f"{self.__failure_reason} ({text})" if text else self.__failure_reason

        return RuleResult(self.__rule_name, self.__passed, text)

    def to_dict(self) -> dict:
        """Same shape the Phase 1 rule functions returned."""
        return {"rule": self.__label, "passed": self.__passed, **self.__details}