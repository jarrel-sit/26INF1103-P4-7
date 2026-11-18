import math

# ScoringWeights ==== holds how much each factor counts

class ScoringWeights:
    """How much each factor counts towards the score. Must add up to 1."""

    def __init__(
        self, confidence: float = 0.5, ingredients: float = 0.35, time: float = 0.15
    ):
        weights = (confidence, ingredients, time)

        if any(weight < 0 for weight in weights) or not math.isclose(sum(weights), 1.0):
            raise ValueError("Scoring weights must be non-negative and add up to 1.")

        self.__confidence = confidence
        self.__ingredients = ingredients
        self.__time = time

    @property
    def confidence(self) -> float:
        return self.__confidence

    @property
    def ingredients(self) -> float:
        return self.__ingredients

    @property
    def time(self) -> float:
        return self.__time