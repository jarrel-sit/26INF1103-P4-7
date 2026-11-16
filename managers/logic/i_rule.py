from abc import ABC, abstractmethod
from .recipe_record import RecipeRecord
from .rule_finding import RuleFinding
from .severity import Severity

# RecordValidator ==== Interface (contract) every business rule must honor

class IRule(ABC):
    """Interface (contract) every business rule must honour."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique name of the rule."""

    @property
    @abstractmethod
    def severity(self) -> Severity:
        """BLOCKING rules reject on failure, ADVISORY rules flag."""

    @abstractmethod
    def evaluate(self, record: RecipeRecord) -> RuleFinding:
        """Run the rule. Must return a RuleFinding for any valid RecipeRecord."""