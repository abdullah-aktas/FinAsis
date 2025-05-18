# -*- coding: utf-8 -*-
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import (
    AccountPlan, BalanceSheet, BaseModel, BudgetLine, CashFlow,
    EDocumentTemplate, EInvoiceLog, EInvoiceSettings, JournalEntry,
    KnowledgeBaseRelatedItem
)

# AccountPlan Views
class AccountPlanListView(LoginRequiredMixin, ListView):
    model = AccountPlan
    template_name = 'accounting/accountplan_list.html'
    context_object_name = 'account_plans'

class AccountPlanDetailView(LoginRequiredMixin, DetailView):
    model = AccountPlan
    template_name = 'accounting/accountplan_detail.html'

class AccountPlanCreateView(LoginRequiredMixin, CreateView):
    model = AccountPlan
    template_name = 'accounting/accountplan_form.html'
    fields = '__all__'
    success_url = reverse_lazy('accounting:accountplan_list')

class AccountPlanUpdateView(LoginRequiredMixin, UpdateView):
    model = AccountPlan
    template_name = 'accounting/accountplan_form.html'
    fields = '__all__'
    success_url = reverse_lazy('accounting:accountplan_list')

class AccountPlanDeleteView(LoginRequiredMixin, DeleteView):
    model = AccountPlan
    template_name = 'accounting/accountplan_confirm_delete.html'
    success_url = reverse_lazy('accounting:accountplan_list')

# BalanceSheet Views
class BalanceSheetListView(LoginRequiredMixin, ListView):
    model = BalanceSheet
    template_name = 'accounting/balancesheet_list.html'
    context_object_name = 'balance_sheets'

class BalanceSheetDetailView(LoginRequiredMixin, DetailView):
    model = BalanceSheet
    template_name = 'accounting/balancesheet_detail.html'

class BalanceSheetCreateView(LoginRequiredMixin, CreateView):
    model = BalanceSheet
    template_name = 'accounting/balancesheet_form.html'
    fields = '__all__'
    success_url = reverse_lazy('accounting:balancesheet_list')

class BalanceSheetUpdateView(LoginRequiredMixin, UpdateView):
    model = BalanceSheet
    template_name = 'accounting/balancesheet_form.html'
    fields = '__all__'
    success_url = reverse_lazy('accounting:balancesheet_list')

class BalanceSheetDeleteView(LoginRequiredMixin, DeleteView):
    model = BalanceSheet
    template_name = 'accounting/balancesheet_confirm_delete.html'
    success_url = reverse_lazy('accounting:balancesheet_list')

# CashFlow Views
class CashFlowListView(LoginRequiredMixin, ListView):
    model = CashFlow
    template_name = 'accounting/cashflow_list.html'
    context_object_name = 'cash_flows'

class CashFlowDetailView(LoginRequiredMixin, DetailView):
    model = CashFlow
    template_name = 'accounting/cashflow_detail.html'

class CashFlowCreateView(LoginRequiredMixin, CreateView):
    model = CashFlow
    template_name = 'accounting/cashflow_form.html'
    fields = '__all__'
    success_url = reverse_lazy('accounting:cashflow_list')

class CashFlowUpdateView(LoginRequiredMixin, UpdateView):
    model = CashFlow
    template_name = 'accounting/cashflow_form.html'
    fields = '__all__'
    success_url = reverse_lazy('accounting:cashflow_list')

class CashFlowDeleteView(LoginRequiredMixin, DeleteView):
    model = CashFlow
    template_name = 'accounting/cashflow_confirm_delete.html'
    success_url = reverse_lazy('accounting:cashflow_list')

# JournalEntry Views
class JournalEntryListView(LoginRequiredMixin, ListView):
    model = JournalEntry
    template_name = 'accounting/journalentry_list.html'
    context_object_name = 'journal_entries'

class JournalEntryDetailView(LoginRequiredMixin, DetailView):
    model = JournalEntry
    template_name = 'accounting/journalentry_detail.html'

class JournalEntryCreateView(LoginRequiredMixin, CreateView):
    model = JournalEntry
    template_name = 'accounting/journalentry_form.html'
    fields = '__all__'
    success_url = reverse_lazy('accounting:journalentry_list')

class JournalEntryUpdateView(LoginRequiredMixin, UpdateView):
    model = JournalEntry
    template_name = 'accounting/journalentry_form.html'
    fields = '__all__'
    success_url = reverse_lazy('accounting:journalentry_list')

