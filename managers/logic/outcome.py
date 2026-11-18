from enum import Enum


# Outcome ==== #Accept, Flag, Reject

class Outcome(Enum):
    """The three outcome paths. Values match the Phase 1 strings, so saved
    CSV rows and io_manager comparisons such as `== "accept"` keep working."""

    ACCEPT = "accept"
    FLAG = "flag"
    REJECT = "reject"