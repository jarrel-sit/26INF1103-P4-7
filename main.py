# --- Imports --- #
import io_manager, data_manager, ai_manager, logic_manager

# Function Calls from io_manager.py
diet = io_manager.diet()
allergy = io_manager.allergy()
ingredient_input = io_manager.ingredient_input()
pax = io_manager.pax()

def menu():
    # placeholder menu - to be updated
    print('--')

record = {}

while True:

    # menu -> ask for innput -> function -> respective output (recommendation/listing of ingredients) -> data manipulation
    ## a skeleton of flow
    choice = int(menu())

    if choice == 1: ## assuming that its for ingredient input
        record["ingredients"] = io_manager.ingredient_input()


    elif choice == 2: ## assuming input allergy
        record["allergy"] = io_manager.allergy()
        

    elif choice == 3: ## assuming input of pax
        record["pax"] = io_manager.pax()

    elif choice == 4:
        record["diet"] = io_manager.diet()

    else:
        # end condition
        break