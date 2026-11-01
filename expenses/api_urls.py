from rest_framework.routers import DefaultRouter

from .views import (
    ExpenseViewSet,
    CategoryViewSet,
    BudgetViewSet,
)

router = DefaultRouter()

router.register("expenses", ExpenseViewSet, basename="expense")
router.register("categories", CategoryViewSet, basename="category")
router.register("budgets", BudgetViewSet, basename="budget")

urlpatterns = router.urls