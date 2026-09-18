# AI Recipe Planner 

## Problem statement
People often have ingredients in their refrigerator but are unsure what meals they can prepare with them. This can lead to **food waste, unnecessary grocery purchases, and difficulty deciding what to cook.**

Our application aims to solve this problem by allowing users to enter the ingredients they currently have in their refrigerator. The AI will analyse the available ingredients and generate a list of meal suggestions and recipes based on what the user already has. 

## Target Users

#### Target users include:

- Students and young adults who want simple meal ideas.
- Families who want to use ingredients before they expire.
- People who want to reduce food waste.
- Users who are unsure what to cook with their available ingredients.


## User Inputs

Users will provide information about the ingredients available in their refrigerator such as:

- Ingredients
- Quantity available (Mass of item (g), Volume of liquid (ml))
- Dietary preferences
- Serving Size Pax
- Available cooking equipment

*More will be added based on availability and time and resources to scale the project, if relevant.*

### User Input Format

As of now, it will be plain string input based on **Command Line Interface (CLI)**. Depending on time and resources, it may be scaled to a more advanced and convenient method of input.


## Use of AI

AI will analyse the user's inputs and determine suitable meals that can be prepared.

#### The process would be:

Input (User Ingredients) → AI analyzes ingredients -> AI Generates Possible Meal Recipes → Does Recipe Match User Requirements?

 **If**:

 Yes → Display Recipe

 No → Generate Another Recommendation

For example:

**Available Ingredients**: Chicken + rice + egg + carrot + onion

**AI Recommendation**: Chicken Fried Rice

#### Instructions:

Cook the chicken.

Fry the onions and carrots.

Add rice and mix.

Add the chicken and egg.

Season and serve.


## Business Rules

The application will apply rules to ensure that the AI's recommendations are practical and safe.

### Validation Rules

#### Ingredient availability
The AI should only recommend meals using ingredients that the user has or clearly identify additional ingredients that need to be purchased.

#### Allergy restrictions
The system must exclude ingredients that conflict with the user's stated allergies.

#### Dietary restrictions
Recommendations should follow the user's selected dietary requirements.

#### Cooking time
Recipes should match the user's maximum cooking-time preference where possible.
