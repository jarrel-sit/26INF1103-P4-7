# --- Imports --- #
from dataclasses import dataclass


# --- Classes --- #
@dataclass
class Instruction:
    step: str
    time_taken: str
