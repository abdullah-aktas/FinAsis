# -*- coding: utf-8 -*-
"""
FinAsis Muhasebe Modülü - Admin Paneli Tanımları

Bu modül, muhasebe modellerinin admin panelindeki görünümlerini tanımlar.
"""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import (
    AccountType, Account, VoucherType, Voucher, VoucherLine,
    Currency, ExchangeRate, VoucherDocument, FinancialReport,
    TaxDeclaration, TaxDeclarationFile, Budget, BudgetLine
)


class AccountInline(admin.TabularInline):
    """Alt hesapları göstermek için inline admin"""
    model = Account
    fields = ('code', 'name', 'type', 'is_active')
    extra = 0
    show_change_link = True
    verbose_name = _("Alt Hesap")
    verbose_name_plural = _("Alt Hesaplar")
    fk_name = 'parent'


@admin.register(AccountType)
class AccountTypeAdmin(admin.ModelAdmin):
    """Hesap türleri admin"""
    list_display = ('code', 'name', 'is_debit_balance', 'is_active')
    list_filter = ('is_debit_balance', 'is_active')
    search_fields = ('code', 'name', 'description')
    ordering = ('code',)


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    """Hesap admin"""
    list_display = ('company', 'code', 'name', 'type', 'parent', 'is_active')
    list_filter = ('company', 'type', 'is_active', 'is_bank_account', 'is_cash_account', 'is_tax_account')
    search_fields = ('code', 'name', 'description')
    ordering = ('company', 'code')
    inlines = [AccountInline]
    fieldsets = (
        (None, {
            'fields': (('company', 'code', 'name'), 'type', 'parent', 'description')
        }),
        (_('Durum'), {
            'fields': ('is_active',)
        }),
        (_('Hesap Özellikleri'), {
            'fields': ('is_bank_account', 'is_cash_account', 'is_tax_account'),
            'classes': ('collapse',),
        }),
    )


@admin.register(VoucherType)
class VoucherTypeAdmin(admin.ModelAdmin):
    """Fiş türleri admin"""
    list_display = ('code', 'name', 'prefix')
    search_fields = ('code', 'name', 'description')
    ordering = ('code',)


class VoucherLineInline(admin.TabularInline):
    """Fiş satırları inline admin"""
    model = VoucherLine
    fields = ('line_no', 'account', 'description', 'debit_amount', 'credit_amount')
    extra = 0
    verbose_name = _("Fiş Satırı")
    verbose_name_plural = _("Fiş Satırları")


class VoucherDocumentInline(admin.TabularInline):
    """Fiş belgeleri inline admin"""
    model = VoucherDocument
    fields = ('title', 'file', 'description')
    extra = 0
    verbose_name = _("Belge")
    verbose_name_plural = _("Belgeler")


@admin.register(Voucher)
class VoucherAdmin(admin.ModelAdmin):
    """Muhasebe fişi admin"""
    list_display = ('company', 'number', 'date', 'type', 'reference', 'state', 'total_amount', 'currency')
    list_filter = ('company', 'fiscal_year', 'type', 'state', 'date', 'currency')
    search_fields = ('number', 'description', 'reference')
    ordering = ('-date', 'number')
    date_hierarchy = 'date'
    inlines = [VoucherLineInline, VoucherDocumentInline]
    readonly_fields = ('state',)
    
    fieldsets = (
        (None, {
            'fields': (('company', 'fiscal_year'), ('type', 'number', 'date'), 'description', 'reference')
        }),
        (_('Durum'), {
            'fields': ('state',)
        }),
        (_('Döviz Bilgileri'), {
            'fields': ('currency', 'exchange_rate'),
            'classes': ('collapse',),
        }),
        (_('İlişkili Belgeler'), {
            'fields': ('invoice',),
            'classes': ('collapse',),
        }),
    )
    
    actions = ['post_vouchers', 'cancel_vouchers']
    
    def post_vouchers(self, request, queryset):
        """Seçili fişleri onaylar"""
        posted_count = 0
        error_count = 0
        
        for voucher in queryset:
            try:
                if voucher.state == 'DRAFT':
                    voucher.post()
                    posted_count += 1
            except Exception as e:
                error_count += 1
                self.message_user(request, 
                    _(f"Hata: {voucher.number} - {str(e)}"), 
                    level='ERROR'
                )
        
        if posted_count:
            self.message_user(request, 
                _(f"{posted_count} fiş başarıyla onaylandı."), 
                level='SUCCESS'
            )
        
        if error_count:
            self.message_user(request, 
                _(f"{error_count} fiş onaylanırken hata oluştu."), 
                level='WARNING'
            )
    
    post_vouchers.short_description = _("Seçili fişleri onayla")
    
    def cancel_vouchers(self, request, queryset):
        """Seçili fişleri iptal eder"""
        cancelled_count = 0
        error_count = 0
        
        for voucher in queryset:
            try:
                if voucher.state == 'DRAFT':
                    voucher.cancel()
                    cancelled_count += 1
            except Exception as e:
                error_count += 1
                self.message_user(request, 
                    _(f"Hata: {voucher.number} - {str(e)}"), 
                    level='ERROR'
                )
        
        if cancelled_count:
            self.message_user(request, 
                _(f"{cancelled_count} fiş başarıyla iptal edildi."), 
                level='SUCCESS'
            )
        
        if error_count:
            self.message_user(request, 
                _(f"{error_count} fiş iptal edilirken hata oluştu."), 
                level='WARNING'
            )
    
    cancel_vouchers.short_description = _("Seçili fişleri iptal et")