class JournalEntryDeleteView(LoginRequiredMixin, DeleteView):
    model = JournalEntry
    template_name = 'accounting/journalentry_confirm_delete.html'
    success_url = reverse_lazy('accounting:journalentry_list')

# EInvoice Views
class EInvoiceSettingsListView(LoginRequiredMixin, ListView):
    model = EInvoiceSettings
    template_name = 'accounting/einvoice_settings_list.html'
    context_object_name = 'settings'

class EInvoiceSettingsDetailView(LoginRequiredMixin, DetailView):
    model = EInvoiceSettings
    template_name = 'accounting/einvoice_settings_detail.html'

class EInvoiceSettingsCreateView(LoginRequiredMixin, CreateView):
    model = EInvoiceSettings
    template_name = 'accounting/einvoice_settings_form.html'
    fields = '__all__'
    success_url = reverse_lazy('accounting:einvoice_settings_list')

class EInvoiceSettingsUpdateView(LoginRequiredMixin, UpdateView):
    model = EInvoiceSettings
    template_name = 'accounting/einvoice_settings_form.html'
    fields = '__all__'
    success_url = reverse_lazy('accounting:einvoice_settings_list')

class EInvoiceSettingsDeleteView(LoginRequiredMixin, DeleteView):
    model = EInvoiceSettings
    template_name = 'accounting/einvoice_settings_confirm_delete.html'
    success_url = reverse_lazy('accounting:einvoice_settings_list')

# EInvoiceLog Views
class EInvoiceLogListView(LoginRequiredMixin, ListView):
    model = EInvoiceLog
    template_name = 'accounting/einvoice_log_list.html'
    context_object_name = 'logs'

class EInvoiceLogDetailView(LoginRequiredMixin, DetailView):
    model = EInvoiceLog
    template_name = 'accounting/einvoice_log_detail.html'

# EDocumentTemplate Views
class EDocumentTemplateListView(LoginRequiredMixin, ListView):
    model = EDocumentTemplate
    template_name = 'accounting/edocument_template_list.html'
    context_object_name = 'templates'

class EDocumentTemplateDetailView(LoginRequiredMixin, DetailView):
    model = EDocumentTemplate
    template_name = 'accounting/edocument_template_detail.html'

class EDocumentTemplateCreateView(LoginRequiredMixin, CreateView):
    model = EDocumentTemplate
    template_name = 'accounting/edocument_template_form.html'
    fields = '__all__'
    success_url = reverse_lazy('accounting:edocument_template_list')

class EDocumentTemplateUpdateView(LoginRequiredMixin, UpdateView):
    model = EDocumentTemplate
    template_name = 'accounting/edocument_template_form.html'
    fields = '__all__'
    success_url = reverse_lazy('accounting:edocument_template_list')

class EDocumentTemplateDeleteView(LoginRequiredMixin, DeleteView):
    model = EDocumentTemplate
    template_name = 'accounting/edocument_template_confirm_delete.html'
    success_url = reverse_lazy('accounting:edocument_template_list')

# KnowledgeBaseRelatedItem Views
class KnowledgeBaseRelatedItemListView(LoginRequiredMixin, ListView):
    model = KnowledgeBaseRelatedItem
    template_name = 'accounting/knowledgebase_related_item_list.html'
    context_object_name = 'related_items'

class KnowledgeBaseRelatedItemDetailView(LoginRequiredMixin, DetailView):
    model = KnowledgeBaseRelatedItem
    template_name = 'accounting/knowledgebase_related_item_detail.html'

class KnowledgeBaseRelatedItemCreateView(LoginRequiredMixin, CreateView):
    model = KnowledgeBaseRelatedItem
    template_name = 'accounting/knowledgebase_related_item_form.html'
    fields = '__all__'
    success_url = reverse_lazy('accounting:knowledgebase_related_item_list')

class KnowledgeBaseRelatedItemUpdateView(LoginRequiredMixin, UpdateView):
    model = KnowledgeBaseRelatedItem
    template_name = 'accounting/knowledgebase_related_item_form.html'
    fields = '__all__'
    success_url = reverse_lazy('accounting:knowledgebase_related_item_list')

class KnowledgeBaseRelatedItemDeleteView(LoginRequiredMixin, DeleteView):
    model = KnowledgeBaseRelatedItem
    template_name = 'accounting/knowledgebase_related_item_confirm_delete.html'
    success_url = reverse_lazy('accounting:knowledgebase_related_item_list') 