# -*- coding: utf-8 -*-
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.urls import reverse_lazy
from .models import (
    CashFlow,
    IncomeStatement,
    Account,
    Transaction,
    Budget,
    FinancialReport,
    Tax,
    BankAccount,
    Invoice,
    EInvoice,
    EInvoiceItem,
    Employee,
    Voucher,
    AIConfig,
)
from .serializers import (
    TransactionSerializer,
    BudgetSerializer,
    AccountSerializer,
    FinancialReportSerializer,
    TaxSerializer,
)
from .permissions import (
    CanManageAccounts,
    CanManageTransactions,
    CanManageBudgets,
    CanManageReports,
    CanManageTaxes,
)
from .filters import (
    AccountFilter,
    TransactionFilter,
    BudgetFilter,
    FinancialReportFilter,
    TaxFilter,
)
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils.translation import gettext_lazy as _
from django.db.models import Sum, Q
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .forms import (
    TransactionForm,
    AccountForm,
    BudgetForm,
    TaxForm,
    CashFlowForm,
    IncomeStatementForm,
    BankAccountForm,
    InvoiceForm,
    FinancialReportForm,
    EInvoiceForm,
    EInvoiceItemForm,
    EmployeeForm,
    VoucherForm,
)
from django.shortcuts import render

try:
    import openai  # type: ignore
except Exception:
    openai = None
from django.template.loader import render_to_string
from django.http import HttpResponse

try:
    from weasyprint import HTML
except (ImportError, OSError):
    HTML = None
from rest_framework.permissions import IsAuthenticated


# CashFlow Views
@method_decorator(login_required, name="dispatch")
class CashFlowListView(ListView):
    model = CashFlow
    template_name = "finance/cashflow_list.html"
    context_object_name = "cashflows"


@method_decorator(login_required, name="dispatch")
class CashFlowDetailView(DetailView):
    model = CashFlow
    template_name = "finance/cashflow_detail.html"
    context_object_name = "cashflow"


@method_decorator(login_required, name="dispatch")
class CashFlowCreateView(CreateView):
    model = CashFlow
    form_class = CashFlowForm
    template_name = "finance/cashflow_form.html"
    success_url = reverse_lazy("finance:cash_flow_list")


@method_decorator(login_required, name="dispatch")
class CashFlowUpdateView(UpdateView):
    model = CashFlow
    form_class = CashFlowForm
    template_name = "finance/cashflow_form.html"
    success_url = reverse_lazy("finance:cash_flow_list")


@method_decorator(login_required, name="dispatch")
class CashFlowDeleteView(DeleteView):
    model = CashFlow
    template_name = "finance/cashflow_confirm_delete.html"
    success_url = reverse_lazy("finance:cash_flow_list")


# IncomeStatement Views
@method_decorator(login_required, name="dispatch")
class IncomeStatementListView(ListView):
    model = IncomeStatement
    template_name = "finance/incomestatement_list.html"
    context_object_name = "statements"


@method_decorator(login_required, name="dispatch")
class IncomeStatementDetailView(DetailView):
    model = IncomeStatement
    template_name = "finance/incomestatement_detail.html"
    context_object_name = "statement"


@method_decorator(login_required, name="dispatch")
class IncomeStatementCreateView(CreateView):
    model = IncomeStatement
    form_class = IncomeStatementForm
    template_name = "finance/incomestatement_form.html"
    success_url = reverse_lazy("finance:income_statement_list")


@method_decorator(login_required, name="dispatch")
class IncomeStatementUpdateView(UpdateView):
    model = IncomeStatement
    form_class = IncomeStatementForm
    template_name = "finance/incomestatement_form.html"
    success_url = reverse_lazy("finance:income_statement_list")


@method_decorator(login_required, name="dispatch")
class IncomeStatementDeleteView(DeleteView):
    model = IncomeStatement
    template_name = "finance/incomestatement_confirm_delete.html"
    success_url = reverse_lazy("finance:income_statement_list")