@admin.register(VoucherLine)
class VoucherLineAdmin(admin.ModelAdmin):
    """Muhasebe fişi satırı admin"""
    list_display = ('voucher', 'line_no', 'account', 'description', 'debit_amount', 'credit_amount')
    list_filter = ('voucher__company', 'voucher__type', 'voucher__date')
    search_fields = ('description', 'voucher__number', 'account__code', 'account__name')
    ordering = ('voucher', 'line_no')
    raw_id_fields = ('voucher', 'account')


@admin.register(VoucherDocument)
class VoucherDocumentAdmin(admin.ModelAdmin):
    """Fiş belgeleri admin"""
    list_display = ('voucher', 'title', 'filename', 'file_size', 'created_by', 'created_at')
    list_filter = ('voucher__company', 'voucher__type', 'created_at')
    search_fields = ('title', 'description', 'voucher__number')
    ordering = ('voucher', '-created_at')
    raw_id_fields = ('voucher',)


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    """Para birimi admin"""
    list_display = ('code', 'name', 'symbol', 'is_default', 'is_active')
    list_filter = ('is_default', 'is_active')
    search_fields = ('code', 'name')
    ordering = ('code',)
    
    actions = ['set_as_default']
    
    def set_as_default(self, request, queryset):
        """Seçili para birimini varsayılan olarak ayarlar"""
        if queryset.count() != 1:
            self.message_user(request, _("Lütfen sadece bir para birimi seçin."), level='ERROR')
            return
        
        currency = queryset.first()
        
        # Diğer para birimlerinin varsayılan ayarını kaldır
        Currency.objects.filter(is_default=True).update(is_default=False)
        
        # Seçilen para birimini varsayılan olarak ayarla
        currency.is_default = True
        currency.save()
        
        self.message_user(request, _(f"{currency.code} varsayılan para birimi olarak ayarlandı."), level='SUCCESS')
    
    set_as_default.short_description = _("Seçili para birimini varsayılan yap")


@admin.register(ExchangeRate)
class ExchangeRateAdmin(admin.ModelAdmin):
    """Döviz kuru admin"""
    list_display = ('currency', 'date', 'rate')
    list_filter = ('currency', 'date')
    search_fields = ('currency__code', 'currency__name')
    ordering = ('currency', '-date')
    date_hierarchy = 'date'


class TaxDeclarationFileInline(admin.TabularInline):
    """Vergi beyanname dosyaları inline admin"""
    model = TaxDeclarationFile
    fields = ('title', 'file')
    extra = 0
    verbose_name = _("Beyanname Dosyası")
    verbose_name_plural = _("Beyanname Dosyaları")


