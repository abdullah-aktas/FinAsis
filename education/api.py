from rest_framework import serializers, viewsets
from .models import FinancialTermCard


class FinancialTermCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinancialTermCard
        fields = ["id", "term", "description", "example", "created_at"]


class FinancialTermCardViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FinancialTermCard.objects.all().order_by("-created_at")
    serializer_class = FinancialTermCardSerializer
