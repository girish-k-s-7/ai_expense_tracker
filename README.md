# AI Expense Tracker

An intelligent personal finance management application built with **Django, Django REST Framework, and Google Gemini AI**.

AI Expense Tracker helps users manage daily expenses, organize spending, set monthly budgets, visualize financial activity, and receive AI-powered financial insights.

The application combines traditional expense tracking with AI capabilities to make personal finance management simpler and more insightful.

---

## Features

### 1. User Authentication
- User registration and login.
- Session-based authentication using Django.
- User-specific financial data.
- Secure password handling through Django authentication.

### 2. Expense Management
- Add, view, update, and delete expenses.
- Organize expenses using categories.
- Track amount, date, payment method, and notes.
- Search expenses using notes.
- Filter expenses by category, date range, and amount.
- Paginated expense listing.

### 3. Dashboard and Analytics
- View total spending and financial summaries.
- Visualize category-wise expenses using doughnut charts.
- Track monthly spending trends using line charts.
- View recent transactions.
- Monitor monthly budget progress.

### 4. Category Management
- Default expense categories.
- User-specific custom categories.
- Category-based expense organization.
- Protection against modifying or deleting default categories.

### 5. Monthly Budget Management
- Create monthly budgets for expense categories.
- View budget limits and spending.
- Calculate remaining budget.
- Monitor budget utilization through progress indicators.
- Edit and delete budgets.

### 6. AI-Powered Expense Assistant
- Enter expenses using natural language.
- Gemini extracts relevant expense information.
- Automatically generates a structured expense draft.
- Review and edit extracted information before saving.

Example:

Input:
`Spent 450 rupees on dinner using UPI yesterday.`

The AI assistant extracts the relevant expense details into a draft for user review.

### 7. AI Monthly Financial Insights
- Generate AI-powered monthly financial summaries.
- Compare current and previous month spending.
- Identify category-wise spending patterns.
- Review monthly budget performance.
- Receive understandable financial observations.

**Important:** Financial calculations are performed by Django. Gemini is used to generate natural-language explanations from the calculated financial summaries.

---

## Technology Stack

| Layer | Technology |
|---|---|
| Backend | Python, Django |
| API | Django REST Framework |
| Database | SQLite |
| Frontend | HTML, CSS, JavaScript |
| Templates | Django Templates |
| Charts | Chart.js |
| AI Integration | Google Gemini API |
| AI SDK | Google GenAI Python SDK |
| Authentication | Django Authentication |
| Version Control | Git and GitHub |

---

## Project Architecture

The application follows a simple Django-based architecture.

```text
ai_expense_tracker/
│
├── ai_services/
│   └── llm.py
│
├── config/
│   ├── settings.py
│   ├── urls.py
│   └── ...
│
├── expenses/
│   ├── migrations/
│   ├── templates/
│   │   └── expenses/
│   │       ├── base.html
│   │       ├── dashboard.html
│   │       ├── expenses.html
│   │       ├── budgets.html
│   │       ├── login.html
│   │       └── signup.html
│   │
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── api_urls.py
│
├── manage.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## Database Models

The application uses three primary models:

### Category
Stores expense categories belonging to individual users.

### Expense
Stores individual expense transactions, including:
- User
- Category
- Amount
- Date
- Note
- Payment method
- Creation timestamp

### Budget
Stores monthly spending limits for individual categories.

Each budget belongs to a user and a category and is associated with a month.

---

## Getting Started

Follow these steps to run the project locally.

### 1. Clone the Repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd ai_expense_tracker
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

Activate it:

**Linux / macOS**

```bash
source .venv/bin/activate
```

**Windows**

```bash
.venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root.

```env
DJANGO_SECRET_KEY=your_django_secret_key
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost

GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=your_configured_gemini_model
```

Replace the placeholder values with your own configuration.

Never commit your `.env` file or expose API keys in the repository.

### 5. Apply Database Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Start the Development Server

```bash
python manage.py runserver
```

Open the application:

```text
http://127.0.0.1:8000/
```

Register a new account and start tracking expenses.

---

## API Overview

The application provides REST API endpoints through Django REST Framework.

| Endpoint | Purpose |
|---|---|
| `/api/expenses/` | Expense management |
| `/api/categories/` | Category management |
| `/api/budgets/` | Monthly budget management |
| `/api/ai/expense-draft/` | AI expense draft generation |
| `/api/ai/monthly-insights/` | AI monthly financial insights |

The API uses authenticated, user-scoped access for financial records.

---

## Security Considerations

- Django's built-in authentication system.
- Session-based authentication.
- CSRF protection for state-changing requests.
- User-specific database querysets.
- Category ownership validation.
- Environment variables for sensitive credentials.
- Financial calculations performed on the backend.
- AI receives calculated financial summaries for monthly insights rather than direct database access.

---

## AI Integration

Google Gemini is integrated using the official Google GenAI Python SDK.

The integration is organized in:

```text
ai_services/llm.py
```

The application uses AI for two primary workflows:

1. **Natural Language Expense Entry:** Converts user descriptions into structured expense drafts.
2. **Monthly Financial Insights:** Generates readable explanations based on financial summaries calculated by Django.

AI-generated expense information is reviewed by the user before being saved.

---

## Future Improvements

Potential future enhancements include:

- Deployment to a cloud hosting platform.
- PostgreSQL database support.
- More advanced financial analytics.
- Improved budget recommendations.
- Additional AI-powered financial assistance.

---

## Project Status

**Core development completed.**

The application includes expense management, budgeting, dashboard analytics, user authentication, and Gemini-powered features.

Deployment and further improvements can be added in future iterations.

---

## Author

Developed as a Python full-stack and AI integration project.

**Technologies:** Python | Django | Django REST Framework | SQLite | JavaScript | Google Gemini AI
