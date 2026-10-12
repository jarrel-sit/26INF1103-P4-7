# --- Imports --- #
import io_manager, data_manager, ai_manager, logic_manager

# --- Variables & Constants --- #
record = {}  # to be loaded

# --- Functions --- #
def recipe_pipeline(record):
    if not record.get("ingredients"):
        print("Please key in some ingredients. Ingredients information is missing.")
        return


    user_input = collect_input(record)  # add respective module


    input_payload = {
        **user_input,
        "available_ingredients": list(
  record["ingredients"].keys()
        ),  # Needed by logic_manager
    }


    success, response = ai_manager.process(input_payload)  # add respective module


    if not success:
        io_manager.display_error(response)  # add respective module
        return


    combined_output = {**user_input, **response}
    evaluated_record = logic_manager.route(combined_output)


    # Store for memory and access previous accepted recipes
    data_manager.save(evaluated_record) 


# --- Main Program --- #
def main():
    while True:

        # menu -> ask for innput -> function -> respective output (recommendation/listing of ingredients) -> data manipulation
        ## a skeleton of flow
        choice = io_manager.menu()

        # Adding of new ingredients
        if choice == 1:
            record["ingredients"] = io_manager.ingredient_input(
                success_message="Updated the ingredients list!",
                failure_message="No new ingredients were added. ",
            )

        # List all ingredients
        elif choice == 2:
            io_manager.display_ingredients(record)

        # AI Recipe recommendation
        elif choice == 3:  ## assuming diet and input allergy
            if not record.get("ingredients"):
                print(
                    "Please key in some ingredients. Ingredients information is missing."
                )
                continue
            record["diet"] = io_manager.diet()
            record["allergy"] = io_manager.allergy()
            recipe_pipeline(record)

        # View past (successful?) recommendations
        elif choice == 4:
            past_recipes = data_manager.load()
            io_manager.display_list(past_recipes)


        # Exit program
        else:
            break


if __name__ == "__main__":
    main()
# Function Calls from io_manager.py
# diet = io_manager.diet()
# allergy = io_manager.allergy()
# ingredient_input = io_manager.ingredient_input()
# pax = io_manager.pax()
# checkfield = io_manager.checkfield()
