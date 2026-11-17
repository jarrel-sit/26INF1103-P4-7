# --- Imports --- #
from dataclasses import dataclass, asdict
from .instruction import Instruction


# --- Classes --- #
@dataclass
class GeneratedRecipe:
    recipe: str
    ingredients: dict[str, str]
    instructions: dict[str, Instruction]
    confidence: float
    dietary_preferences: list[str]
    equipment: list[str]
    hazardous_ingredients: dict[str, str]
    insufficient_ingredients: bool

    def recipe_to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "GeneratedRecipe":
        """Shapes a validated dictionary into a GeneratedRecipe instance."""
        instructions_dict = {
            str(key): Instruction(
                step=value.get("step", ""),
                time_taken=value.get("time_taken", ""),
            )
            for key, value in data.get("instructions", {}).items()
        }
        return cls(
            recipe=data["recipe"],
            ingredients=data["ingredients"],
            instructions=instructions_dict,
            confidence=data["confidence"],
            dietary_preferences=data["dietary_preferences"],
            hazardous_ingredients=data["hazardous_ingredients"],
            equipment=data["equipment"],
            insufficient_ingredients=data["insufficient_ingredients"],
        )
