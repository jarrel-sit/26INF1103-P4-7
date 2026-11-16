# --- Imports --- #
from abc import ABC, abstractmethod


# --- Classes --- #
class Repository(ABC):
    """Abstract base class for a repository that manages data storage and retrieval."""

    @abstractmethod
    def save(self, data):
        """Save new data to the repository."""
        pass

    @abstractmethod
    def load(self):
        """Load all records from the repository."""
        pass

    @abstractmethod
    def query(self, filter_fn):
        """
        Accepts a filter function and returns all matching records.
        Example: query(lambda r: r["outcome"] == "accept")
        """
        pass
