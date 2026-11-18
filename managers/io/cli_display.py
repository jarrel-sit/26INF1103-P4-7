# --- Imports --- #
from .display import Display
from managers.logic import RoutingDecision


# --- Classes --- #
class CLIDisplay(Display):
    """Concrete implementation of the Display abstract base class for command-line interface (CLI) output."""

    def display_logs(self, log: str) -> None:
        """Outputs verbose log messages."""
        print(f"{log}")

    def display_error(self, msg: str) -> None:
        """Outputs error messages."""
        print(f"[ERROR]: {msg}")

    # Displays list of ingredients
    def display_ingredients(self, ingredients: dict) -> None:
        """Displays the current list of available ingredients."""
        if not ingredients:
            print("No ingredients have been added yet.")
            return

        print("--- Current Available Ingredients ---")
        for key, value in ingredients.items():
            print(f"- {key}: {value}")

    # Displays recipe
    def display_result(self, result: RoutingDecision) -> None:
        """Displays the details of a generated recipe, including its outcome, score, reason, ingredients, and instructions."""
        data = (
            result.to_dict()
        )  # Convert RoutingDecision to a dictionary for easier access

        recipe = data.get("recipe", "N/A")
        outcome = data.get("outcome", "N/A")
        score = data.get("score", 0)
        reason = data.get("reason", "")
        ingredients = data.get("ingredients", {})
        instructions = data.get("instructions", {})

        print("\n" + "=" * 55)
        print(f"RECIPE: {recipe}")
        print(f"OUTCOME: {outcome} (Score: {score})")
        print(f"REASON: {reason}")

        if outcome == "reject":
            print("!!! USE AT YOUR OWN RISK !!!")

        print("=" * 55)

        print("\n--- Ingredients Used ---")

        for ingredient, quantity in ingredients.items():
            print(f" - {str(ingredient).capitalize()}: {quantity}")

        print("\n--- Instructions ---")

        # Sort keys to ensure that the steps are in numerical order
        for step_num, step_data in sorted(
            instructions.items(), key=lambda x: str(x[0])
        ):
            step = step_data.get("step", "")
            time_taken = step_data.get("time_taken")
            print(f" {step_num}. {step} [Time: {time_taken}]")

        print()
        print("=" * 55)

    # Displays menu formatting
    def display_menu(self, message: str) -> None:
        """Displays a formatted menu message."""
        print(message)

    def display_recipe_list(self, recipes: list[RoutingDecision]) -> None:
        """Displays a list of past recipes with their outcomes and scores."""
        if not recipes:
            print("No recipes found.")
            return

        print("\n--- Past Recipes ---")
        for idx, recipe in enumerate(recipes, start=1):
            recipe_data = (
                recipe.to_dict()
            )  # Convert RoutingDecision to a dictionary for easier access
            print(
                f"{idx}. {recipe_data.get('recipe', 'N/A')} - Outcome: {recipe_data.get('outcome', 'N/A').upper()} (Score: {recipe_data.get('score', 0)})"
            )

    def display_used_ingredients(self, used_ingredients: list[str]) -> None:
        """Displays a list of used ingredients for filtering past recipes."""
        print("\nFilter Past Recipes by Ingredient:")
        for idx, name in enumerate(used_ingredients, start=1):
            print(f"  {idx}. {name}")
        print(f"  {idx+1}. Cancel")
