# --- Imports --- #
from google import genai
from .ai_client import AIClient


# --- Classes --- #
class GeminiClient(AIClient):
    def __init__(self, api_key: str):
        self._client = genai.Client(api_key=api_key)
        self._model = "gemini-3.1-flash-lite"

    def generate(self, prompt: str) -> str:
        response = ""

        # Implementation for calling the underlying client
        interaction = self._client.interactions.create(
            model="gemini-3.1-flash-lite",
            input=prompt,
            stream=True,  # Enable streaming to receive partial responses as they are generated
        )

        for event in interaction:
            # Check for error events
            if hasattr(event, "error") and event.error:
                return f"API Error ({event.error.code}): {event.error.message}"

            # Check if the event contains text delta chunks (successful responses)
            if (
                hasattr(event, "delta")
                and hasattr(event.delta, "text")
                and event.delta.text
            ):
                response += event.delta.text
        return response
