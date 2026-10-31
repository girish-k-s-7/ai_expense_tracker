from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

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