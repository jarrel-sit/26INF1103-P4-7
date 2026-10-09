# --- Imports --- #
import io_manager, data_manager, ai_manager, logic_manager

# Function Calls from io_manager.py
# diet = io_manager.diet()
# allergy = io_manager.allergy()
# ingredient_input = io_manager.ingredient_input()
# pax = io_manager.pax()
# checkfield = io_manager.checkfield()

def menu():
    # placeholder menu - to be updated
    return(input('1. Input Ingredients\n2. Generate Recipe\n3. Exit\n'))

    

while True:
    record = {}
    # menu -> ask for innput -> function -> respective output (recommendation/listing of ingredients) -> data manipulation
    ## a skeleton of flow
    choice = int(menu())

    if choice == 1: ## assuming that its for ingredient input
        record["ingredients"] = io_manager.ingredient_input()


    elif choice == 2: ## assuming diet and input allergy
        if not record.get("ingredients"):
            print("Please key in some ingredients. Ingredients information is missing.")
            continue
        record["diet"] = io_manager.diet()
        record["allergy"] = io_manager.allergy()
        #Call API here
    elif choice == 3: ## Exit
        break


    
    

    else:
        # end condition
        break

