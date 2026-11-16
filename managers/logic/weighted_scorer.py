from .i_scorer import IScorer
from .recipe_record import RecipeRecord
from .scoring_weights import ScoringWeights

# WeightedScorer ==== the actual scorer

class WeightedScorer(IScorer):
    """Produces a 0-100 score used to rank candidate recipes. Rewards high AI
    confidence, then having the ingredients on hand, then staying within the
    time budget. Owns its ScoringWeights."""

    def __init__(
        self, confidence: float = 0.5, ingredients: float = 0.35, time: float = 0.15
    ):
        self.__weights = ScoringWeights(confidence, ingredients, time)

    def score(self, record: RecipeRecord) -> float:
        weighted = (
            (record.confidence * self.__weights.confidence)
            + (self.__ingredient_ratio(record) * self.__weights.ingredients)
            + (self.__time_ratio(record) * self.__weights.time)
        )

        return round(weighted * 100, 1)

    def __ingredient_ratio(self, record: RecipeRecord) -> float:
        needed = {i.strip().lower() for i in record.ingredients_used}
        have = {i.strip().lower() for i in record.available_ingredients}

        return len(needed & have) / len(needed) if needed else 1.0

    def __time_ratio(self, record: RecipeRecord) -> float:
        max_time = record.cooking_time_limit
        estimated = record.estimated_cooking_time

        if max_time and estimated > max_time:
            return max(0.0, min(1.0, 1 - (estimated - max_time) / max_time))

        return 1.0