# -*- coding: utf-8 -*-
from django_filters import rest_framework as filters
from .models import ChatSession, ChatMessage, PagePrompt

class ChatSessionFilter(filters.FilterSet):
    status = filters.CharFilter(field_name='status')
    start_date = filters.DateFilter(field_name='created_at', lookup_expr='gte')
    end_date = filters.DateFilter(field_name='created_at', lookup_expr='lte')
    search = filters.CharFilter(method='search_filter')

    class Meta:
        model = ChatSession
        fields = ['status', 'start_date', 'end_date', 'search']

    def search_filter(self, queryset, name, value):
        return queryset.filter(
            Q(title__icontains=value) |
            Q(context__icontains=value)
        )

class ChatMessageFilter(filters.FilterSet):
    message_type = filters.CharFilter(field_name='message_type')
    is_user = filters.BooleanFilter(field_name='is_user')
    start_date = filters.DateFilter(field_name='created_at', lookup_expr='gte')
    end_date = filters.DateFilter(field_name='created_at', lookup_expr='lte')
    search = filters.CharFilter(method='search_filter')

    class Meta:
        model = ChatMessage
        fields = ['message_type', 'is_user', 'start_date', 'end_date', 'search']

    def search_filter(self, queryset, name, value):
        return queryset.filter(content__icontains=value)

class PagePromptFilter(filters.FilterSet):
    page_type = filters.CharFilter(field_name='page_type')
    is_active = filters.BooleanFilter(field_name='is_active')
    priority = filters.NumberFilter(field_name='priority')
    search = filters.CharFilter(method='search_filter')

    class Meta:
        model = PagePrompt
        fields = ['page_type', 'is_active', 'priority', 'search']

    def search_filter(self, queryset, name, value):
        return queryset.filter(
            Q(title__icontains=value) |
            Q(prompt_template__icontains=value)
        ) 