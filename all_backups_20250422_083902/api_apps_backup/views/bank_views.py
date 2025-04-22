"""
Banka işlemleri API görünümleri
"""
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from django.db.models import Sum, Q
from django.utils.translation import gettext_lazy as _

from finance.models import BankAccount, Transaction
from api.serializers.bank_serializers import (
    BankAccountSerializer, 
    TransactionSerializer,
)

class BankAccountViewSet(viewsets.ModelViewSet):
    """Banka hesapları API görünümü"""
    queryset = BankAccount.objects.all()
    serializer_class = BankAccountSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Kullanıcının kendi banka hesaplarını filtrele"""
        return BankAccount.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Oluşturulacak banka hesabına kullanıcıyı ekle"""
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Banka hesapları özeti"""
        accounts = self.get_queryset()
        total_balance = accounts.aggregate(Sum('balance'))['balance__sum'] or 0
        
        by_currency = {}
        for account in accounts:
            currency = account.currency
            if currency not in by_currency:
                by_currency[currency] = 0
            by_currency[currency] += account.balance
        
        return Response({
            'total_accounts': accounts.count(),
            'total_balance': total_balance,
            'by_currency': by_currency,
        })

class TransactionViewSet(viewsets.ModelViewSet):
    """İşlemler API görünümü"""
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Kullanıcının kendi işlemlerini filtrele"""
        return Transaction.objects.filter(
            Q(source_account__user=self.request.user) | 
            Q(destination_account__user=self.request.user)
        )
    
    def perform_create(self, serializer):
        """İşlem oluştururken kullanıcı hesaplarını kontrol et"""
        source_account = serializer.validated_data.get('source_account')
        if source_account and source_account.user != self.request.user:
            raise serializers.ValidationError(
                {'source_account': _('Bu hesap sizin değil.')}
            )
        
        destination_account = serializer.validated_data.get('destination_account')
        if destination_account and destination_account.user != self.request.user:
            raise serializers.ValidationError(
                {'destination_account': _('Bu hesap sizin değil.')}
            )
        
        serializer.save()
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Son işlemleri getir"""
        transactions = self.get_queryset().order_by('-date')[:10]
        serializer = self.get_serializer(transactions, many=True)
        return Response(serializer.data)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def bank_summary(request):
    """Banka hesapları genel özeti API görünümü"""
    accounts = BankAccount.objects.filter(user=request.user)
    total_balance = accounts.aggregate(Sum('balance'))['balance__sum'] or 0
    
    # Son işlemler
    recent_transactions = Transaction.objects.filter(
        Q(source_account__user=request.user) | 
        Q(destination_account__user=request.user)
    ).order_by('-date')[:5]
    
    transaction_serializer = TransactionSerializer(recent_transactions, many=True)
    account_serializer = BankAccountSerializer(accounts, many=True)
    
    return Response({
        'accounts': account_serializer.data,
        'total_balance': total_balance,
        'recent_transactions': transaction_serializer.data,
    }) 