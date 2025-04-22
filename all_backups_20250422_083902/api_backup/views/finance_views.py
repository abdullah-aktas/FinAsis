"""
Finans işlemleri API görünümleri
"""
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from django.db.models import Sum, Count, Q
from django.utils.translation import gettext_lazy as _
from datetime import datetime, timedelta

from finance.models import EInvoice, Customer, Product, Transaction
from api.serializers.finance_serializers import (
    EInvoiceSerializer,
    CustomerSerializer,
    ProductSerializer,
)

class EInvoiceViewSet(viewsets.ModelViewSet):
    """E-Fatura API görünümü"""
    queryset = EInvoice.objects.all()
    serializer_class = EInvoiceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Kullanıcının kendi faturalarını filtrele"""
        return EInvoice.objects.filter(created_by=self.request.user)
    
    def perform_create(self, serializer):
        """Oluşturulacak faturaya kullanıcıyı ekle"""
        serializer.save(created_by=self.request.user, updated_by=self.request.user)
    
    def perform_update(self, serializer):
        """Güncellenecek faturanın güncelleyen kullanıcısını ekle"""
        serializer.save(updated_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def send(self, request, pk=None):
        """Faturayı gönder"""
        einvoice = self.get_object()
        
        if einvoice.status != 'draft':
            return Response(
                {'detail': _('Sadece taslak durumundaki faturalar gönderilebilir.')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Burada E-Fatura gönderme işlemi gerçekleştirilecek
        
        einvoice.status = 'sent'
        einvoice.sent_date = datetime.now()
        einvoice.save()
        
        return Response({'status': 'success', 'message': _('Fatura başarıyla gönderildi.')})
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """E-Fatura özeti"""
        queryset = self.get_queryset()
        
        total_count = queryset.count()
        draft_count = queryset.filter(status='draft').count()
        sent_count = queryset.filter(status='sent').count()
        paid_count = queryset.filter(status='paid').count()
        
        total_amount = queryset.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        
        return Response({
            'total_count': total_count,
            'draft_count': draft_count,
            'sent_count': sent_count,
            'paid_count': paid_count,
            'total_amount': total_amount,
        })

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def einvoice_summary(request):
    """E-Fatura özet görünümü"""
    einvoices = EInvoice.objects.filter(created_by=request.user)
    
    # Fatura istatistikleri
    total_count = einvoices.count()
    draft_count = einvoices.filter(status='draft').count()
    sent_count = einvoices.filter(status='sent').count()
    paid_count = einvoices.filter(status='paid').count()
    
    # Toplam tutarlar
    total_amount = einvoices.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    unpaid_amount = einvoices.filter(status__in=['sent', 'overdue']).aggregate(
        Sum('total_amount')
    )['total_amount__sum'] or 0
    
    # Son faturaları getir
    recent_einvoices = einvoices.order_by('-issue_date')[:5]
    serializer = EInvoiceSerializer(recent_einvoices, many=True)
    
    return Response({
        'total_count': total_count,
        'draft_count': draft_count,
        'sent_count': sent_count,
        'paid_count': paid_count,
        'total_amount': total_amount,
        'unpaid_amount': unpaid_amount,
        'recent_einvoices': serializer.data,
    })

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def monthly_transactions_report(request):
    """Aylık işlem raporu"""
    # Son 6 ay için tarih aralığı
    end_date = datetime.now().date()
    start_date = (end_date - timedelta(days=180))
    
    # İşlemleri getir
    transactions = Transaction.objects.filter(
        Q(source_account__user=request.user) | Q(destination_account__user=request.user),
        date__gte=start_date,
        date__lte=end_date
    )
    
    # Aylık verileri grupla
    months = {}
    for transaction in transactions:
        month_key = transaction.date.strftime('%Y-%m')
        if month_key not in months:
            months[month_key] = {
                'income': 0,
                'expense': 0,
                'transfer': 0,
                'count': 0
            }
        
        months[month_key]['count'] += 1
        
        if transaction.transaction_type == 'income':
            months[month_key]['income'] += transaction.amount
        elif transaction.transaction_type == 'expense':
            months[month_key]['expense'] += transaction.amount
        elif transaction.transaction_type == 'transfer':
            months[month_key]['transfer'] += transaction.amount
    
    # Sonuçları sırala
    result = []
    for month, data in sorted(months.items()):
        result.append({
            'month': month,
            'income': data['income'],
            'expense': data['expense'],
            'transfer': data['transfer'],
            'count': data['count'],
            'balance': data['income'] - data['expense']
        })
    
    return Response(result)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def financial_summary_report(request):
    """Finansal özet raporu"""
    # Banka hesapları
    bank_accounts = request.user.bankaccount_set.all()
    total_balance = bank_accounts.aggregate(Sum('balance'))['balance__sum'] or 0
    
    # Faturalar
    einvoices = EInvoice.objects.filter(created_by=request.user)
    total_invoice_amount = einvoices.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    unpaid_invoice_amount = einvoices.filter(status__in=['sent', 'overdue']).aggregate(
        Sum('total_amount')
    )['total_amount__sum'] or 0
    
    # İşlemler
    transactions = Transaction.objects.filter(
        Q(source_account__user=request.user) | Q(destination_account__user=request.user)
    )
    
    # Son 30 gün içindeki işlemler
    thirty_days_ago = datetime.now().date() - timedelta(days=30)
    recent_transactions = transactions.filter(date__gte=thirty_days_ago)
    
    income_30d = recent_transactions.filter(
        transaction_type='income'
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    expense_30d = recent_transactions.filter(
        transaction_type='expense'
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    return Response({
        'bank_summary': {
            'account_count': bank_accounts.count(),
            'total_balance': total_balance,
        },
        'invoice_summary': {
            'invoice_count': einvoices.count(),
            'total_amount': total_invoice_amount,
            'unpaid_amount': unpaid_invoice_amount,
        },
        'transaction_summary': {
            'last_30_days': {
                'income': income_30d,
                'expense': expense_30d,
                'net': income_30d - expense_30d
            }
        }
    }) 