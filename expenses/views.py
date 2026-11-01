from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Expense
from .serializers import ExpenseSerializer

from .forms import SignUpForm


def signup_view(request):

    if request.method == "POST":
        form = SignUpForm(request.POST)

        if form.is_valid():
            form.save()
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