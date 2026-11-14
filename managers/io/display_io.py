#Imports
from recipe_io import RecipeRequestCollector, RecipeRequestValidator

class Display:
     def display_logs(log: str):
          """Outputs verbose log messages."""
          print(f"{log}")

    #Displays error messages when recieiving input from user
     def display_error(self, msg):
          print(f"[ERROR]: {msg}")

    #Displays list of ingredients
     def display_ingredients(self):
          record = RecipeRequestCollector(RecipeRequestValidator).collect_input()
          allingredients = record[2]
          print("--- Current Available Ingredients ---")
          for i in allingredients:
               for key,value in i.items():
                    print(f"- {key}: {value}")

     #Displays recipe
     def display_result(self, result):
          print("\n" + "=" * 55)
          print(f"RECIPE: {result.get('recipe', 'N/A')}")
          print(
               f"OUTCOME: {result.get('outcome', 'N/A').upper()} (Score: {result.get('score', 0)})"
              )
          print(f"REASON: {result.get('reason', '')}")
     
          if result.get("outcome") == "reject":
               print("!!! USE AT YOUR OWN RISK !!!")
     
          print("=" * 55)
     
          print("\n--- Ingredients Used ---")
          ingredients = result.get("ingredients", {})
     
          for ingredient, quantity in ingredients.items():
               print(f" - {str(ingredient).capitalize()}: {quantity}")
     
          print("\n--- Instructions ---")
     
          instructions = result.get("instructions")
     
          # Sort keys to ensure that the steps are in numerical order
          for step_num, step_data in sorted(instructions.items(), key=lambda x: str(x[0])):
               step = step_data.get("step", "")
               time_taken = step_data.get("time_taken")
               print(f" {step_num}. {step} [Time: {time_taken}]")
     
          print()
          print("=" * 55)

    #Displays menu formatting
     def display_menu(self,message):
          print(message)