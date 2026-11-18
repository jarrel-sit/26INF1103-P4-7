# --- Classes --- #
class MenuValidator:
    """Validates user input for menu selections."""
    def validate(self, choice: str, option_count: int) -> bool:
        if choice.isdecimal() and int(choice) > 0 and int(choice) <= option_count:
            return True

        else:
            return False
