# --- Imports --- #
from .weighted_scorer import WeightedScorer


# --- Classes --- #
class LogicSettings:
    """Allows for the configuration of logic settings and business logic rules for the application."""

    # Default weights for scoring components
    DEFAULT_CONFIDENCE_WEIGHT = 0.5
    DEFAULT_INGREDIENTS_WEIGHT = 0.35
    DEFAULT_TIME_WEIGHT = 0.15

    def __init__(
        self,
        confidence_weight: float = DEFAULT_CONFIDENCE_WEIGHT,
        ingredients_weight: float = DEFAULT_INGREDIENTS_WEIGHT,
        time_weight: float = DEFAULT_TIME_WEIGHT,
    ):
        # Validate and set the scoring weights
        self.set_weights(confidence_weight, ingredients_weight, time_weight)

    @property
    def weights(self) -> tuple[float, float, float]:
        return (
            self._confidence_weight,
            self._ingredients_weight,
            self._time_weight,
        )

    def set_weights(
        self,
        confidence_weight: float,
        ingredients_weight: float,
        time_weight: float,
    ) -> None:
        """Validates and updates scoring weights (non-negative and summing to 1.0)."""

        raw_weights = (confidence_weight, ingredients_weight, time_weight)
        if any(
            isinstance(w, bool) or not isinstance(w, (int, float)) for w in raw_weights
        ):
            raise ValueError("All scoring weights must be numeric.")
        if any(w < 0.0 for w in raw_weights):
            raise ValueError("Scoring weights cannot be negative.")
        if abs(sum(raw_weights) - 1.0) > 1e-6:
            raise ValueError("Scoring weights must sum to 1.0.")

        self._confidence_weight = float(confidence_weight)
        self._ingredients_weight = float(ingredients_weight)
        self._time_weight = float(time_weight)

    def reset_defaults(self) -> None:
        """Resets scoring weights to their default values."""
        self._confidence_weight = self.DEFAULT_CONFIDENCE_WEIGHT
        self._ingredients_weight = self.DEFAULT_INGREDIENTS_WEIGHT
        self._time_weight = self.DEFAULT_TIME_WEIGHT

    def build_scorer(self) -> WeightedScorer:
        """Creates a WeightedScorer instance using the current weights."""
        return WeightedScorer(
            confidence=self._confidence_weight,
            ingredients=self._ingredients_weight,
            time=self._time_weight,
        )
