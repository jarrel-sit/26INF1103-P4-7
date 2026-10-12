# Imports
import re

# Input Handling
# def pax():
#     while True:
#         #Asks user for pax input
#         num_ppl = input("How many pax is this meal for? ")

#         #Checks if user input is non-negative and numeric
#         if num_ppl.isnumeric() == False:
#             print('Invalid pax input, please input a non-negative number for pax.')
#         else:
#             #Validation for pax check if pax more than 10 (Large number of people)
#             num_ppl = int(num_ppl)
#             if num_ppl > 10:
#                 accept = input("This is a large number of people, results might not be accurate based on your ingredients inputs, are you sure? Please input Yes/No\n").lower()
#                 pattern = "[yes|no]"
#                 match = re.match(pattern,accept)
#                 if match:
#                     print(f'Noted. Pax of {num_ppl} has be taken note of.')
#                     return num_ppl
#                 else:
#                     print('Invalid please input a non-negative number for pax.')
#             else:
#                 return num_ppl


# Function for inputting dietary restrictions
def diet():
    # List of existing diets
    diets = ["vegetarian", "vegan", "pescetarian", "halal", "kosher"]
    while True:
        # Asks user for dietary input
        diet_input = input(
            "Any dietary restrictions? Enter without input if no dietary preference. "
        ).lower()

        # User has no dietary preference
        if diet_input == "":
            print(
                "No fixed diet selected, we will show you all the recipes that can be made with the ingredients provided"
            )
            return diet_input

        # User's dietary preference is in list of existing diets
        elif diet_input in diets:
            print(f"Taken note of {diet_input} diet")
            return diet_input

        # User's diet is not empty and is not in list of existing dietary preferences
        else:
            print("Invalid dietary preference, please re-enter dietary preference")


# Function for inputting allergies
def allergy():
    allergy_list = []
    allergens = ["milk", "soy", "fish", "peanuts", "walnuts", "almonds", "eggs"]
    print(
        "Are you allergic to any foods? Enter without input if no (more) allergies to be stated. "
    )
    while True:
        # Prompts user if they have any food allergies
        allergic = input("")
        if allergic.lower() == "" and len(allergy_list) == 0:
            print(
                "You are not allergic to any foods, we will show you all the recipes that can be made with the ingredients provided. \n"
            )
            return allergy_list

        # If user input is empty and there is already an allergen in the list, stop and return list of allergens
        elif allergic.lower() == "" and len(allergy_list) != 0:
            print("Noted. We will exclude recipes with any of these foods in it \n")
            return allergy_list

        # Checks if what user is allergic to is in list of allergens, if yes, adds to list of allergens
        elif allergic.lower() in allergens and allergic.lower() not in allergy_list:
            allergy_list.append(allergic)

        # Checks if user's input is already in allergy list
        elif allergic.lower() in allergens and allergic.lower() in allergy_list:
            print(
                "We have already taken note of that, please re-input or enter without input if no (more) allergies to be stated. \n"
            )

        # Notifies user that allergen is not found
        else:
            print(
                "Unable to identify allergy, please re-input or enter without input if no (more) allergies to be stated. \n"
            )


# Function for inputting ingredient
def ingredient_input(
    success_message="Alright, looking for recipes with the ingredients you have...",
    failure_message="You have not added any ingredients yet, we cannot generate any recipes for you...",
):
    # Initiate ingredients list as empty dictionary
    ingredients_list = {}

    # Pattern format to match user's input
    pattern = r"([A-Za-z]+(?:\s[A-Za-z]+)*)\s*(\d+)\s*(g|ml)"

    # Repeats until user inputs done
    while True:

        # Prompts user to input ingredients with example format
        user_input = input("Enter the ingredient and quantity (e.g., 'Sugar 100g'): ")

        # Checks if user inputs nothing, prompts to re-enter if empty
        if user_input == "":
            print("Input cannot be empty. Please try again.")

        # Checks if user inputs 'done' and ingredients list is empty
        elif user_input.lower() == "done" and not ingredients_list:
            print(failure_message)
            return ingredients_list

        # User inputs done to stop adding ingredients and ingredients list is not empty
        elif user_input.lower() == "done" and ingredients_list:
            print(success_message)
            return ingredients_list

        else:
            # Gets rid of case sensitivity input and whitespace of user input
            user_input = user_input.lower().strip()

            # Uses regex to check for formatting of user input
            match = re.match(pattern, user_input)
            if match and re.search(r"[^\w\s]", user_input) is None:

                # Extract the ingredient, quantity, and quantifier from the matched groups
                name = match.group(1)

                # Adds name and quantity to dictionary
                if (
                    match.group(2).isnumeric()
                    and match.group(3) == "ml"
                    or match.group(3) == "g"
                ):
                    quantity = match.group(2) + match.group(3)
                    ingredients_list[name] = quantity

                    # Message to indicate valid input from user
                    print(
                        f"Valid input received. {name.title()} {quantity} has been added to the ingredients list."
                    )

                # Uncomment to see what enters ingredients_list
                # print(ingredients_list)

            else:
                # Prompts user to input again if user gives rubbish format
                print("Invalid input. Please try again.")


