from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Expense
from .serializers import CategorySerializer, ExpenseSerializer

from rest_framework.exceptions import PermissionDenied


from .forms import SignUpForm

from django.db import transaction
from .models import Category


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
        return Expense.objects.filter(
            user=self.request.user
        ).select_related("category")

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