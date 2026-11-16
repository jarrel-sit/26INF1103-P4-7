from typing import Iterable
from .evaluation import Evaluation
from .i_rule import IRule
from .recipe_record import RecipeRecord


# RuleEvaluator ==== Runs a set of rules against a record

class RuleEvaluator:
    """Runs a set of rules against a record. Holds the rules it is given
    (aggregation: rules can exist and be reused outside this evaluator).
    Treats every rule as an IRule - no type-specific branching."""

    def __init__(self, rules: Iterable[IRule]):
        self.__rules: list[IRule] = []

        for rule in rules:
            self.add_rule(rule)

        if not self.__rules:
            raise ValueError("RuleEvaluator needs at least one rule.")

    def add_rule(self, rule: IRule) -> None:
        if any(existing.name == rule.name for existing in self.__rules):
            raise ValueError(f"A rule named '{rule.name}' is already registered.")

        self.__rules.append(rule)

    def evaluate(self, record: RecipeRecord) -> Evaluation:
        return Evaluation(record.recipe, [rule.evaluate(record) for rule in self.__rules])