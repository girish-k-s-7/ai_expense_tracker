
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db import transaction

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
    return render(request, "expenses/dashboard.html")


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
