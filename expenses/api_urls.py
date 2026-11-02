from rest_framework.routers import DefaultRouter
from django.urls import path

from .views import (
    ExpenseViewSet,
    CategoryViewSet,
    BudgetViewSet,
    generate_expense_draft,
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
]

urlpatterns += router.urls