class AccountViewSet(viewsets.ModelViewSet):
    """Hesap yönetimi"""

    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticated, CanManageAccounts]
    filterset_class = AccountFilter

    @action(detail=True, methods=["get"])
    def balance_history(self, request, pk=None):
        """Hesap bakiyesi geçmişi"""
        account = self.get_object()
        transactions = Transaction.objects.filter(
            account=account, status="POSTED"
        ).order_by("date")

        balance = 0
        history = []
        for transaction in transactions:
            if transaction.type == "DEBIT":
                balance += transaction.amount
            else:
                balance -= transaction.amount
            history.append(
                {
                    "date": transaction.date,
                    "amount": transaction.amount,
                    "type": transaction.type,
                    "balance": balance,
                }
            )

        return Response(history)


class TransactionViewSet(viewsets.ModelViewSet):
    """İşlem yönetimi"""

    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated, CanManageTransactions]
    filterset_class = TransactionFilter

    @action(detail=True, methods=["post"])
    def post(self, request, pk=None):
        """İşlemi kaydet"""
        transaction = self.get_object()
        if transaction.status != "DRAFT":
            return Response(
                {"error": _("Sadece taslak durumundaki işlemler kaydedilebilir")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        transaction.status = "POSTED"
        transaction.save()

        # Hesap bakiyesini güncelle
        account = transaction.account
        if transaction.type == "DEBIT":
            account.balance += transaction.amount
        else:
            account.balance -= transaction.amount
        account.save()

        return Response({"status": "success"})

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        """İşlemi iptal et"""
        transaction = self.get_object()
        if transaction.status != "POSTED":
            return Response(
                {"error": _("Sadece kaydedilmiş işlemler iptal edilebilir")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        transaction.status = "CANCELLED"
        transaction.save()

        # Hesap bakiyesini güncelle
        account = transaction.account
        if transaction.type == "DEBIT":
            account.balance -= transaction.amount
        else:
            account.balance += transaction.amount
        account.save()

        return Response({"status": "success"})


class BudgetViewSet(viewsets.ModelViewSet):
    """Bütçe yönetimi"""

    queryset = Budget.objects.all()
    serializer_class = BudgetSerializer
    permission_classes = [IsAuthenticated, CanManageBudgets]
    filterset_class = BudgetFilter

    @action(detail=True, methods=["get"])
    def actual_vs_budget(self, request, pk=None):
        """Bütçe vs gerçekleşen analizi"""
        budget = self.get_object()
        transactions = Transaction.objects.filter(
            date__range=[budget.start_date, budget.end_date], status="POSTED"
        ).aggregate(total=Sum("amount", filter=Q(type="DEBIT")))

        actual_amount = transactions["total"] or 0
        variance = actual_amount - budget.amount
        variance_percentage = (variance / budget.amount * 100) if budget.amount else 0

        return Response(
            {
                "budget": budget.amount,
                "actual": actual_amount,
                "variance": variance,
                "variance_percentage": variance_percentage,
            }
        )


class FinancialReportViewSet(viewsets.ModelViewSet):
    """Finansal rapor yönetimi"""

    queryset = FinancialReport.objects.all()
    serializer_class = FinancialReportSerializer
    permission_classes = [IsAuthenticated, CanManageReports]
    filterset_class = FinancialReportFilter

    @action(detail=True, methods=["post"])
    def generate(self, request, pk=None):
        """Rapor oluştur"""
        report = self.get_object()
        if report.status != "DRAFT":
            return Response(
                {"error": _("Sadece taslak durumundaki raporlar oluşturulabilir")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Rapor tipine göre veri topla
        data = {}
        if report.type == "BALANCE_SHEET":
            data = self._generate_balance_sheet(report)
        elif report.type == "INCOME_STATEMENT":
            data = self._generate_income_statement(report)
        elif report.type == "CASH_FLOW":
            data = self._generate_cash_flow(report)
        elif report.type == "BUDGET_VS_ACTUAL":
            data = self._generate_budget_vs_actual(report)

        report.parameters = data
        report.status = "GENERATED"
        report.save()

        return Response(data)

    def _generate_balance_sheet(self, report):
        """Bilanço oluştur"""
        accounts = (
            Account.objects.filter(type__in=["ASSET", "LIABILITY", "EQUITY"])
            .values("type", "code", "name")
            .annotate(balance=Sum("balance"))
        )

        return {
            "assets": accounts.filter(type="ASSET"),
            "liabilities": accounts.filter(type="LIABILITY"),
            "equity": accounts.filter(type="EQUITY"),
        }

    def _generate_income_statement(self, report):
        """Gelir tablosu oluştur"""
        transactions = (
            Transaction.objects.filter(
                date__range=[report.start_date, report.end_date], status="POSTED"
            )
            .values("account__type")
            .annotate(total=Sum("amount", filter=Q(type="DEBIT")))
        )

        return {
            "revenue": transactions.filter(account__type="REVENUE"),
            "expenses": transactions.filter(account__type="EXPENSE"),
        }

    def _generate_cash_flow(self, report):
        """Nakit akışı oluştur"""
        transactions = (
            Transaction.objects.filter(
                date__range=[report.start_date, report.end_date], status="POSTED"
            )
            .values("date")
            .annotate(
                inflow=Sum("amount", filter=Q(type="DEBIT")),
                outflow=Sum("amount", filter=Q(type="CREDIT")),
            )
            .order_by("date")
        )

        return {
            "transactions": transactions,
            "total_inflow": sum(t["inflow"] or 0 for t in transactions),
            "total_outflow": sum(t["outflow"] or 0 for t in transactions),
        }

    def _generate_budget_vs_actual(self, report):
        """Bütçe vs gerçekleşen raporu oluştur"""
        budgets = Budget.objects.filter(
            start_date__lte=report.end_date, end_date__gte=report.start_date
        )

        return [
            {
                "budget": budget,
                "actual": Transaction.objects.filter(
                    date__range=[budget.start_date, budget.end_date], status="POSTED"
                ).aggregate(total=Sum("amount", filter=Q(type="DEBIT")))["total"]
                or 0,
            }
            for budget in budgets
        ]


class TaxViewSet(viewsets.ModelViewSet):
    """Vergi yönetimi"""

    queryset = Tax.objects.all()
    serializer_class = TaxSerializer
    permission_classes = [IsAuthenticated, CanManageTaxes]
    filterset_class = TaxFilter

    @action(detail=True, methods=["get"])
    def calculate(self, request, pk=None):
        """Vergi hesapla"""
        tax = self.get_object()
        amount = float(request.query_params.get("amount", 0))

        if tax.type == "VAT":
            tax_amount = amount * (tax.rate / 100)
            total = amount + tax_amount
        else:
            tax_amount = amount * (tax.rate / 100)
            total = amount

        return Response(
            {
                "amount": amount,
                "tax_rate": tax.rate,
                "tax_amount": tax_amount,
                "total": total,
            }
        )


@method_decorator(login_required, name="dispatch")
class TransactionListView(ListView):
    model = Transaction
    template_name = "finance/transaction_list.html"
    context_object_name = "transactions"


@method_decorator(login_required, name="dispatch")
class TransactionDetailView(DetailView):
    model = Transaction
    template_name = "finance/transaction_detail.html"
    context_object_name = "transaction"


@method_decorator(login_required, name="dispatch")
class TransactionCreateView(CreateView):
    model = Transaction
    form_class = TransactionForm
    template_name = "finance/transaction_form.html"
    success_url = reverse_lazy("finance:transaction_list")


@method_decorator(login_required, name="dispatch")
class TransactionUpdateView(UpdateView):
    model = Transaction
    form_class = TransactionForm
    template_name = "finance/transaction_form.html"
    success_url = reverse_lazy("finance:transaction_list")


@method_decorator(login_required, name="dispatch")
class TransactionDeleteView(DeleteView):
    model = Transaction
    template_name = "finance/transaction_confirm_delete.html"
    success_url = reverse_lazy("finance:transaction_list")


@method_decorator(login_required, name="dispatch")
class AccountListView(ListView):
    model = Account
    template_name = "finance/account_list.html"
    context_object_name = "accounts"


@method_decorator(login_required, name="dispatch")
class AccountDetailView(DetailView):
    model = Account
    template_name = "finance/account_detail.html"
    context_object_name = "account"


@method_decorator(login_required, name="dispatch")
class AccountCreateView(CreateView):
    model = Account
    form_class = AccountForm
    template_name = "finance/account_form.html"
    success_url = reverse_lazy("finance:account_list")


@method_decorator(login_required, name="dispatch")
class AccountUpdateView(UpdateView):
    model = Account
    form_class = AccountForm
    template_name = "finance/account_form.html"
    success_url = reverse_lazy("finance:account_list")


@method_decorator(login_required, name="dispatch")
class AccountDeleteView(DeleteView):
    model = Account
    template_name = "finance/account_confirm_delete.html"
    success_url = reverse_lazy("finance:account_list")


@method_decorator(login_required, name="dispatch")
class BudgetListView(ListView):
    model = Budget
    template_name = "finance/budget_list.html"
    context_object_name = "budgets"


@method_decorator(login_required, name="dispatch")
class BudgetDetailView(DetailView):
    model = Budget
    template_name = "finance/budget_detail.html"
    context_object_name = "budget"


@method_decorator(login_required, name="dispatch")
class BudgetCreateView(CreateView):
    model = Budget
    form_class = BudgetForm
    template_name = "finance/budget_form.html"
    success_url = reverse_lazy("finance:budget_list")


@method_decorator(login_required, name="dispatch")
class BudgetUpdateView(UpdateView):
    model = Budget
    form_class = BudgetForm
    template_name = "finance/budget_form.html"
    success_url = reverse_lazy("finance:budget_list")


@method_decorator(login_required, name="dispatch")
class BudgetDeleteView(DeleteView):
    model = Budget
    template_name = "finance/budget_confirm_delete.html"
    success_url = reverse_lazy("finance:budget_list")


@method_decorator(login_required, name="dispatch")
class TaxListView(ListView):
    model = Tax
    template_name = "finance/tax_list.html"
    context_object_name = "taxes"


@method_decorator(login_required, name="dispatch")
class TaxDetailView(DetailView):
    model = Tax
    template_name = "finance/tax_detail.html"
    context_object_name = "tax"


@method_decorator(login_required, name="dispatch")
class TaxCreateView(CreateView):
    model = Tax
    form_class = TaxForm
    template_name = "finance/tax_form.html"
    success_url = reverse_lazy("finance:tax_list")


@method_decorator(login_required, name="dispatch")
class TaxUpdateView(UpdateView):
    model = Tax
    form_class = TaxForm
    template_name = "finance/tax_form.html"
    success_url = reverse_lazy("finance:tax_list")


@method_decorator(login_required, name="dispatch")
class TaxDeleteView(DeleteView):
    model = Tax
    template_name = "finance/tax_confirm_delete.html"
    success_url = reverse_lazy("finance:tax_list")


@method_decorator(login_required, name="dispatch")
class BankAccountListView(ListView):
    model = BankAccount
    template_name = "finance/bankaccount_list.html"
    context_object_name = "bankaccounts"


@method_decorator(login_required, name="dispatch")
class BankAccountDetailView(DetailView):
    model = BankAccount
    template_name = "finance/bankaccount_detail.html"
    context_object_name = "bankaccount"


@method_decorator(login_required, name="dispatch")
class BankAccountCreateView(CreateView):
    model = BankAccount
    form_class = BankAccountForm
    template_name = "finance/bankaccount_form.html"
    success_url = reverse_lazy("finance:bank_account_list")


@method_decorator(login_required, name="dispatch")
class BankAccountUpdateView(UpdateView):
    model = BankAccount
    form_class = BankAccountForm
    template_name = "finance/bankaccount_form.html"
    success_url = reverse_lazy("finance:bank_account_list")


@method_decorator(login_required, name="dispatch")
class BankAccountDeleteView(DeleteView):
    model = BankAccount
    template_name = "finance/bankaccount_confirm_delete.html"
    success_url = reverse_lazy("finance:bank_account_list")


@method_decorator(login_required, name="dispatch")
class InvoiceListView(ListView):
    model = Invoice
    template_name = "finance/invoice_list.html"
    context_object_name = "invoices"


@method_decorator(login_required, name="dispatch")
class InvoiceDetailView(DetailView):
    model = Invoice
    template_name = "finance/invoice_detail.html"
    context_object_name = "invoice"


@method_decorator(login_required, name="dispatch")
class InvoiceCreateView(CreateView):
    model = Invoice
    form_class = InvoiceForm
    template_name = "finance/invoice_form.html"
    success_url = reverse_lazy("finance:invoice_list")


@method_decorator(login_required, name="dispatch")
class InvoiceUpdateView(UpdateView):
    model = Invoice
    form_class = InvoiceForm
    template_name = "finance/invoice_form.html"
    success_url = reverse_lazy("finance:invoice_list")


@method_decorator(login_required, name="dispatch")
class InvoiceDeleteView(DeleteView):
    model = Invoice
    template_name = "finance/invoice_confirm_delete.html"
    success_url = reverse_lazy("finance:invoice_list")


@method_decorator(login_required, name="dispatch")
class FinancialReportListView(ListView):
    model = FinancialReport
    template_name = "finance/financialreport_list.html"
    context_object_name = "reports"


@method_decorator(login_required, name="dispatch")
class FinancialReportDetailView(DetailView):
    model = FinancialReport
    template_name = "finance/financialreport_detail.html"
    context_object_name = "report"


@method_decorator(login_required, name="dispatch")
class FinancialReportCreateView(CreateView):
    model = FinancialReport
    form_class = FinancialReportForm
    template_name = "finance/financialreport_form.html"
    success_url = reverse_lazy("finance:financial_report_list")


@method_decorator(login_required, name="dispatch")
class FinancialReportUpdateView(UpdateView):
    model = FinancialReport
    form_class = FinancialReportForm
    template_name = "finance/financialreport_form.html"
    success_url = reverse_lazy("finance:financial_report_list")


@method_decorator(login_required, name="dispatch")
class FinancialReportDeleteView(DeleteView):
    model = FinancialReport
    template_name = "finance/financialreport_confirm_delete.html"
    success_url = reverse_lazy("finance:financial_report_list")


@method_decorator(login_required, name="dispatch")
class EInvoiceListView(ListView):
    model = EInvoice
    template_name = "finance/einvoice_list.html"
    context_object_name = "einvoices"


@method_decorator(login_required, name="dispatch")
class EInvoiceDetailView(DetailView):
    model = EInvoice
    template_name = "finance/einvoice_detail.html"
    context_object_name = "einvoice"


@method_decorator(login_required, name="dispatch")
class EInvoiceCreateView(CreateView):
    model = EInvoice
    form_class = EInvoiceForm
    template_name = "finance/einvoice_form.html"
    success_url = reverse_lazy("finance:e_invoice_list")


@method_decorator(login_required, name="dispatch")
class EInvoiceUpdateView(UpdateView):
    model = EInvoice
    form_class = EInvoiceForm
    template_name = "finance/einvoice_form.html"
    success_url = reverse_lazy("finance:e_invoice_list")


@method_decorator(login_required, name="dispatch")
class EInvoiceDeleteView(DeleteView):
    model = EInvoice
    template_name = "finance/einvoice_confirm_delete.html"
    success_url = reverse_lazy("finance:e_invoice_list")


@method_decorator(login_required, name="dispatch")
class EInvoiceItemListView(ListView):
    model = EInvoiceItem
    template_name = "finance/einvoiceitem_list.html"
    context_object_name = "einvoiceitems"


@method_decorator(login_required, name="dispatch")
class EInvoiceItemDetailView(DetailView):
    model = EInvoiceItem
    template_name = "finance/einvoiceitem_detail.html"
    context_object_name = "einvoiceitem"


@method_decorator(login_required, name="dispatch")
class EInvoiceItemCreateView(CreateView):
    model = EInvoiceItem
    form_class = EInvoiceItemForm
    template_name = "finance/einvoiceitem_form.html"
    success_url = reverse_lazy("finance:e_invoice_item_list")


@method_decorator(login_required, name="dispatch")
class EInvoiceItemUpdateView(UpdateView):
    model = EInvoiceItem
    form_class = EInvoiceItemForm
    template_name = "finance/einvoiceitem_form.html"
    success_url = reverse_lazy("finance:e_invoice_item_list")


@method_decorator(login_required, name="dispatch")
class EInvoiceItemDeleteView(DeleteView):
    model = EInvoiceItem
    template_name = "finance/einvoiceitem_confirm_delete.html"
    success_url = reverse_lazy("finance:e_invoice_item_list")


@method_decorator(login_required, name="dispatch")
class EmployeeListView(ListView):
    model = Employee
    template_name = "finance/employee_list.html"
    context_object_name = "employees"


@method_decorator(login_required, name="dispatch")
class EmployeeDetailView(DetailView):
    model = Employee
    template_name = "finance/employee_detail.html"
    context_object_name = "employee"


@method_decorator(login_required, name="dispatch")
class EmployeeCreateView(CreateView):
    model = Employee
    form_class = EmployeeForm
    template_name = "finance/employee_form.html"
    success_url = reverse_lazy("finance:employee_list")


@method_decorator(login_required, name="dispatch")
class EmployeeUpdateView(UpdateView):
    model = Employee
    form_class = EmployeeForm
    template_name = "finance/employee_form.html"
    success_url = reverse_lazy("finance:employee_list")


@method_decorator(login_required, name="dispatch")
class EmployeeDeleteView(DeleteView):
    model = Employee
    template_name = "finance/employee_confirm_delete.html"
    success_url = reverse_lazy("finance:employee_list")


@method_decorator(login_required, name="dispatch")
class VoucherListView(ListView):
    model = Voucher
    template_name = "finance/voucher_list.html"
    context_object_name = "vouchers"


@method_decorator(login_required, name="dispatch")
class VoucherDetailView(DetailView):
    model = Voucher
    template_name = "finance/voucher_detail.html"
    context_object_name = "voucher"


@method_decorator(login_required, name="dispatch")
class VoucherCreateView(CreateView):
    model = Voucher
    form_class = VoucherForm
    template_name = "finance/voucher_form.html"
    success_url = reverse_lazy("finance:voucher_list")


@method_decorator(login_required, name="dispatch")
class VoucherUpdateView(UpdateView):
    model = Voucher
    form_class = VoucherForm
    template_name = "finance/voucher_form.html"
    success_url = reverse_lazy("finance:voucher_list")


@method_decorator(login_required, name="dispatch")
class VoucherDeleteView(DeleteView):
    model = Voucher
    template_name = "finance/voucher_confirm_delete.html"
    success_url = reverse_lazy("finance:voucher_list")


@login_required
def finance_dashboard(request):
    # Örnek: Son 6 ayın isimleri
    import calendar
    from datetime import date, timedelta

    today = date.today()
    months = [
        (today.replace(day=1) - timedelta(days=30 * i)).replace(day=1)
        for i in reversed(range(6))
    ]
    chart_labels = [calendar.month_name[m.month] for m in months]

    # Her ay için gelir ve gider hesapla
    chart_income = []
    chart_expense = []
    for m in months:
        month_start = m
        if m.month == 12:
            month_end = m.replace(year=m.year + 1, month=1)
        else:
            month_end = m.replace(month=m.month + 1)
        income = (
            Transaction.objects.filter(
                date__gte=month_start,
                date__lt=month_end,
                type="DEBIT",
                status="POSTED",
                account__user=request.user,
            ).aggregate(total=Sum("amount"))["total"]
            or 0
        )
        expense = (
            Transaction.objects.filter(
                date__gte=month_start,
                date__lt=month_end,
                type="CREDIT",
                status="POSTED",
                account__user=request.user,
            ).aggregate(total=Sum("amount"))["total"]
            or 0
        )
        chart_income.append(float(income))
        chart_expense.append(float(expense))

    # Son 5 finansal uyarı/bildirim
    # FinanceAlert modeli henüz tanımlı olmadığı için boş liste kullanıyoruz
    finance_alerts = []

    # 1. Fatura Geçmişi Analiz Grafiği
    from .models import Invoice

    invoice_labels = chart_labels
    invoice_amounts = []
    for m in months:
        month_start = m
        if m.month == 12:
            month_end = m.replace(year=m.year + 1, month=1)
        else:
            month_end = m.replace(month=m.month + 1)
        total = (
            Invoice.objects.filter(
                date__gte=month_start,
                date__lt=month_end,
                user=request.user,
                status="PAID",
            ).aggregate(total=Sum("amount"))["total"]
            or 0
        )
        invoice_amounts.append(float(total))

    # 2. Kredi Kartı Borç Takibi (örnek veri)
    credit_cards = [
        {
            "name": "Akbank Axess",
            "debt": 3200,
            "limit": 8000,
            "usage_percent": int(3200 / 8000 * 100),
        },
        {
            "name": "Yapı Kredi World",
            "debt": 1500,
            "limit": 6000,
            "usage_percent": int(1500 / 6000 * 100),
        },
    ]

    # 3. Yatırım Performansı (örnek veri)
    investment_labels = ["BIST", "USD", "BTC"]
    investment_returns = [1200, 800, 250]

    # 4. AI Destekli Finansal Öneri (örnek mantık)
    total_income = sum(chart_income)
    total_expense = sum(chart_expense)
    if total_expense > total_income:
        ai_advice = (
            "Giderleriniz gelirlerinizden fazla. Harcamaları kontrol etmenizi öneririz."
        )
    else:
        ai_advice = "Harika! Gelir-gider dengeniz olumlu görünüyor."

    context = {
        "chart_labels": chart_labels,
        "chart_income": chart_income,
        "chart_expense": chart_expense,
        "finance_alerts": finance_alerts,
        "invoice_labels": invoice_labels,
        "invoice_amounts": invoice_amounts,
        "credit_cards": credit_cards,
        "investment_labels": investment_labels,
        "investment_returns": investment_returns,
        "ai_advice": ai_advice,
    }
    return render(request, "finance/finance_dashboard.html", context)


def get_ai_financial_advice(user, total_income, total_expense, total_investment):
    # Aktif OpenAI API anahtarını al
    config = AIConfig.objects.filter(active=True).order_by("-created_at").first()
    if not config or not openai:
        return "AI öneri servisi yapılandırılmamış."

    try:
        # Yeni OpenAI client formatı
        client = openai.OpenAI(api_key=config.key)
        prompt = f"""
        Kullanıcının geliri: {total_income}₺\nGideri: {total_expense}₺\nYatırım tutarı: {total_investment}₺\nBu verilere göre kısa bir finansal öneri sun.
        """

        response = client.chat.completions.create(
            model="gpt-4", messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI öneri alınamadı: {e}"


@login_required
def download_financial_report(request):
    # Panelde kullanılan context ile aynı veriler
    # (Varsa) paneldeki hesaplamaları tekrar et
    # (Kısa örnek, gerçek paneldekiyle uyumlu olmalı)
    chart_labels = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran"]
    chart_income = [5000, 7500, 6200, 8000, 7000, 9000]
    chart_expense = [3000, 4000, 3500, 4200, 3900, 4100]
    investment_labels = ["BIST", "USD", "BTC"]
    investment_returns = [1200, 800, 250]
    total_income = sum(chart_income)
    total_expense = sum(chart_expense)
    total_investment = sum(investment_returns)
    ai_advice = get_ai_financial_advice(
        request.user, total_income, total_expense, total_investment
    )

    context = {
        "user": request.user,
        "chart_labels": chart_labels,
        "chart_income": chart_income,
        "chart_expense": chart_expense,
        "investment_labels": investment_labels,
        "investment_returns": investment_returns,
        "ai_advice": ai_advice,
    }
    html_string = render_to_string("finance/pdf_report.html", context)
    if HTML is None:
        return HttpResponse("WeasyPrint yüklü değil.", status=500)
    pdf_file = HTML(string=html_string).write_pdf()
    response = HttpResponse(pdf_file, content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="finansal_rapor.pdf"'
    return response
