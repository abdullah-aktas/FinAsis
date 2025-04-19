from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.permissions.permissions import IsSalesStaff
from .serializers import (
    CustomerSerializer,
    LeadSerializer,
    InteractionLogSerializer
)

class CustomerViewSet(viewsets.ModelViewSet):
    """
    Müşteri işlemlerini yönetmek için ViewSet.
    """
    permission_classes = [IsSalesStaff]
    serializer_class = CustomerSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'customer_type']
    search_fields = ['name', 'email', 'phone']
    ordering_fields = ['name', 'created_at', 'last_interaction']
    
    def get_queryset(self):
        return self.request.user.company.customers.all()
    
    @action(detail=True, methods=['post'])
    def convert_to_lead(self, request, pk=None):
        """Müşteriyi potansiyel müşteriye dönüştürür."""
        customer = self.get_object()
        customer.status = 'lead'
        customer.save()
        return Response({'status': 'customer converted to lead'})

class LeadViewSet(viewsets.ModelViewSet):
    """
    Potansiyel müşteri işlemlerini yönetmek için ViewSet.
    """
    permission_classes = [IsSalesStaff]
    serializer_class = LeadSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'source']
    search_fields = ['name', 'email', 'phone']
    ordering_fields = ['name', 'created_at', 'last_contact']
    
    def get_queryset(self):
        return self.request.user.company.leads.all()
    
    @action(detail=True, methods=['post'])
    def convert_to_customer(self, request, pk=None):
        """Potansiyel müşteriyi müşteriye dönüştürür."""
        lead = self.get_object()
        lead.status = 'customer'
        lead.save()
        return Response({'status': 'lead converted to customer'})

class InteractionLogViewSet(viewsets.ModelViewSet):
    """
    Müşteri etkileşim kayıtlarını yönetmek için ViewSet.
    """
    permission_classes = [IsSalesStaff]
    serializer_class = InteractionLogSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['interaction_type', 'customer']
    search_fields = ['notes']
    ordering_fields = ['interaction_date', 'created_at']
    
    def get_queryset(self):
        return self.request.user.company.interaction_logs.all() 