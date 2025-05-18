# -*- coding: utf-8 -*-
"""
api modülü
"""

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import UserRateThrottle
from rest_framework.versioning import URLPathVersioning
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

class BaseAPIView(APIView):
    """
    Tüm API view'ları için temel sınıf
    """
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]
    versioning_class = URLPathVersioning
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    pagination_class = PageNumberPagination

    def get_queryset(self):
        raise NotImplementedError

    def get_serializer_class(self):
        raise NotImplementedError

    def get_serializer_context(self):
        return {
            'request': self.request,
            'format': self.format_kwarg,
            'view': self
        }

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)

    def paginate_queryset(self, queryset):
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        return None

    def get_paginated_response(self, data):
        return Response({
            'status': 'success',
            'data': data,
            'pagination': {
                'count': self.paginator.page.paginator.count,
                'next': self.paginator.get_next_link(),
                'previous': self.paginator.get_previous_link()
            }
        })

    def handle_exception(self, exc):
        if isinstance(exc, Exception):
            return Response({
                'status': 'error',
                'message': str(exc),
                'code': exc.__class__.__name__
            }, status=status.HTTP_400_BAD_REQUEST)
        return super().handle_exception(exc)
