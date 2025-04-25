from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import (
    Bank, Check, PromissoryNote, CheckTransaction, PromissoryNoteTransaction,
    CheckCategory, CheckType, CheckRule,
    CheckResult, CheckSchedule
)

@admin.register(Bank)
class BankAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'branch_code', 'branch_name', 'created_at')
    search_fields = ('name', 'code', 'branch_code', 'branch_name')
    list_filter = ('created_at',)

@admin.register(Check)
class CheckAdmin(admin.ModelAdmin):
    list_display = ('check_number', 'bank', 'amount', 'issue_date', 'due_date', 'status', 'check_type')
    search_fields = ('check_number', 'drawer_name', 'payee_name', 'drawer_tax_number', 'payee_tax_number')
    list_filter = ('status', 'check_type', 'bank', 'issue_date', 'due_date')
    date_hierarchy = 'due_date'

@admin.register(PromissoryNote)
class PromissoryNoteAdmin(admin.ModelAdmin):
    list_display = ('note_number', 'amount', 'issue_date', 'due_date', 'status', 'note_type')
    search_fields = ('note_number', 'drawer_name', 'payee_name', 'drawer_tax_number', 'payee_tax_number')
    list_filter = ('status', 'note_type', 'issue_date', 'due_date')
    date_hierarchy = 'due_date'

@admin.register(CheckTransaction)
class CheckTransactionAdmin(admin.ModelAdmin):
    list_display = ('check', 'transaction_type', 'transaction_date', 'amount', 'created_by')
    search_fields = ('check__check_number', 'reference_number', 'notes')
    list_filter = ('transaction_type', 'transaction_date', 'created_by')
    date_hierarchy = 'transaction_date'

@admin.register(PromissoryNoteTransaction)
class PromissoryNoteTransactionAdmin(admin.ModelAdmin):
    list_display = ('promissory_note', 'transaction_type', 'transaction_date', 'amount', 'created_by')
    search_fields = ('promissory_note__note_number', 'reference_number', 'notes')
    list_filter = ('transaction_type', 'transaction_date', 'created_by')
    date_hierarchy = 'transaction_date'

@admin.register(CheckCategory)
class CheckCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'priority', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('-priority', 'name')

@admin.register(CheckType)
class CheckTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'category', 'severity', 'is_active', 'created_at')
    list_filter = ('category', 'severity', 'is_active', 'created_at')
    search_fields = ('name', 'code', 'description')
    ordering = ('category', 'severity', 'name')
    raw_id_fields = ('category',)

@admin.register(CheckRule)
class CheckRuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'check_type', 'weight', 'is_active', 'created_at')
    list_filter = ('check_type', 'is_active', 'created_at')
    search_fields = ('name', 'description', 'condition')
    ordering = ('check_type', 'weight')
    raw_id_fields = ('check_type',)

@admin.register(CheckResult)
class CheckResultAdmin(admin.ModelAdmin):
    list_display = ('check_type', 'status', 'score', 'started_at', 'completed_at', 'duration')
    list_filter = ('check_type', 'status', 'started_at')
    search_fields = ('check_type__name', 'details')
    ordering = ('-started_at',)
    raw_id_fields = ('check_type',)
    readonly_fields = ('started_at', 'completed_at', 'duration')

@admin.register(CheckSchedule)
class CheckScheduleAdmin(admin.ModelAdmin):
    list_display = ('check_type', 'schedule', 'is_active', 'last_run', 'next_run')
    list_filter = ('is_active', 'last_run', 'next_run')
    search_fields = ('check_type__name', 'schedule')
    ordering = ('next_run',)
    raw_id_fields = ('check_type',)
    readonly_fields = ('last_run',)
