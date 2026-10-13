# --- Imports --- #
import io_manager, data_manager, ai_manager, logic_manager


# --- Functions --- #
def recipe_pipeline(record):
    if not record:
        print("Please key in some ingredients. Ingredients information is missing.")
        return

    user_input = io_manager.collect_input(record)  # add respective module

    success, response = ai_manager.process(user_input)  # add respective module

    if not success:
        io_manager.display_error(response)  # add respective module
        return

    combined_output = {**user_input, **response}
    evaluated_record = logic_manager.route(combined_output)

    # Store for memory and access previous accepted recipes
    data_manager.save_recipe(evaluated_record)

    io_manager.display_result(evaluated_record)


def add_ingredients():
    ingredients = io_manager.ingredient_input(
        success_message="\nUpdated the ingredients list!",
        failure_message="No new ingredients were added. ",
    )

    if ingredients:
        success = data_manager.save_ingredients(ingredients)

        if success:
            io_manager.display_logs(
                "Successfully saved ingredients to persistent storage."
            )
        else:
            io_manager.display_error("Failed to save ingredients to disk.")

    return data_manager.load_ingredients()


# --- Main Program --- #
def main():
    # --- Variables & Constants --- #
    record = data_manager.load_ingredients()
    recipes = data_manager.load_recipes()

    # --- Program Code --- #
    while True:

        # menu -> ask for innput -> function -> respective output (recommendation/listing of ingredients) -> data manipulation
        ## a skeleton of flow
        choice = io_manager.menu()

        # Adding of new ingredients
        if choice == 1:
            record = add_ingredients()

        # List all ingredients
        elif choice == 2:
            io_manager.display_ingredients(record)

        # AI Recipe recommendation
        elif choice == 3:
            recipe_pipeline(record)

        # View past (successful?) recommendations
        elif choice == 4:
            while True:
                sub_choice = io_manager.past_recipes_menu()

                if sub_choice == 1:
                    io_manager.display_list(recipes)

                elif sub_choice == 2:
                    successful_recipes = data_manager.filter_by_success(recipes)
                    io_manager.display_list(successful_recipes)

                elif sub_choice == 3:
                    ingredient_query = io_manager.prompt_ingredient_query()
                    if ingredient_query:
                        filtered_recipes = data_manager.filter_by_ingredient(
                            recipes, ingredient_query
                        )

                        io_manager.display_list(filtered_recipes)

                    else:
                        io_manager.display_error("Ingredient query cannot be empty.")

                elif sub_choice == 4:
                    break  # Exit back to main menu

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
