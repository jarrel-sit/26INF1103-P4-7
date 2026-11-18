from typing import Iterable

from .rule_finding import RuleFinding
from .severity import Severity


# Evaluation ====

class Evaluation:
    """The outcome of running every rule against one record.
    Owns its RuleFindings. Does not decide a final outcome - that's the router's job."""

    def __init__(self, recipe: str, results: Iterable[RuleFinding]):
        self.__recipe = recipe
        self.__results = list(results)

    @property
    def recipe(self) -> str:
        return self.__recipe

    @property
    def results(self) -> tuple:
        return tuple(self.__results)

    def failed(self, severity: Severity) -> list:
        """Failed results of the given severity, in rule order."""
        return [
            result
            for result in self.__results
            if not result.passed and result.severity is severity
        ]

    def result_for(self, rule_name: str) -> RuleFinding:
        for result in self.__results:
            if result.rule_name == rule_name:
                return result

        raise KeyError(rule_name)

    def all_passed(self) -> bool:
        return all(result.passed for result in self.__results)

    def to_dict(self) -> dict:
        """Same decision dict shape the Phase 1 evaluate() returned."""
        return {
            "recipe": self.__recipe,
            "rule_results": {
                result.rule_name: result.to_dict() for result in self.__results
            },
        }