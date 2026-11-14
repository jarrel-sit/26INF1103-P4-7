#Imports
from display_io import Display
import re

#Validates all the inputs needed for the recipe
class RecipeRequestValidator:
     #Validation for diet
     def validate_diet(self,diet, dietlist):
          if diet in dietlist:
               print(f"Taken note of {diet} dietary restriction, we will ensure that generated recipes adhere to {diet} dietary restrictions.")
               return True

    #Validation for allergy
     def validate_allergy(self, allergy, allergylist):
          if allergy in allergylist:
               print(f"Taken note of {allergy} allergy, we will not include {allergy} in your generated recipes")
               return True

    #Validation for ingredients
     def validate_ingredients(self, ingredient):
          pattern = r"([A-Za-z]+(?:\s[A-Za-z]+)*)\s*(\d+)\s*(g|ml)"
          match = re.match(pattern, ingredient)
          if match and re.search(r"[^\w\s]", ingredient) is None:
               name = match.group(1)
               if (match.group(2).isnumeric() and match.group(3) == "ml" or match.group(3) == "g"):
                    quantity = match.group(2) + match.group(3)
                    print(f"Valid input received. {name.title()} {quantity} has been added to the ingredients list.")
                    ingredient = {name:quantity}
                    return ingredient

               else:
                    print("Invalid item detected. Please ensure that ingredient entered follows the proper format.")

#Collects all the inputs needed for the recipe
class RecipeRequestCollector:
     def __init__(self, validator=RecipeRequestValidator,
                   dietlist = ["vegetarian", "vegan", "pescetarian", "halal", "kosher"],
                   allergylist = ["milk", "soy", "fish", "peanuts", "nuts", "almonds", "eggs"]):
          self.dietlist = dietlist
          self.allergylist = allergylist
          self.__validator = validator
          self._display = Display

    #Consolidates diet,allergy and ingredients
     def collect_input(self):
          diet = self._collect_diet()
          allergy = self._collect_allergy()
          ingredients = self._collect_ingredients()
          self.record = [allergy,diet,ingredients]
          return self.record

    #Recieves input for diet
     def _collect_diet(self):
               self.user_diet = "none"
               while True:
                    diet = input("Do you have any dietary restrictions? Input none if not applicable: \n").lower().strip()
                    success = self.__validator.validate_diet(self, diet, self.dietlist)
          
                    if success:
                         self.user_diet = diet
                         return
                    elif not success and diet == "none":
                         self.user_diet = "none"
                         return self.user_diet
                    else:
                         self._display.display_error("We do not recognise this diet type. Ensure you typed it in correctly.")
                    print(self.user_diet)
                    
    #Recieves input for allergy
     def _collect_allergy(self):
          self.user_allergies = []
          while True:
               allergy = input("Do you have any allergies? Input if any, input done when there are no more allergies to be input: \n").lower().strip()
               success = self.__validator.validate_allergy(self, allergy, self.allergylist)

               if success:
                    self.user_allergies.append(allergy)
                    print(self.user_allergies)
               elif not success and allergy == "done":
                    return self.user_allergies
               else:
                    self._display.display_error("We do not recognise this allergy. Ensure you typed it in correctly.")
                    
    #Recieves input for ingredients
     def _collect_ingredients(self):
          self.user_ingredients = []
          while True:
               ingredient = input("Input ingredients and quantity, following this format E.g: Apple: 50g \n")
               success = self.__validator.validate_ingredients(self,ingredient)
               if success:
                    self.user_ingredients.append(success)
               elif not success and ingredient == "done":
                    return self.user_ingredients
               else:
                    self._display.display_error("Invalid input, please ensure you have entered the ingredient in the correct format. ")