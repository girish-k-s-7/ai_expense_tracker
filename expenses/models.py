from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class Category(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="categories"
    )

    name = models.CharField(max_length=100)

    is_default = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "name"],
                name="unique_category_per_user"
            )
        ]

    def __str__(self):
        return self.name



class Expense(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="expenses"
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="expenses"
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    date = models.DateField()

    note = models.TextField(blank=True)

    payment_method = models.CharField(max_length=50)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.category.name} - {self.amount}"

    def clean(self):
        if (
            self.user_id
            and self.category_id
            and self.user_id != self.category.user_id
        ):
            raise ValidationError(
                "You cannot use another user's category."
            )




class Budget(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="budgets"
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="budgets"
    )

    month = models.DateField()

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "category", "month"],
                name="unique_monthly_budget_per_category"
            )
        ]

    def __str__(self):
        return f"{self.category.name} - {self.month}"

    def clean(self):
        if (
            self.user_id
            and self.category_id
            and self.user_id != self.category.user_id
        ):
            raise ValidationError(
                "You cannot create a budget for another user's category."
            )

