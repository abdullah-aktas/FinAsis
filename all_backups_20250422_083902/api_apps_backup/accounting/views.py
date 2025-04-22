from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from permissions.permissions import IsAccountingStaff
from .serializers import (
    JournalEntrySerializer,
    AccountPlanSerializer,
    BalanceSheetSerializer
)

class JournalEntryViewSet(viewsets.ModelViewSet):
    """
    Muhasebe kayıtlarını yönetmek için ViewSet.
    """
    permission_classes = [IsAccountingStaff]
    serializer_class = JournalEntrySerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['entry_type', 'status', 'date']
    search_fields = ['description', 'reference_number']
    ordering_fields = ['date', 'amount', 'created_at']
    
    def get_queryset(self):
        return self.request.user.company.journal_entries.all()
    
    @action(detail=True, methods=['post'])
    def post_entry(self, request, pk=None):
        """Muhasebe kaydını deftere işler."""
        entry = self.get_object()
        entry.status = 'posted'
        entry.posted_by = request.user
        entry.save()
        return Response({'status': 'entry posted'})

class AccountPlanViewSet(viewsets.ModelViewSet):
    """
    Hesap planı işlemlerini yönetmek için ViewSet.
    """
    permission_classes = [IsAccountingStaff]
    serializer_class = AccountPlanSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['account_type', 'status']
    search_fields = ['account_code', 'account_name']
    ordering_fields = ['account_code', 'account_name']
    
    def get_queryset(self):
        return self.request.user.company.account_plans.all()

class BalanceSheetViewSet(viewsets.ModelViewSet):
    """
    Bilanço işlemlerini yönetmek için ViewSet.
    """
    permission_classes = [IsAccountingStaff]
    serializer_class = BalanceSheetSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['period', 'year']
    search_fields = ['description']
    ordering_fields = ['period', 'year', 'total_assets']
    
    def get_queryset(self):
        return self.request.user.company.balance_sheets.all()
    
    @action(detail=True, methods=['get'])
    def generate_report(self, request, pk=None):
        """Bilanço raporu oluşturur."""
        balance_sheet = self.get_object()
        # Rapor oluşturma mantığı burada implement edilecek
        return Response({
            'status': 'report generated',
            'report_url': f'/api/accounting/balance-sheets/{balance_sheet.id}/report/'
        }) 