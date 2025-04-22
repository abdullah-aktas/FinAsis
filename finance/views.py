from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import CashFlow, IncomeStatement

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