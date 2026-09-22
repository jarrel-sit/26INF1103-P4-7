# --- Imports --- #
from google import genai
from google.genai import errors
from dotenv import load_dotenv
import os
import json

# --- Load Environment Variables --- #
load_dotenv(dotenv_path="./.env")
API_KEY = os.getenv("GENAI_API_KEY")


# --- Constants --- #
CLIENT = genai.Client(api_key=API_KEY)
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

    try:
        response = ""
        interaction = CLIENT.interactions.create(
            model="gemini-3.1-flash-lite",
            input=prompt,
            response_format=RESPONSE_FORMAT,
            stream=True,  # Enable streaming to receive partial responses as they are generated
        )

        for event in interaction:
            # Check for error events
            if hasattr(event, "error") and event.error:
                print(f"Error Code: {event.error.code}")
                return event.error.message

            # Check if the event contains text delta chunks (successful responses)
            if (
                hasattr(event, "delta")
                and hasattr(event.delta, "text")
                and event.delta.text
            ):
                response += event.delta.text

        return response

    except Exception as e:
        # Catches network drops or client-side issues outside the stream loop
        return f"\nTransport or connection exception: {e}"


def parse_response(response: str):
    """
    Function to parse the response from the API.
    """

    if not response:
        return "No response received from the API."

    # Check for markdown formatting issues in the response, and fix them if necessary
    if response.startswith("```") or response.endswith("```"):
        response = response.strip("```").strip()

    # Parse the response as JSON and handle any parsing errors
    try:
        return json.loads(response)

    except json.JSONDecodeError as e:
        return f"JSON parsing error: {e} \nResponse content: {response}"
