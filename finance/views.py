"""
Finance Modülü - View Sınıfları
---------------------
Bu dosya, Finance modülünün view sınıflarını içerir.
"""

from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Avg, Count
from django.utils import timezone
from datetime import timedelta
from .models import Transaction, Budget
from .serializers import TransactionSerializer, BudgetSerializer

class TransactionViewSet(viewsets.ModelViewSet):
    """
    Finansal işlemler için viewset.
    """
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        Kullanıcının finansal özetini döndürür.
        """
        user = request.user
        today = timezone.now().date()
        
        # Son 30 günlük işlemler
        last_30_days = today - timedelta(days=30)
        transactions = self.get_queryset().filter(
            date__gte=last_30_days
        )
        
        # Toplam gelir ve gider
        total_income = transactions.filter(
            type='income'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        total_expense = transactions.filter(
            type='expense'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Kategori bazlı harcamalar
        category_expenses = transactions.filter(
            type='expense'
        ).values('category').annotate(
            total=Sum('amount')
        ).order_by('-total')
        
        return Response({
            'total_income': total_income,
            'total_expense': total_expense,
            'balance': total_income - total_expense,
            'category_expenses': category_expenses
        })

class BudgetViewSet(viewsets.ModelViewSet):
    """
    Bütçe yönetimi için viewset.
    """
    queryset = Budget.objects.all()
    serializer_class = BudgetSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def overview(self, request):
        """
        Bütçe genel görünümünü döndürür.
        """
        user = request.user
        budgets = self.get_queryset()
        
        # Bütçe kullanım oranları
        budget_usage = []
        for budget in budgets:
            spent = budget.transactions.filter(
                type='expense'
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            usage_percentage = (spent / budget.amount) * 100 if budget.amount > 0 else 0
            
            budget_usage.append({
                'category': budget.category,
                'amount': budget.amount,
                'spent': spent,
                'remaining': budget.amount - spent,
                'usage_percentage': usage_percentage
            })
        
        return Response({
            'budgets': budget_usage
        }) 