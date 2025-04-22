from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import CashFlow, IncomeStatement, Account, Transaction, Budget, FinancialReport, Tax
from .serializers import (
    AccountSerializer, TransactionSerializer,
    BudgetSerializer, FinancialReportSerializer,
    TaxSerializer
)
from .permissions import (
    CanManageAccounts, CanManageTransactions,
    CanManageBudgets, CanManageReports,
    CanManageTaxes
)
from .filters import (
    AccountFilter, TransactionFilter,
    BudgetFilter, FinancialReportFilter,
    TaxFilter
)
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils.translation import gettext_lazy as _
from django.db.models import Sum, F, Q
from django.utils import timezone

# CashFlow Views
class CashFlowListView(ListView):
    model = CashFlow
    template_name = 'finance/cashflow_list.html'
    context_object_name = 'cashflows'

class CashFlowDetailView(DetailView):
    model = CashFlow
    template_name = 'finance/cashflow_detail.html'
    context_object_name = 'cashflow'

class CashFlowCreateView(CreateView):
    model = CashFlow
    template_name = 'finance/cashflow_form.html'
    fields = ['date', 'description', 'amount', 'flow_type', 'category']
    success_url = reverse_lazy('finance:cashflow_list')

class CashFlowUpdateView(UpdateView):
    model = CashFlow
    template_name = 'finance/cashflow_form.html'
    fields = ['date', 'description', 'amount', 'flow_type', 'category']
    success_url = reverse_lazy('finance:cashflow_list')

class CashFlowDeleteView(DeleteView):
    model = CashFlow
    template_name = 'finance/cashflow_confirm_delete.html'
    success_url = reverse_lazy('finance:cashflow_list')

# IncomeStatement Views
class IncomeStatementListView(ListView):
    model = IncomeStatement
    template_name = 'finance/incomestatement_list.html'
    context_object_name = 'statements'

class IncomeStatementDetailView(DetailView):
    model = IncomeStatement
    template_name = 'finance/incomestatement_detail.html'
    context_object_name = 'statement'

class IncomeStatementCreateView(CreateView):
    model = IncomeStatement
    template_name = 'finance/incomestatement_form.html'
    fields = ['period_start', 'period_end', 'revenue', 'expenses', 'net_income']
    success_url = reverse_lazy('finance:incomestatement_list')

class IncomeStatementUpdateView(UpdateView):
    model = IncomeStatement
    template_name = 'finance/incomestatement_form.html'
    fields = ['period_start', 'period_end', 'revenue', 'expenses', 'net_income']
    success_url = reverse_lazy('finance:incomestatement_list')

class IncomeStatementDeleteView(DeleteView):
    model = IncomeStatement
    template_name = 'finance/incomestatement_confirm_delete.html'
    success_url = reverse_lazy('finance:incomestatement_list')

class AccountViewSet(viewsets.ModelViewSet):
    """Hesap yönetimi"""
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticated, CanManageAccounts]
    filterset_class = AccountFilter
    
    @action(detail=True, methods=['get'])
    def balance_history(self, request, pk=None):
        """Hesap bakiyesi geçmişi"""
        account = self.get_object()
        transactions = Transaction.objects.filter(
            account=account,
            status='POSTED'
        ).order_by('date')
        
        balance = 0
        history = []
        for transaction in transactions:
            if transaction.type == 'DEBIT':
                balance += transaction.amount
            else:
                balance -= transaction.amount
            history.append({
                'date': transaction.date,
                'amount': transaction.amount,
                'type': transaction.type,
                'balance': balance
            })
        
        return Response(history)

