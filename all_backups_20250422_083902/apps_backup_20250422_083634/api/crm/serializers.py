from rest_framework import serializers
from crm.models import Customer, Lead, InteractionLog

class CustomerSerializer(serializers.ModelSerializer):
    """
    Müşteri işlemleri için serializer.
    """
    class Meta:
        model = Customer
        fields = [
            'id', 'name', 'email', 'phone', 'address',
            'customer_type', 'status', 'created_at',
            'updated_at', 'last_interaction'
        ]
        read_only_fields = ['created_at', 'updated_at', 'last_interaction']

class LeadSerializer(serializers.ModelSerializer):
    """
    Potansiyel müşteri işlemleri için serializer.
    """
    class Meta:
        model = Lead
        fields = [
            'id', 'name', 'email', 'phone', 'company',
            'source', 'status', 'created_at',
            'updated_at', 'last_contact'
        ]
        read_only_fields = ['created_at', 'updated_at', 'last_contact']

class InteractionLogSerializer(serializers.ModelSerializer):
    """
    Müşteri etkileşim kayıtları için serializer.
    """
    class Meta:
        model = InteractionLog
        fields = [
            'id', 'customer', 'interaction_type', 'interaction_date',
            'notes', 'created_at', 'updated_at', 'created_by'
        ]
        read_only_fields = ['created_at', 'updated_at', 'created_by'] 