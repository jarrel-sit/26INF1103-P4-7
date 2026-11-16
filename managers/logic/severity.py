from enum import Enum


# Severity ====

class Severity(Enum):
    """What a failed rule means for the final outcome."""

    BLOCKING = "blocking"  # a failure here REJECTS the recipe (safety / trust)
    ADVISORY = "advisory"  # a failure here FLAGS the recipe (user should check)