@admin.register(TaxDeclaration)
class TaxDeclarationAdmin(admin.ModelAdmin):
    """Vergi beyannamesi admin"""
    list_display = ('company', 'tax_type', 'period', 'due_date', 'state', 'total_tax')
    list_filter = ('company', 'tax_type', 'state', 'due_date')
    search_fields = ('period', 'reference_number', 'notes')
    ordering = ('company', 'tax_type', '-due_date')
    date_hierarchy = 'due_date'
    inlines = [TaxDeclarationFileInline]
    
    fieldsets = (
        (None, {
            'fields': (('company', 'tax_type', 'period'), ('due_date', 'submission_date'), 'total_tax', 'reference_number')
        }),
        (_('Durum'), {
            'fields': ('state',)
        }),
        (_('Detaylar'), {
            'fields': ('notes',),
            'classes': ('collapse',),
        }),
    )
    
    actions = ['mark_as_submitted', 'mark_as_accepted']
    
    def mark_as_submitted(self, request, queryset):
        """Seçili beyannameleri gönderildi olarak işaretler"""
        count = queryset.update(state='SUBMITTED')
        self.message_user(request, _(f"{count} beyanname gönderildi olarak işaretlendi."), level='SUCCESS')
    
    mark_as_submitted.short_description = _("Seçili beyannameleri gönderildi olarak işaretle")
    
    def mark_as_accepted(self, request, queryset):
        """Seçili beyannameleri kabul edildi olarak işaretler"""
        count = queryset.update(state='ACCEPTED')
        self.message_user(request, _(f"{count} beyanname kabul edildi olarak işaretlendi."), level='SUCCESS')
    
    mark_as_accepted.short_description = _("Seçili beyannameleri kabul edildi olarak işaretle")


class BudgetLineInline(admin.TabularInline):
    """Bütçe kalemleri inline admin"""
    model = BudgetLine
    fields = ('account', 'description', 'planned_amount', 'actual_amount')
    extra = 0
    verbose_name = _("Bütçe Kalemi")
    verbose_name_plural = _("Bütçe Kalemleri")


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    """Bütçe admin"""
    list_display = ('company', 'title', 'fiscal_year', 'start_date', 'end_date', 'state', 'total_planned_amount', 'total_actual_amount')
    list_filter = ('company', 'fiscal_year', 'state', 'start_date')
    search_fields = ('title', 'description')
    ordering = ('company', '-start_date')
    date_hierarchy = 'start_date'
    inlines = [BudgetLineInline]
    
    fieldsets = (
        (None, {
            'fields': (('company', 'fiscal_year'), 'title', ('start_date', 'end_date'), 'description')
        }),
        (_('Durum'), {
            'fields': ('state',)
        }),
    )
    
    actions = ['activate_budgets', 'close_budgets']
    
    def activate_budgets(self, request, queryset):
        """Seçili bütçeleri aktifleştirir"""
        activated_count = 0
        
        for budget in queryset:
            if budget.state == 'DRAFT':
                budget.activate()
                activated_count += 1
        
        self.message_user(request, _(f"{activated_count} bütçe aktifleştirildi."), level='SUCCESS')
    
    activate_budgets.short_description = _("Seçili bütçeleri aktifleştir")
    
    def close_budgets(self, request, queryset):
        """Seçili bütçeleri kapatır"""
        closed_count = 0
        
        for budget in queryset:
            if budget.state == 'ACTIVE':
                budget.close()
                closed_count += 1
        
        self.message_user(request, _(f"{closed_count} bütçe kapatıldı."), level='SUCCESS')
    
    close_budgets.short_description = _("Seçili bütçeleri kapat")


@admin.register(FinancialReport)
class FinancialReportAdmin(admin.ModelAdmin):
    """Finansal rapor admin"""
    list_display = ('company', 'report_type', 'title', 'start_date', 'end_date', 'created_at')
    list_filter = ('company', 'report_type', 'fiscal_year', 'created_at')
    search_fields = ('title', 'description')
    ordering = ('company', '-created_at')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        (None, {
            'fields': (('company', 'fiscal_year'), 'report_type', 'title', ('start_date', 'end_date'), 'description')
        }),
        (_('Rapor Verisi'), {
            'fields': ('parameters', 'data'),
            'classes': ('collapse',),
        }),
    )
    
    readonly_fields = ('data',) 