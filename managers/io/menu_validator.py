# --- Classes --- #
class MenuValidator:
    def validate(choice: str, option_count: int):
        if choice.isdecimal() and int(choice) > 0 and int(choice) <= option_count:
            return True
