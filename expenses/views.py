
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django.utils import timezone

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

from .models import Expense, Category, Budget
from .serializers import (
    ExpenseSerializer,
    CategorySerializer,
    BudgetSerializer,
)

from .forms import SignUpForm

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status

from ai_services.llm import (
    call_llm,
    build_expense_prompt,
    parse_expense_response,
    validate_expense_data,
)


DEFAULT_CATEGORIES = [
    "Food",
    "Travel",
    "Shopping",
    "Entertainment",
    "Bills",
    "Healthcare",
    "Education",
    "Groceries",
    "Rent",
    "Others",
]


def signup_view(request):

    if request.method == "POST":
        form = SignUpForm(request.POST)

        if form.is_valid():

            with transaction.atomic():

                user = form.save()

                Category.objects.bulk_create([
                    Category(
                        user=user,
                        name=name,
                        is_default=True
                    )
                    for name in DEFAULT_CATEGORIES
                ])

            return redirect("login")

    else:
        form = SignUpForm()

    return render(request, "expenses/signup.html", {"form": form})



@login_required
def dashboard_view(request):

    user = request.user
    today = timezone.localdate()

    # Total expenses
    total_expenses = Expense.objects.filter(
        user=user
    ).aggregate(
        total=Sum("amount")
    )["total"] or 0

    # Current month's expenses
    monthly_expenses = Expense.objects.filter(
        user=user,
        date__year=today.year,
        date__month=today.month
    ).aggregate(
        total=Sum("amount")
    )["total"] or 0

    # Current month's budgets
    monthly_budgets = Budget.objects.filter(
        user=user,
        month__year=today.year,
        month__month=today.month
    )

    total_budget = monthly_budgets.aggregate(
        total=Sum("amount")
    )["total"] or 0

    remaining_budget = max(
        total_budget - monthly_expenses,
        0
    )

    # Category-wise spending
    category_expenses = Expense.objects.filter(
        user=user,
        date__year=today.year,
        date__month=today.month
    ).values(
        "category__name"
    ).annotate(
        total=Sum("amount")
    ).order_by("-total")

    # Monthly spending trend
    monthly_trend = Expense.objects.filter(
        user=user
    ).annotate(
        month=TruncMonth("date")
    ).values(
        "month"
    ).annotate(
        total=Sum("amount")
    ).order_by("month")

    # Budget progress by category
    budget_progress = []

    for budget in monthly_budgets:

        spent = Expense.objects.filter(
            user=user,
            category=budget.category,
            date__year=today.year,
            date__month=today.month
        ).aggregate(
            total=Sum("amount")
        )["total"] or 0

        percentage = 0

        if budget.amount > 0:
            percentage = round(
                (spent / budget.amount) * 100,
                2
            )

        budget_progress.append({
            "category": budget.category.name,
            "amount": budget.amount,
            "spent": spent,
            "remaining": max(budget.amount - spent, 0),
            "percentage": percentage,
        })

    # Recent expenses
    recent_expenses = Expense.objects.filter(
        user=user
    ).select_related(
        "category"
    ).order_by(
        "-date", "-created_at"
    )[:5]

    context = {
        "total_expenses": total_expenses,
        "monthly_expenses": monthly_expenses,
        "total_budget": total_budget,
        "remaining_budget": remaining_budget,
        "category_expenses": category_expenses,
        "monthly_trend": monthly_trend,
        "budget_progress": budget_progress,
        "recent_expenses": recent_expenses,
    }

    return render(
        request,
        "expenses/dashboard.html",
        context
    )


class ExpenseViewSet(viewsets.ModelViewSet):

    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        queryset = Expense.objects.filter(
            user=self.request.user
        ).select_related("category")

        params = self.request.query_params

        category = params.get("category")
        start_date = params.get("start_date")
        end_date = params.get("end_date")
        min_amount = params.get("min_amount")
        max_amount = params.get("max_amount")
        search = params.get("search")

        if category:
            queryset = queryset.filter(category_id=category)

        if start_date:
            queryset = queryset.filter(date__gte=start_date)

        if end_date:
            queryset = queryset.filter(date__lte=end_date)

        if min_amount:
            queryset = queryset.filter(amount__gte=min_amount)

        if max_amount:
            queryset = queryset.filter(amount__lte=max_amount)

        if search:
            queryset = queryset.filter(note__icontains=search)

        return queryset.order_by("-date")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CategoryViewSet(viewsets.ModelViewSet):

    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Category.objects.filter(
            user=self.request.user
        ).order_by("name")

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            is_default=False
        )

    def perform_update(self, serializer):

        category = self.get_object()

        if category.is_default:
            raise PermissionDenied(
                "Default categories cannot be modified."
            )

        serializer.save()

    def perform_destroy(self, instance):

        if instance.is_default:
            raise PermissionDenied(
                "Default categories cannot be deleted."
            )

        instance.delete()


class BudgetViewSet(viewsets.ModelViewSet):

    serializer_class = BudgetSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Budget.objects.filter(
            user=self.request.user
        ).select_related("category").order_by("-month")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def generate_expense_draft(request):

    user_input = request.data.get("description", "").strip()

    if not user_input:
        return Response(
            {"error": "Please enter an expense description."},
            status=status.HTTP_400_BAD_REQUEST
        )

    if len(user_input) > 1000:
        return Response(
            {"error": "Description cannot exceed 1000 characters."},
            status=status.HTTP_400_BAD_REQUEST
        )

    categories = list(
        Category.objects.filter(
            user=request.user
        ).values_list("name", flat=True)
    )

    today = timezone.localdate().isoformat()

    try:
        prompt = build_expense_prompt(
            user_input=user_input,
            categories=categories,
            today=today
        )

        gemini_response = call_llm(prompt)

        expense_data = parse_expense_response(
            gemini_response
        )

        validated_data = validate_expense_data(
            expense_data,
            categories
        )

        return Response(
            {
                "message": "Expense draft generated successfully.",
                "expense": {
                    "amount": str(validated_data["amount"]),
                    "category": validated_data["category"],
                    "date": validated_data["date"].isoformat(),
                    "payment_method": validated_data["payment_method"],
                    "note": validated_data["note"],
                }
            },
            status=status.HTTP_200_OK
        )

    except (ValueError, RuntimeError) as error:
        return Response(
            {"error": str(error)},
            status=status.HTTP_400_BAD_REQUEST
        )