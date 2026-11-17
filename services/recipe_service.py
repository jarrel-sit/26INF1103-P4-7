# --- Imports --- #
from managers.ai import GeminiAIManager
from managers.logic import LogicManager, RoutingDecision, InvalidRecordError
from managers.data import RecipeRepository
from models import RecipeRequest


# --- Classes --- #
class RecipeService:
    """Application service coordinating recipe generation, evaluation, and storage."""

    def __init__(
        self,
        generator: GeminiAIManager,
        evaluator: LogicManager,
        repository: RecipeRepository,
    ) -> None:
        self._generator = generator
        self._evaluator = evaluator
        self._repository = repository

    def generate_recipe(self, request: RecipeRequest) -> RoutingDecision | str:
        ai_result = self._generator.process(request)

        if not ai_result.success:
            return f"AI generation failed: {ai_result.error_message}"

        # Ensure evaluation uses the user's requested ingredients, not AI-hallucinated extras
        try:
            evaluation = self._evaluator.process(request, ai_result.recipe)

        except InvalidRecordError as e:
            return f"Recipe evaluation failed: {str(e)}"

        self._repository.save(evaluation)
        return evaluation

    def get_all_recipes(self) -> list[RoutingDecision]:
        return self._repository.find_all()

    def get_successful_recipes(self) -> list[RoutingDecision]:
        return self._repository.find_successful()

    def find_by_ingredient(self, name: str) -> list[RoutingDecision]:
        return self._repository.find_by_ingredient(name)
