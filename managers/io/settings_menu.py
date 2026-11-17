from managers.logic.logic_settings import LogicSettings
from .cli_display import CLIDisplay
from .menu import Menu
from .menu_validator import MenuValidator


class SettingsMenu(Menu):
    """Submenu for viewing and configuring LogicManager settings."""

    def __init__(self, validator: MenuValidator, displayer: CLIDisplay) -> None:
        super().__init__(validator=validator, displayer=displayer, choices=5)

    def display_menu_text(self) -> None:
        self._displayer.display_menu("""
================================================
|          Configure Scoring Weights           |
|----------------------------------------------|
|                                              |
|  1. Balanced (0.50, 0.35, 0.15)              |
|  2. Strict AI Confidence (0.70, 0.20, 0.10)  |
|  3. Ingredient-Focused (0.30, 0.55, 0.15)    |
|  4. Custom Weights                           |
|  5. Back to Main Menu                        |
|                                              |
================================================""")

    def configure(self, current_settings: LogicSettings) -> LogicSettings | None:
        """Displays current weights, prompts the user, and returns updated LogicSettings."""
        confidence, ingredients, time = current_settings.weights
        self._displayer.display_logs(
            f"\nCurrent Weights -> Confidence: {confidence:.2f}, Ingredients: {ingredients:.2f}, Time: {time:.2f}"
        )

        choice = int(self.get_choice())
        updated = LogicSettings(*current_settings.weights)

        if choice == 1:
            updated.reset_defaults()
            return updated
        if choice == 2:
            updated.set_weights(0.70, 0.20, 0.10)
            return updated
        if choice == 3:
            updated.set_weights(0.30, 0.55, 0.15)
            return updated
        if choice == 4:
            return self._collect_custom_weights(updated)
        return None

    def _collect_custom_weights(self, settings: LogicSettings) -> LogicSettings | None:
        """Prompts for three numeric weights and validates them via LogicSettings."""
        while True:
            try:
                raw_confidence = input(
                    "Confidence weight (0.0 - 1.0, or 'q' to cancel): "
                ).strip()
                if raw_confidence.lower() == "q":
                    return None
                raw_ingredients = input("Ingredients weight (0.0 - 1.0): ").strip()
                raw_time = input("Cooking time weight (0.0 - 1.0): ").strip()

                settings.set_weights(
                    float(raw_confidence), float(raw_ingredients), float(raw_time)
                )
                return settings
            except ValueError as err:
                self._displayer.display_error(f"Invalid weights: {err}")
