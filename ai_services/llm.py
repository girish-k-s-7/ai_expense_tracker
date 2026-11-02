import os

from dotenv import load_dotenv
from google import genai
from google.genai import errors

import json

from datetime import date
from decimal import Decimal, InvalidOperation

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


def build_expense_prompt(user_input: str, categories: list, today: str) -> str:
    category_list = ", ".join(categories)

    prompt = f"""
    You are an expense extraction assistant.

    Extract expense details from the user's description.

    Today's date: {today}

    Available categories: {category_list}

    User's description: {user_input}

    Follow these rules:
    1. Extract the expense amount.
    2. Select the most suitable category from the available categories.
    3. Never create a category that is not in the available categories.
    4. Convert relative dates such as today and yesterday into YYYY-MM-DD.
    5. Extract the payment method if mentioned.
    6. Write a short description in the note field.
    7. If information is missing, return an empty string for that field.
    8. Never invent missing information.
    9. Return valid JSON only. Do not include Markdown or explanations.

    Return exactly this JSON structure:

    {{
        "amount": "",
        "category": "",
        "date": "",
        "payment_method": "",
        "note": ""
    }}
    """

    return prompt

def parse_expense_response(response: str) -> dict:
    try:
        expense_data = json.loads(response)

        if not isinstance(expense_data, dict):
            raise ValueError("Gemini response must be a JSON object.")

        return expense_data

    except json.JSONDecodeError as error:
        raise ValueError(
            "Gemini returned invalid JSON."
        ) from error


def validate_expense_data(expense_data: dict, categories: list) -> dict:
    required_fields = {
        "amount",
        "category",
        "date",
        "payment_method",
        "note"
    }

    if set(expense_data.keys()) != required_fields:
        raise ValueError("Gemini returned an incorrect data structure.")

    try:
        amount = Decimal(str(expense_data["amount"]))

        if not amount.is_finite() or amount <= 0:
            raise ValueError("Expense amount must be positive.")

    except (InvalidOperation, TypeError):
        raise ValueError("Invalid expense amount.")

    category = expense_data["category"]

    if category and category not in categories:
        raise ValueError("Invalid expense category.")

    try:
        expense_date = date.fromisoformat(expense_data["date"])
    except (ValueError, TypeError):
        raise ValueError("Invalid expense date.")

    payment_method = expense_data["payment_method"]
    note = expense_data["note"]

    if not isinstance(payment_method, str) or len(payment_method) > 50:
        raise ValueError("Invalid payment method.")

    if not isinstance(note, str):
        raise ValueError("Invalid expense note.")

    return {
        "amount": amount,
        "category": category,
        "date": expense_date,
        "payment_method": payment_method,
        "note": note
    }