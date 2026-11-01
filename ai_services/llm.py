import os

from dotenv import load_dotenv
from google import genai
from google.genai import errors


load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")


if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is missing from environment variables.")


client = genai.Client(api_key=GEMINI_API_KEY)


def call_llm(prompt: str) -> str:
    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt
        )

        if not response.text:
            raise ValueError("Gemini returned an empty response.")

        return response.text

    except errors.APIError as error:
        raise RuntimeError(
            f"Gemini API error: {error.message}"
        ) from error

    except Exception as error:
        raise RuntimeError(
            "Unable to communicate with Gemini."
        ) from error