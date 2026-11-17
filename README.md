[![Python application CI script](https://github.com/jarrel-sit/26INF1103-P4-7/actions/workflows/python-app.yml/badge.svg)](https://github.com/jarrel-sit/26INF1103-P4-7/actions/workflows/python-app.yml)

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

Input (User Ingredients) -> AI analyzes ingredients -> Input (Allergies and Diet) -> AI Generates Possible Meal Recipes -> Does the recipe match user requirements?

 **If**:

 Yes → Display Recipe with successful outcome

 No → Display Recipe with rejected outcome and display warning that the recipe is not up to standard, proceed with caution

For example:

**Available Ingredients**: Chicken + rice + egg + carrot + onion

**AI Recommendation**: Chicken Fried Rice

#### Instructions:

Cook the chicken. (8 mins)

Fry the onions and carrots. (5 mins)

Add rice and mix. (2 mins)

Add the chicken and egg. (1 min)

Season and serve. (1 min)


## Business Rules

The application will apply rules to ensure that the AI's recommendations are practical and safe.

### Validation Rules

#### Ingredient availability
The AI should only recommend meals using ingredients that the user has or clearly identify additional ingredients that need to be purchased.

#### Allergy restrictions
The system must exclude ingredients that conflict with the user's stated allergies.

#### Dietary restrictions
Recommendations should follow the user's selected dietary requirements.

---
## Continuous Integration (CI) Workflow

This repository uses GitHub Actions to include CI pipeline. Its configuration is located in our repository at `.github/workflows/python-app.yml`.

### Workflow Triggers

The CI pipeline is configured to execute automatically whenever code is pushed to **any branch** or when a pull request is opened against **any branch**.

### Automated Testing & API Independence

Our CI script automatically sets up a Python 3.11 environment, installs project dependencies from `requirements.txt`, and executes our automated test suite using `pytest`.

To ensure the tests strictly verify core logic independently of a live API connection, the workflow injects a dummy environment variable (`GENAI_API_KEY: "test_api_key"`). This allows the test suite to execute successfully using hardcoded sample responses without crashing due to missing real credentials.

### Code Quality

Before running the tests, the workflow includes a linting step using `flake8` to catch Python syntax errors, undefined names, and complexity issues, ensuring good programming practices are maintained throughout the codebase.