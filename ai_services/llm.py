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
    5. If the user does not mention a date, return an empty string.
    6. Write a short description in the note field.
    7. If the user does not mention a payment method, return an empty string.
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

def build_monthly_insights_prompt(monthly_data: dict) -> str:

    prompt = f"""
    You are a personal finance assistant.

    Analyse the following monthly financial summary
    and provide useful financial insights.

    Financial data:
    {json.dumps(monthly_data, indent=4)}

    
    Instructions:
    1. Summarize the user's total monthly spending.
    2. Identify the highest spending category.
    3. Explain the budget performance for each budgeted category.
    4. Clearly identify categories that do not have a budget.
    5. Compare spending with the previous month.
    6. Suggest 2 or 3 practical ways to manage expenses.
    7. Mention important spending patterns.
    8. Use only the financial data provided.
    9. Never invent amounts, percentages, categories, or financial facts.
    10. If previous-month data is unavailable, clearly mention it.
    11. Keep the language simple, clear, and easy to understand.
    12. All financial amounts are in Indian Rupees (INR).
    13. Always use ₹ when displaying currency.
    14. Never use $, USD, or any other currency symbol.
    15. Do not describe the sum of category budgets as an overall
        budget unless all spending categories are budgeted.
    16. Never claim that total spending is within an overall budget
        when only some categories have budgets.
    17. Clearly distinguish between budgeted and unbudgeted
        categories.
    18. Do not assume that unspent budget means actual savings.
    19. Do not make unsupported assumptions about the user's
        income, savings, or financial goals.
    20. If there is no spending data, clearly state that.
    21. Avoid repeating the same information in multiple sections.
    22. Keep recommendations relevant to the actual spending data.
    23. Do not give investment, loan, or tax advice.

    Formatting Rules:
    1. Write the entire report using normal sentences and paragraphs.
    2. Do not use Markdown formatting.
    3. Do not use #, *, **, bullet points, or numbered lists.
    4. Use simple section titles as plain text.
    5. Separate each section with a blank line.
    6. Write recommendations as normal sentences.
    7. Keep the report concise and readable.
    8. Do not include greetings, introductions, or unnecessary
       closing statements.

    Use exactly these section titles:

    Monthly Spending Summary

    Category Analysis

    Budget Analysis

    Previous Month Comparison

    Recommendations

    Return the complete report as plain text only.
    """

    return prompt