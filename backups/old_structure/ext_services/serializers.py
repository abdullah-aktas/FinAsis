from rest_framework import serializers
from .models import Service, Integration

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['id', 'name', 'description', 'api_endpoint', 'api_key', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class IntegrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Integration
        fields = ['id', 'service', 'name', 'description', 'config', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at'] 