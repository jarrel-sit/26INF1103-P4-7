# --- Imports --- #
from google import genai

# --- Constants --- #
API_KEY = "AQ.Ab8RN6LMOUOVeyifr_4w_6hZcIG__9exVtc742oVyL3pilUaiA"


# --- Functions --- #
def call_api(prompt: str = ""):
    """
    Function to call the API and handle the response.
    """
    client = genai.Client(api_key=API_KEY)

    interaction = client.interactions.create(
        model="gemini-3.1-flash-lite",
        input=prompt,
        response_format={
            "type": "text",
            "mime_type": "application/json",
            "schema": {
                "type": "object",
                "properties": {
                    "recipe": {"type": "string"},
                    "ingredients": {"type": "string"},
                    "instructions": {"type": "string"},
                    "confidence": {"type": "number"},
                },
                "required": ["recipe", "ingredients", "instructions", "confidence"],
            },
        },
    )

    return interaction.output_text
