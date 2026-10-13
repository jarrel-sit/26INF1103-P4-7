# --- Imports --- #
import io_manager, data_manager, ai_manager, logic_manager


# --- Functions --- #
def recipe_pipeline(record, logger=None):
    """Pipeline for the recipe generator. Takes in `record` and `logger` as inputs.
    - `record`: the loaded data from CSV spreadsheet
    - `logger`: enables logging if the logging function is passed through"""

    # If record is empty
    if not record:
        io_manager.display_error(
            "Please key in some ingredients. Ingredients information is missing."
        )
        return record

    # Collect user input
    user_input = io_manager.collect_input(record)

    # If user input is empty
    if not user_input:
        return record

    # Gets AI response on success
    success, response = ai_manager.process(user_input)

    # If AI response failed checks or is malformed
    if not success:
        io_manager.display_error(response)
        return record

    # Check response and user input under business rules
    combined_output = {**user_input, **response}
    evaluated_record = logic_manager.route(combined_output)

    # Store for memory and access previous accepted recipes
    data_manager.save_recipe(evaluated_record, logger=logger)

    io_manager.display_result(evaluated_record)

    # Reload updated data from CSV
    return data_manager.load_recipes(logger=logger)


def add_ingredients(record, logger=None):
    """Pipeline for the adding ingredients to CSV. Takes in `record` and `logger` as inputs.
    - `record`: the loaded data from CSV spreadsheet
    - `logger`: enables logging if the logging function is passed through"""

    # Allows user to add ingredients
    ingredients = io_manager.ingredient_input(
        success_message="\nUpdated the ingredients list!",
        failure_message="No new ingredients were added. ",
    )

    # If new ingredients are added
    if ingredients:
        success = data_manager.save_ingredients(ingredients, logger=logger)

        # Checks if the saving to file attempt was successful and logs messages accordingly
        if success:
            io_manager.display_logs(
                "Successfully saved ingredients to persistent storage."
            )
        else:
            io_manager.display_error("Failed to save ingredients to disk.")

        # Reloads updated data from CSV
        return data_manager.load_ingredients(logger=logger)

    # Returns itself if nothing has changed
    return record


# --- Main Program --- #
def main(logger):
    """Handles the main program for the entire project. Takes in `logger` as input.
    - `logger`: enables logging if the logging function is passed through"""

    # --- Variables & Constants --- #
    ingredients = data_manager.load_ingredients(logger=logger)
    recipes = data_manager.load_recipes(logger=logger)

    # --- Program Code --- #
    while True:
        # Get menu
        choice = io_manager.menu()

        # Adding of new ingredients
        if choice == 1:
            ingredients = add_ingredients(ingredients)

        # List all ingredients
        elif choice == 2:
            io_manager.display_ingredients(ingredients)

        # AI Recipe recommendation
        elif choice == 3:
            recipes = recipe_pipeline(ingredients, logger=logger)

        # View past recipe recommendations
        elif choice == 4:
            while True:
                # Get recipe sub menu
                sub_choice = io_manager.past_recipes_menu()

                # List all past recipes
                if sub_choice == 1:
                    io_manager.display_list(recipes)

                # List successful recipes
                elif sub_choice == 2:
                    successful_recipes = data_manager.filter_by_success(recipes)
                    io_manager.display_list(
                        successful_recipes,
                        message="There are no saved recipes that contain the query. ",
                    )

                # Filter and list recipes based on ingredient matches
                elif sub_choice == 3:
                    ingredient_query = io_manager.prompt_ingredient_query()
                    if ingredient_query:
                        filtered_recipes = data_manager.filter_by_ingredient(
                            recipes, ingredient_query
                        )

                        io_manager.display_list(
                            filtered_recipes,
                            message="There are no saved recipes that contain the query. ",
                        )

                    else:
                        io_manager.display_logs(
                            "Ingredient query is empty. Returning..."
                        )

                # Exit back to main menu
                elif sub_choice == 4:
                    break

        # Exit program
        else:
            break


if __name__ == "__main__":
    main(io_manager.display_logs)
