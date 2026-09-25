#Imports
import re

#Input Handling
def pax():
    while True:
        #Asks user for pax input
        num_ppl = input("How many pax is this meal for? ")

        #Checks if user input is non-negative and numeric
        if num_ppl.isnumeric() == False:
            print('Invalid pax input, please input a non-negative number for pax.')
        else:
            #Validation for pax check if pax more than 10 (Large number of people)
            num_ppl = int(num_ppl)
            if num_ppl > 10:
                accept = input("This is a large number of people, results might not be accurate based on your ingredients inputs, are you sure? Please input Yes/No\n").lower()
                pattern = "[yes|no]"
                match = re.match(pattern,accept) 
                if match:
                    print(f'Noted. Pax of {num_ppl} has be taken note of.')
                    return num_ppl
                else:
                    print('Invalid please input a non-negative number for pax.')
            else:
                return num_ppl


#Function for inputting dietary restrictions
def diet():
    #List of existing diets
    diets = ['vegetarian', 'vegan', 'pescetarian', 'halal', 'kosher']
    while True:
        #Asks user for dietary input
        diet_input = input("Any dietary restrictions? Enter without input if no dietary preference. ").lower()

        #User has no dietary preference
        if diet_input == "":
            print('No fixed diet selected, we will show you all the recipes that can be made with the ingredients provided')
            return diet_input

        #User's dietary preference is in list of existing diets
        elif diet_input in diets:
            print(f"Taken note of {diet_input} diet")
            return diet_input

        #User's diet is not empty and is not in list of existing dietary preferences
        else:
            print("Invalid dietary preference, please re-enter dietary preference")
    
#Function for inputting allergies
def allergy():
    allergy_list = []
    allergens = ['milk','soy','fish','peanuts', 'walnuts','almonds', 'eggs' ]
    print("Are you allergic to any foods? Enter without input if no (more) allergies to be stated. ")
    while True:
        #Prompts user if they have any food allergies
        allergic = input('')
        if allergic.lower()  == '' and len(allergy_list) == 0:
            print('You are not allergic to any foods, we will show you all the recipes that can be made with the ingredients provided. \n')
            return allergy_list
        
        #If user input is empty and there is already an allergen in the list, stop and return list of allergens    
        elif allergic.lower() == '' and len(allergy_list) != 0:
            print('Noted. We will exclude recipes with any of these foods in it \n')
            return allergy_list
        
        #Checks if what user is allergic to is in list of allergens, if yes, adds to list of allergens
        elif allergic.lower() in allergens and allergic.lower() not in allergy_list:
            allergy_list.append(allergic)

        #Checks if user's input is already in allergy list
        elif allergic.lower() in allergy_list and allergic.lower() in allergy_list:
            print('We have already taken note of that, please re-input or enter without input if no (more) allergies to be stated. \n')
        
        #Notifies user that allergen is not found
        else:
            print('Unable to identify allergy, please re-input or enter without input if no (more) allergies to be stated. \n')

#Function for inputting ingredient
def ingredient_input():
    #Initiate ingredients list as empty dictionary
    ingredients_list = {}

    #Pattern format to match user's input 
    pattern = r'([A-Za-z]+(?:\s[A-Za-z]+)*)\s*(\d+)\s*(g|ml)'

    #Repeats until user inputs done
    while True:

        #Prompts user to input ingredients with example format
        user_input = input("Enter the ingredient and quantity (e.g., 'Sugar 100g'): ")

        #Checks if user inputs nothing, prompts to re-enter if empty
        if user_input == "":
            print("Input cannot be empty. Please try again.")
            continue

        #Checks if user inputs 'done' and ingredients list is empty
        elif user_input.lower() == "done" and not ingredients_list:
            print("You have not added any ingredients yet, we cannot generate any recipes for you...")

        #User inputs done to stop adding ingredients and ingredients list is not empty
        elif user_input.lower() == "done" and ingredients_list:
            print('Alright, looking for recipes with the ingredients you have...')
            return ingredients_list
        
        else: 
            #Gets rid of case sensitivity input and whitespace of user input
            user_input = user_input.lower().strip()

            #Uses regex to check for formatting of user input
            match = re.match(pattern, user_input)
            if match and re.search(r'[^\w\s]', user_input) is None:

                #Extract the ingredient, quantity, and quantifier from the matched groups
                name = match.group(1)
                quantity = match.group(2) + match.group(3)

                #Adds name and quantity to dictionary
                ingredients_list[name] = quantity

                #Message to indicate valid input from user
                print(f"Valid input received. {name.title()} {quantity} has been added to the ingredients list.")

                #Uncomment to see what enters ingredients_list
                #print(ingredients_list)

            else:
                #Prompts user to input again if user gives rubbish format
                print("Invalid input. Please try again.")
            

#Function Logic



#Function Calls
#diet()
#allergy()
#ingredient_input()
pax()