class TransactionViewSet(viewsets.ModelViewSet):
    """İşlem yönetimi"""
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated, CanManageTransactions]
    filterset_class = TransactionFilter
    
    @action(detail=True, methods=['post'])
    def post(self, request, pk=None):
        """İşlemi kaydet"""
        transaction = self.get_object()
        if transaction.status != 'DRAFT':
            return Response(
                {'error': _('Sadece taslak durumundaki işlemler kaydedilebilir')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        transaction.status = 'POSTED'
        transaction.save()
        
        # Hesap bakiyesini güncelle
        account = transaction.account
        if transaction.type == 'DEBIT':
            account.balance += transaction.amount
        else:
            account.balance -= transaction.amount
        account.save()
        
        return Response({'status': 'success'})
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """İşlemi iptal et"""
        transaction = self.get_object()
        if transaction.status != 'POSTED':
            return Response(
                {'error': _('Sadece kaydedilmiş işlemler iptal edilebilir')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        transaction.status = 'CANCELLED'
        transaction.save()
        
        # Hesap bakiyesini güncelle
        account = transaction.account
        if transaction.type == 'DEBIT':
            account.balance -= transaction.amount
        else:
            account.balance += transaction.amount
        account.save()
        
        return Response({'status': 'success'})

class BudgetViewSet(viewsets.ModelViewSet):
    """Bütçe yönetimi"""
    queryset = Budget.objects.all()
    serializer_class = BudgetSerializer
    permission_classes = [IsAuthenticated, CanManageBudgets]
    filterset_class = BudgetFilter
    
    @action(detail=True, methods=['get'])
    def actual_vs_budget(self, request, pk=None):
        """Bütçe vs gerçekleşen analizi"""
        budget = self.get_object()
        transactions = Transaction.objects.filter(
            date__range=[budget.start_date, budget.end_date],
            status='POSTED'
        ).aggregate(
            total=Sum('amount', filter=Q(type='DEBIT'))
        )
        
        actual_amount = transactions['total'] or 0
        variance = actual_amount - budget.amount
        variance_percentage = (variance / budget.amount * 100) if budget.amount else 0
        
        return Response({
            'budget': budget.amount,
            'actual': actual_amount,
            'variance': variance,
            'variance_percentage': variance_percentage
        })

class FinancialReportViewSet(viewsets.ModelViewSet):
    """Finansal rapor yönetimi"""
    queryset = FinancialReport.objects.all()
    serializer_class = FinancialReportSerializer
    permission_classes = [IsAuthenticated, CanManageReports]
    filterset_class = FinancialReportFilter
    
    @action(detail=True, methods=['post'])
    def generate(self, request, pk=None):
        """Rapor oluştur"""
        report = self.get_object()
        if report.status != 'DRAFT':
            return Response(
                {'error': _('Sadece taslak durumundaki raporlar oluşturulabilir')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Rapor tipine göre veri topla
        data = {}
        if report.type == 'BALANCE_SHEET':
            data = self._generate_balance_sheet(report)
        elif report.type == 'INCOME_STATEMENT':
            data = self._generate_income_statement(report)
        elif report.type == 'CASH_FLOW':
            data = self._generate_cash_flow(report)
        elif report.type == 'BUDGET_VS_ACTUAL':
            data = self._generate_budget_vs_actual(report)
        
        report.parameters = data
        report.status = 'GENERATED'
        report.save()
        
        return Response(data)
    
    def _generate_balance_sheet(self, report):
        """Bilanço oluştur"""
        accounts = Account.objects.filter(
            type__in=['ASSET', 'LIABILITY', 'EQUITY']
        ).values('type', 'code', 'name').annotate(
            balance=Sum('balance')
        )
        
        return {
            'assets': accounts.filter(type='ASSET'),
            'liabilities': accounts.filter(type='LIABILITY'),
            'equity': accounts.filter(type='EQUITY')
        }
    
    def _generate_income_statement(self, report):
        """Gelir tablosu oluştur"""
        transactions = Transaction.objects.filter(
            date__range=[report.start_date, report.end_date],
            status='POSTED'
        ).values('account__type').annotate(
            total=Sum('amount', filter=Q(type='DEBIT'))
        )
        
        return {
            'revenue': transactions.filter(account__type='REVENUE'),
            'expenses': transactions.filter(account__type='EXPENSE')
        }
    
    def _generate_cash_flow(self, report):
        """Nakit akışı oluştur"""
        transactions = Transaction.objects.filter(
            date__range=[report.start_date, report.end_date],
            status='POSTED'
        ).values('date').annotate(
            inflow=Sum('amount', filter=Q(type='DEBIT')),
            outflow=Sum('amount', filter=Q(type='CREDIT'))
        ).order_by('date')
        
        return {
            'transactions': transactions,
            'total_inflow': sum(t['inflow'] or 0 for t in transactions),
            'total_outflow': sum(t['outflow'] or 0 for t in transactions)
        }
    
    def _generate_budget_vs_actual(self, report):
        """Bütçe vs gerçekleşen raporu oluştur"""
        budgets = Budget.objects.filter(
            start_date__lte=report.end_date,
            end_date__gte=report.start_date
        )
        
        return [{
            'budget': budget,
            'actual': Transaction.objects.filter(
                date__range=[budget.start_date, budget.end_date],
                status='POSTED'
            ).aggregate(
                total=Sum('amount', filter=Q(type='DEBIT'))
            )['total'] or 0
        } for budget in budgets]

class TaxViewSet(viewsets.ModelViewSet):
    """Vergi yönetimi"""
    queryset = Tax.objects.all()
    serializer_class = TaxSerializer
    permission_classes = [IsAuthenticated, CanManageTaxes]
    filterset_class = TaxFilter
    
    @action(detail=True, methods=['get'])
    def calculate(self, request, pk=None):
        """Vergi hesapla"""
        tax = self.get_object()
        amount = float(request.query_params.get('amount', 0))
        
        if tax.type == 'VAT':
            tax_amount = amount * (tax.rate / 100)
            total = amount + tax_amount
        else:
            tax_amount = amount * (tax.rate / 100)
            total = amount
        
        return Response({
            'amount': amount,
            'tax_rate': tax.rate,
            'tax_amount': tax_amount,
            'total': total
        }) 