# -*- coding: utf-8 -*-
from rest_framework import serializers
from .models import Customer, CustomerNote, CustomerDocument

class CustomerNoteSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source='created_by.username')

    class Meta:
        model = CustomerNote
        fields = ('id', 'title', 'content', 'created_by', 'created_at', 'updated_at')
        read_only_fields = ('created_by', 'created_at', 'updated_at')

class CustomerDocumentSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source='created_by.username')

    class Meta:
        model = CustomerDocument
        fields = ('id', 'title', 'file', 'description', 'created_by', 'created_at', 'updated_at')
        read_only_fields = ('created_by', 'created_at', 'updated_at')

class CustomerSerializer(serializers.ModelSerializer):
    notes = CustomerNoteSerializer(many=True, read_only=True)
    documents = CustomerDocumentSerializer(many=True, read_only=True)
    created_by = serializers.ReadOnlyField(source='created_by.username')

    class Meta:
        model = Customer
        fields = ('id', 'name', 'email', 'phone', 'company', 'address', 'tax_number', 'tax_office', 'notes', 'created_by', 'created_at', 'updated_at', 'is_active', 'notes', 'documents')
        read_only_fields = ('created_by', 'created_at', 'updated_at') 