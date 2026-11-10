# --- Imports --- #
from models import GeneratedRecipe, Instruction, ValidationResult


# --- Classes --- #
class RecipeValidator:
    def validate(self, response: GeneratedRecipe) -> ValidationResult:
        errors: list[str] = []

        if not isinstance(response.recipe, str) or not response.recipe.strip():
            errors.append("Recipe name is missing or not a non-empty string.")

        if not isinstance(response.ingredients, dict):
            errors.append(
                "Ingredients value is missing or not of the expected type (dict)."
            )

        if not isinstance(response.instructions, dict):
            errors.append(
                "Instructions value is missing or not of the expected type (dict)."
            )
        else:
            for step_key, instruction_obj in response.instructions.items():
                if not isinstance(step_key, str) or not step_key.isdigit():
                    errors.append(f"Step '{step_key}' key is not a numeric string.")

                if not isinstance(instruction_obj, Instruction):
                    errors.append(
                        f"Value of step '{step_key}' is not an Instruction object."
                    )
                else:
                    if (
                        not isinstance(instruction_obj.step, str)
                        or not instruction_obj.step.strip()
                    ):
                        errors.append(
                            f"Field 'step' in step '{step_key}' must be a non-empty string."
                        )

                    if (
                        not isinstance(instruction_obj.time_taken, str)
                        or not instruction_obj.time_taken.strip()
                    ):
                        errors.append(
                            f"Field 'time_taken' in step '{step_key}' must be a non-empty string."
                        )

        if (
            response.confidence is None
            or not isinstance(response.confidence, (int, float))
            or response.confidence < 0
            or response.confidence > 1
        ):
            errors.append("Confidence value must be a number between 0 and 1.")

        if not isinstance(response.equipment, list):
            errors.append(
                "Equipment value is missing or not of the expected type (list)."
            )

        if not isinstance(response.insufficient_ingredients, bool):
            errors.append("Insufficient Ingredients value must be a boolean.")

        return ValidationResult(is_valid=len(errors) == 0, errors=errors)
