# --- Imports --- #
from google import genai
from dotenv import load_dotenv
import os

# --- Load Environment Variables --- #
load_dotenv(dotenv_path="./.env")
API_KEY = os.getenv("GENAI_API_KEY")


# --- Constants --- #
RESPONSE_FORMAT = {
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
}


# --- Functions --- #
def call_api(prompt: str = ""):
    """
    Function to call the API and handle the response.
    """

    client = genai.Client(api_key=API_KEY)

    interaction = client.interactions.create(
        model="gemini-3.1-flash-lite",
        input=prompt,
        response_format=RESPONSE_FORMAT,
    )

    return interaction.output_text
