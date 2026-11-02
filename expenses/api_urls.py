from rest_framework.routers import DefaultRouter
from django.urls import path

from .views import (
    ExpenseViewSet,
    CategoryViewSet,
    BudgetViewSet,
    generate_expense_draft,
    generate_monthly_insights,
)

router = DefaultRouter()

router.register("expenses", ExpenseViewSet, basename="expense")
router.register("categories", CategoryViewSet, basename="category")
router.register("budgets", BudgetViewSet, basename="budget")

urlpatterns = [
    path(
        "ai/expense-draft/",
        generate_expense_draft,
        name="generate-expense-draft"
    ),
    path(
    "ai/monthly-insights/",
    generate_monthly_insights,
    name="generate-monthly-insights"
),
]

urlpatterns += router.urls