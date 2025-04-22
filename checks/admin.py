from django.contrib import admin
from .models import Bank, Check, PromissoryNote, CheckTransaction, PromissoryNoteTransaction

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
