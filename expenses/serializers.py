
from rest_framework import serializers

from .models import Expense, Category

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