# --- Imports --- #
import io_manager, data_manager, ai_manager, logic_manager


# --- Functions --- #
# def recipe_pipeline(record, logger=None):
#     """Pipeline for the recipe generator. Takes in `record` and `logger` as inputs.
#     - `record`: the loaded data from CSV spreadsheet
#     - `logger`: enables logging if the logging function is passed through"""

#     # If record is empty
#     if not record:
#         io_manager.display_error(
#             "Please key in some ingredients. Ingredients information is missing."
#         )
#         return record

#     # Collect user input
#     user_input = io_manager.collect_input(record)

#     # If user input is empty
#     if not user_input:
#         return record

#     # Gets AI response on success
#     success, response = ai_manager.process(user_input)

#     # If AI response failed checks or is malformed
#     if not success:
#         io_manager.display_error(response)
#         return record

#     # Check response and user input under business rules
#     combined_output = {**user_input, **response}
#     evaluated_record = logic_manager.route(combined_output)

#     # Store for memory and access previous accepted recipes
#     data_manager.save_recipe(evaluated_record, logger=logger)

#     io_manager.display_result(evaluated_record)

#     # Reload updated data from CSV
#     return data_manager.load_recipes(logger=logger)

def recipe_pipeline(record, recipe_repo):
    """Pipeline for the recipe generator.
    - `record`: the user's saved ingredients
    - `recipe_repo`: the recipe repository used to save and reload recipes"""

    # If record is empty
    if not record:
        io_manager.display_error(
            "Please key in some ingredients. Ingredients information is missing."
        )
        return recipe_repo.find_all()

    # Collect user input
    user_input = io_manager.collect_input(record)

    # If user input is empty
    if not user_input:
        return recipe_repo.find_all()

    # Gets AI response on success
    success, response = ai_manager.process(user_input)

    # If AI response failed checks or is malformed
    if not success:
        io_manager.display_error(response)
        return recipe_repo.find_all()

    # Check response and user input under business rules
    combined_output = {**user_input, **response}
    evaluated_record = logic_manager.route(combined_output)

    # Store for memory and access previous accepted recipes
    recipe_repo.save(evaluated_record)

    io_manager.display_result(evaluated_record)

    # Reload updated data from CSV
    return recipe_repo.find_all()


def add_ingredients(record, ingredient_repo):
    ingredients = io_manager.ingredient_input(
        success_message="\nUpdated the ingredients list!",
        failure_message="No new ingredients were added. ",
    )

    if ingredients:
        success = ingredient_repo.save_all(ingredients)

        if success:
            io_manager.display_logs("Successfully saved ingredients to persistent storage.")
        else:
            io_manager.display_error("Failed to save ingredients to disk.")

        return ingredient_repo.find_all()

    return record


# --- Main Program --- #
def main(logger):
    """Handles the main program for the entire project. Takes in `logger` as input.
    - `logger`: enables logging if the logging function is passed through"""

    # --- Variables & Constants --- #
    ingredient_repo = data_manager.CsvIngredientRepository(logger=logger)
    ingredients = ingredient_repo.find_all()          # was data_manager.load_ingredients(logger=logger)
    recipe_repo = data_manager.CsvRecipeRepository(logger=logger)
    recipes = recipe_repo.find_all()

    # --- Program Code --- #
    while True:
        # Get menu
        choice = io_manager.menu()

        # Adding of new ingredients
        if choice == 1:
            ingredients = add_ingredients(ingredients, ingredient_repo) #was add_ingredients(ingredients)

        # List all ingredients
        elif choice == 2:
            io_manager.display_ingredients(ingredients)

        # AI Recipe recommendation
        elif choice == 3:
            recipes = recipe_pipeline(ingredients, recipe_repo)

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
                    successful_recipes = recipe_repo.find_successful()
                    io_manager.display_list(
                        successful_recipes,
                        message="There are no saved recipes that contain the query. ",
                    )

                # Filter and list recipes based on ingredient matches
                elif sub_choice == 3:
                    ingredient_query = io_manager.prompt_ingredient_query()
                    if ingredient_query:
                        filtered_recipes = recipe_repo.find_by_ingredient(ingredient_query)

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
