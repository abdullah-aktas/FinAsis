from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from permissions.permissions import IsFinanceManager
from .serializers import (
    TransactionSerializer,
    CashFlowSerializer,
    IncomeStatementSerializer
)

class TransactionViewSet(viewsets.ModelViewSet):
    """
    Finansal işlemleri yönetmek için ViewSet.
    
    list: Tüm işlemleri listeler
    create: Yeni işlem oluşturur
    retrieve: Belirli bir işlemin detaylarını gösterir
    update: İşlem bilgilerini günceller
    delete: İşlemi siler
    """
    permission_classes = [IsFinanceManager]
    serializer_class = TransactionSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['transaction_type', 'status', 'date']
    search_fields = ['description', 'reference_number']
    ordering_fields = ['date', 'amount', 'created_at']
    
    def get_queryset(self):
        return self.request.user.company.transactions.all()
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """İşlemi onaylar."""
        transaction = self.get_object()
        transaction.status = 'approved'
        transaction.approved_by = request.user
        transaction.save()
        return Response({'status': 'transaction approved'})
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """İşlemi reddeder."""
        transaction = self.get_object()
        transaction.status = 'rejected'
        transaction.rejected_by = request.user
        transaction.save()
        return Response({'status': 'transaction rejected'})

class CashFlowViewSet(viewsets.ModelViewSet):
    """
    Nakit akışı işlemlerini yönetmek için ViewSet.
    """
    permission_classes = [IsFinanceManager]
    serializer_class = CashFlowSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['flow_type', 'period']
    search_fields = ['description']
    ordering_fields = ['date', 'amount']
    
    def get_queryset(self):
        return self.request.user.company.cash_flows.all()

class IncomeStatementViewSet(viewsets.ModelViewSet):
    """
    Gelir tablosu işlemlerini yönetmek için ViewSet.
    """
    permission_classes = [IsFinanceManager]
    serializer_class = IncomeStatementSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['period', 'year']
    search_fields = ['description']
    ordering_fields = ['period', 'year', 'total_revenue']
    
    def get_queryset(self):
        return self.request.user.company.income_statements.all() 