def display_ingredients(record):
    if not record:
        print("\nYou have not added any ingredients yet.")
        return

    if isinstance(record, list):
        ingredients = record

    elif isinstance(record, dict):
        ingredients = record.get("ingredients", [])

    print("\n--- Current Available Ingredients ---")
    for item in ingredients:
        print(f" - {item['ingredient']}: {item['quantity']}")


def display_list(records):
    print(f"\n--- Saved Records ({len(records)}) ---")
    for r in records:
        print(
            f"- {r.get('recipe_name')} | Status: {r.get('outcome')} | Score: {r.get('score')}"
        )


def display_error(msg):
    print(f"\n[ERROR]: {msg}")


def display_result(record):
    print("\n" + "=" * 40)
    print(f"RECIPE: {record.get('recipe_name', 'N/A')}")
    print(
        f"OUTCOME: {record.get('outcome', 'N/A').upper()} (Score: {record.get('score', 0)})"
    )
    print(f"REASON: {record.get('reason', '')}")
    print("=" * 40)


def checkfield(ingredients, allergies, dietreq):
    allinputs = {  # "pax": serving,
        "ingredients": ingredients,
        "allergies": allergies,
        "diet": dietreq,
    }

    # if not allinputs.get("pax"):
    #     print("Please key in the serving size. Serving size information is missing.")


# checkfield(ingredients, allergies,dietreq)


def validate_menu(choice, options):
    if choice.isdigit() and int(choice) > 0 and int(choice) <= options:
        return int(choice)
    return None


def menu(options=5):
    print("""
=================================
|           Main Menu           |
|-------------------------------|
|                               |
|  1. Add new ingredients       |
|  2. List current ingredients  |
|  3. Recommend me a recipe!    |
|  4. View past recipes         |
|  5. Exit                      |
|                               |
=================================""")

    while True:
        choice = input("\nSelect option: ").strip()
        validated_choice = validate_menu(choice, options)

        if validated_choice is not None:
            return validated_choice

        print("Invalid option selected. Please try again.")


def display_logs(log: str):
    """Outputs verbose log messages."""
    print(f"{log}")


def select_ingredients_from_available(available_ingredients):
    """
    Displays all available ingredients and prompts the user to select
    which ones they want to use for the current recipe run.
    Validates selections strictly against the available ingredients pool.
    """
    if not available_ingredients:
        return {}

    ingredients = {}

    for row in available_ingredients:
        name = row.get("ingredient").strip()
        ingredients[name] = row.get("quantity")

    if not ingredients:
        return {}

    print("\n--- Available Ingredients Pool ---")
    for item, qty in ingredients.items():
        print(f" - {item}: {qty}")

    selected = {}
    print("\nWhich ingredients would you like to use for this recipe?")
    print(
        "Type ingredient names one by one (or type 'all' to use everything, 'done' when finished):"
    )

    while True:
        user_choice = input("> ").strip().lower()

        if user_choice == "done":
            if not selected:
                print("No ingredients selected yet. Returning back to main menu...")
            break

        elif user_choice == "all":
            return ingredients

        elif user_choice in ingredients.keys():
            selected[user_choice] = ingredients[user_choice]

            print(
                f"-> Added '{user_choice}' ({ingredients[user_choice]}) to recipe inputs."
            )
        else:
            print(
                f"'{user_choice}' is not in your available ingredients. Please select from the list above."
            )

    return selected


def collect_input(record):
    """Combines all input prompts into one standard record dict."""
    # pax_val = input("How many pax is this meal for? ").strip()
    # pax_num = int(pax_val) if pax_val.isdigit() else 1

    ingredient_list = select_ingredients_from_available(record)
    allergies_list = allergy()
    diet_list = diet()

    ## cooking time??

    return {
        # "pax": pax_num,
        "ingredients": ingredient_list,
        "available_ingredients": [
            {row.get("ingredient"), row.get("quantity")} for row in record
        ],
        "allergies": allergies_list,
        "dietary_preferences": diet_list,
        # "max_cooking_time_minutes": 60 !! PLEASE CHANGE ACCORDINGLY
    }


def past_recipes_menu(options=4):
    """Displays the submenu for filtering past recipes."""
    print("""
=================================
|      Past Recipes Submenu     |
|-------------------------------|
|  1. View All Saved Recipes    |
|  2. View Successful Only      |
|  3. Filter by Ingredient      |
|  4. Back to Main Menu         |
=================================""")

    while True:
        choice = input("\nSelect option: ").strip()
        if choice.isdigit() and int(choice) <= options and int(choice) > 0:
            return int(choice)
        print("Invalid option selected. Please try again.")


def prompt_ingredient_query():
    """Prompts the user for an ingredient name to filter past recipes."""
    return input("Enter the ingredient name to search for: ").strip()
