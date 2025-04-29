# -*- coding: utf-8 -*-
from rest_framework import serializers
from .models import (
    ChatSession, ChatMessage, PagePrompt,
    UserPreference, AssistantCapability,
    AssistantPerformance
)

class AssistantCapabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = AssistantCapability
        fields = ['id', 'name', 'code', 'description', 'is_active', 'priority']
        read_only_fields = ['id']

class UserPreferenceSerializer(serializers.ModelSerializer):
    enabled_capabilities = AssistantCapabilitySerializer(many=True, read_only=True)
    
    class Meta:
        model = UserPreference
        fields = [
            'id', 'language', 'voice_style', 'response_speed',
            'enabled_capabilities', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = [
            'id', 'session', 'content', 'message_type',
            'is_user', 'metadata', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class ChatSessionSerializer(serializers.ModelSerializer):
    messages = ChatMessageSerializer(many=True, read_only=True)
    user = serializers.StringRelatedField()
    
    class Meta:
        model = ChatSession
        fields = [
            'id', 'user', 'title', 'status', 'context',
            'metadata', 'messages', 'created_at', 'updated_at',
            'last_activity'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'last_activity']

class PagePromptSerializer(serializers.ModelSerializer):
    class Meta:
        model = PagePrompt
        fields = [
            'id', 'page_path', 'page_type', 'title',
            'prompt_template', 'context_variables', 'is_active',
            'priority', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class AssistantPerformanceSerializer(serializers.ModelSerializer):
    session = serializers.StringRelatedField()
    capability_used = AssistantCapabilitySerializer(read_only=True)
    
    class Meta:
        model = AssistantPerformance
        fields = [
            'id', 'session', 'response_time', 'token_count',
            'capability_used', 'user_feedback', 'created_at'
        ]
        read_only_fields = ['id', 'created_at'] 