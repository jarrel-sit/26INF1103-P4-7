# --- Imports --- #
import os
from dotenv import load_dotenv
from services import RecipeService

from managers.ai import GeminiAIManager, GeminiClient, RecipeValidator
from managers.logic import LogicManager, RoutingDecision

from managers.data import (
    RecipeRepository,
    IngredientRepository,
    CsvRecipeRepository,
    CsvIngredientRepository,
)

from managers.io import (
    MenuValidator,
    MainMenu,
    SubMenu,
    RecipeRequestCollector,
    RecipeRequestValidator,
    CLIDisplay,
)


# --- Classes --- #
class Application:
    """Top-level application controller managing UI workflows and dependencies."""

    def __init__(
        self,
        ingredients: IngredientRepository,
        recipe_repository: RecipeRepository,
        api_key: str,
    ) -> None:
        # Association: Repositories exist independently of Application lifecycle
        self._ingredients: IngredientRepository = ingredients

        # Composition: Application owns and manages UI and service lifecycles
        self.__display = CLIDisplay()
        self.__menu_validator = MenuValidator()
        self.__recipe_validator = RecipeRequestValidator()

        self._menu: MainMenu = MainMenu(self.__menu_validator, self.__display)
        self._recipe_menu: SubMenu = SubMenu(self.__menu_validator, self.__display)
        self._collector: RecipeRequestCollector = RecipeRequestCollector(
            self.__recipe_validator, self.__display
        )

        generator = GeminiAIManager(
            client=GeminiClient(api_key=api_key),
            validator=RecipeValidator(),
            max_retries=3,
        )
        evaluator = LogicManager()

        self._service: RecipeService = RecipeService(
            generator=generator,
            evaluator=evaluator,
            repository=recipe_repository,
        )

    def run(self) -> None:
        """Executes the main interactive CLI loop."""
        while True:
            self._menu.display_menu_text()
            choice = int(self._menu.get_choice())

            if choice == 1:
                self._handle_add_ingredients()
            elif choice == 2:
                self._handle_list_ingredients()
            elif choice == 3:
                self._handle_recommend_recipe()
            elif choice == 4:
                self._handle_view_past_recipes()
            # elif choice == 5:
            #     self._handle_delete_ingredient()
            elif choice == 5:
                self.__display.display_logs("Exiting application. Goodbye!")
                break

    def _handle_add_ingredients(self) -> None:
        updated = self._collector.collect_ingredients()

        if updated == {}:
            self.__display.display_logs("No ingredients were added.")

        elif self._ingredients.save(updated):
            self.__display.display_logs("Ingredients saved successfully.")
        else:
            self.__display.display_error("Failed to save ingredients.")

    def _handle_list_ingredients(self) -> None:
        available = self._ingredients.find_all()
        if not available:
            self.__display.display_logs("Your fridge is currently empty.")
            return
        self.__display.display_ingredients(available)

    def _handle_recommend_recipe(self) -> None:
        available = self._ingredients.find_all()
        if not available:
            self.__display.display_error(
                "No ingredients found. Add ingredients before requesting a recipe."
            )
            return

        request = self._collector.collect_input(available)
        if request is None:
            self.__display.display_logs("Recipe request cancelled.")
            return

        self.__display.display_logs("Generating and evaluating recipe...")
        result = self._service.generate_recipe(request)

        if isinstance(result, str):
            self.__display.display_error(result)
        else:
            self.__display.display_result(result)

    def _handle_view_past_recipes(self) -> None:
        """Handles the past recipes submenu loop."""
        while True:
            self._recipe_menu.display_menu_text()
            sub_choice = int(self._recipe_menu.get_choice())

            if sub_choice == 1:
                recipes = self._service.get_all_recipes()
                if not recipes:
                    self.__display.display_logs("No past recipes found.")

                else:
                    self.__display.display_recipe_list(recipes)
                    self._view_selected_recipe_details(recipes)

            elif sub_choice == 2:
                recipes = self._service.get_successful_recipes()

                if not recipes:
                    self.__display.display_logs("No successful recipes found.")

                else:
                    self.__display.display_recipe_list(recipes)
                    self._view_selected_recipe_details(recipes)

            elif sub_choice == 3:
                past_recipes = self._service.get_all_recipes()

                used_ingredients = sorted(
                    {
                        ingredient.strip().lower()
                        for record in past_recipes
                        for ingredient in record.ingredients.keys()
                    }
                )

                selected = self._recipe_menu.select_from_used(used_ingredients)

                if selected:
                    filtered = self._service.find_by_ingredient(selected)

                    if filtered:
                        self.__display.display_recipe_list(filtered)
                        self._view_selected_recipe_details(filtered)

            elif sub_choice == 4:
                break

    def _view_selected_recipe_details(self, recipes: list[RoutingDecision]) -> None:
        """Prompts the user to select a recipe from a list and displays its details."""
        if not recipes:
            self.__display.display_logs("No recipes available to view.")
            return

        selected_recipe = self._recipe_menu.select_recipe(recipes)

        if selected_recipe:
            self.__display.display_result(selected_recipe)

    def _handle_delete_ingredient(self) -> None:
        available = self._ingredients.find_all()
        if not available:
            self.__display.display_logs("No ingredients available to delete.")
            return

        self.__display.display_ingredients(available)
        # name = self._collector.collect_ingredient_to_delete()
        # if not name:
        #     return

        # if self._ingredients.delete(name):
        #     self.__display.display_logs(f"Removed '{name}' from your ingredients.")
        # else:
        #     self.__display.display_error(f"Ingredient '{name}' not found.")


if __name__ == "__main__":
    load_dotenv(dotenv_path="./.env")
    api_key = os.getenv("GENAI_API_KEY", "")

    ingredient_repo = CsvIngredientRepository(
        "ingredients_data.csv",
        fieldnames=["session_id", "timestamp", "ingredient", "quantity"],
    )
    recipe_repo = CsvRecipeRepository(
        "recipe_data.csv",
        fieldnames=[
            "recipe",
            "outcome",
            "score",
            "reason",
            "ingredients",
            "instructions",
        ],
    )

    app = Application(
        ingredients=ingredient_repo,
        recipe_repository=recipe_repo,
        api_key=api_key,
    )
    app.run()
