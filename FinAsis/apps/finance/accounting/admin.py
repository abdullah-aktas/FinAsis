# -*- coding: utf-8 -*-
"""
FinAsis Muhasebe Modülü - Admin Paneli Tanımları

Bu modül, muhasebe modellerinin admin panelindeki görünümlerini tanımlar.
"""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import (
    AccountType, Account, VoucherType, Voucher, VoucherLine,
    Currency, FinancialReport, AutoBookingRule
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
    list_display = ('code', 'name', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('code', 'name', 'description')
    ordering = ('code',)


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    """Hesap admin"""
    list_display = ('company', 'code', 'name', 'type', 'parent')
    list_filter = ('company', 'type', 'is_bank_account', 'is_cash_account', 'is_tax_account')
    search_fields = ('code', 'name', 'description')
    ordering = ('company', 'code')
    inlines = [AccountInline]
    fieldsets = (
        (None, {
            'fields': (('company', 'code', 'name'), 'type', 'parent', 'description')
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
    model = VoucherLine  # placeholder removed; no VoucherDocument model
    fields = ()
    extra = 0
    can_delete = False
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
    inlines = [VoucherLineInline]
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


# VoucherDocument modeli mevcut değil; ilgili admin kaldırıldı


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


# ExchangeRate modeli mevcut değil; ilgili admin kaldırıldı


# TaxDeclarationFile modeli mevcut değil; ilgili inline kaldırıldı


# TaxDeclaration modeli mevcut değil; ilgili admin kaldırıldı


# BudgetLine modeli mevcut değil; inline kaldırıldı


# Budget/BudgetLine modelleri mevcut değil; ilgili adminler kaldırıldı


@admin.register(FinancialReport)
class FinancialReportAdmin(admin.ModelAdmin):
    """Finansal rapor admin"""
    list_display = ('company', 'name', 'type', 'start_date', 'end_date')
    list_filter = ('company', 'type', 'start_date')
    search_fields = ('name', 'description')
    ordering = ('company', '-start_date')


@admin.register(AutoBookingRule)
class AutoBookingRuleAdmin(admin.ModelAdmin):
    list_display = ('company', 'name', 'nature', 'keyword_pattern', 'priority', 'is_active')
    list_filter = ('company', 'nature', 'is_active')
    search_fields = ('name', 'keyword_pattern')
    ordering = ('company', 'priority', 'name')