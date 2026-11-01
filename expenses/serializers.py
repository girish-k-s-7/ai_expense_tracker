
from rest_framework import serializers

from .models import Expense, Category, Budget

class ExpenseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Expense

        fields = [
            "id",
            "category",
            "amount",
            "date",
            "note",
            "payment_method",
            "created_at",
        ]

        read_only_fields = ["id", "created_at"]

    def validate_category(self, category):

        request = self.context.get("request")

        if request and category.user_id != request.user.id:
            raise serializers.ValidationError(
                "You cannot use another user's category."
            )

        return category


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category

        fields = [
            "id",
            "name",
            "is_default",
        ]

        read_only_fields = ["id", "is_default"]

class BudgetSerializer(serializers.ModelSerializer):

    spent = serializers.SerializerMethodField()
    remaining = serializers.SerializerMethodField()
    percentage_used = serializers.SerializerMethodField()

    class Meta:
        model = Budget

        fields = [
            "id",
            "category",
            "month",
            "amount",
            "spent",
            "remaining",
            "percentage_used",
        ]

        read_only_fields = [
            "id",
            "spent",
            "remaining",
            "percentage_used",
        ]

    def get_spent(self, obj):
        from django.db.models import Sum

        result = Expense.objects.filter(
            user=obj.user,
            category=obj.category,
            date__year=obj.month.year,
            date__month=obj.month.month
        ).aggregate(total=Sum("amount"))

        return result["total"] or 0

    def get_remaining(self, obj):
        spent = self.get_spent(obj)
        return max(obj.amount - spent, 0)

    def get_percentage_used(self, obj):
        spent = self.get_spent(obj)

        if obj.amount == 0:
            return 0

        return round((spent / obj.amount) * 100, 2)

    def validate_category(self, category):
        request = self.context.get("request")

        if request and category.user_id != request.user.id:
            raise serializers.ValidationError(
                "You cannot use another user's category."
            )

        return category