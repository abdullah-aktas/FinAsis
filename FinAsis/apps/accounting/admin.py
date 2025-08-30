from django.contrib import admin
from .models import Company, Customer, Invoice, Expense, Product, Sale, Payment, BankAccount, InvoiceItem, BankTransaction, CompanyDeleteLog, EDefter
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "tax_number", "phone", "sector", "created_at", "is_active_colored")
    search_fields = ("name", "tax_number", "sector")
    list_filter = ("sector", "created_at", "is_active")
    actions = ["restore_companies"]

    def is_active_colored(self, obj):
        if not obj.is_active:
            return format_html('<span style="color: #888; background: #eee; padding:2px 8px; border-radius:4px;">Pasif</span>')
        return format_html('<span style="color: #388e3c;">Aktif</span>')
    is_active_colored.short_description = "Durum"

    def restore_companies(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} şirket yeniden aktifleştirildi.")
    restore_companies.short_description = "Seçili şirketleri yeniden aktifleştir"

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "email", "phone", "company", "created_at")
    search_fields = ("first_name", "last_name", "email")
    list_filter = ("company",)

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("invoice_number", "company", "customer", "issue_date", "total_amount", "currency", "e_archive")
    search_fields = ("invoice_number", "customer__first_name", "customer__last_name")
    list_filter = ("company", "currency", "issue_date", "e_archive")

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ("company", "category", "amount", "expense_date", "paid")
    list_filter = ("company", "category", "paid", "expense_date")
    search_fields = ("description",)
    list_editable = ("paid",)
    list_per_page = 20
    
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "company", "price", "stock", "created_at")
    search_fields = ("name", "description")
    list_filter = ("company",)

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ("customer", "product", "quantity", "unit_price", "total_price", "sale_date")
    list_filter = ("company", "sale_date")
    search_fields = ("customer__first_name", "product__name")

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("customer", "amount", "payment_method", "payment_date", "related_invoice")
    list_filter = ("company", "payment_method", "payment_date")
    search_fields = ("customer__first_name", "customer__last_name", "related_invoice__invoice_number")

@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    list_display = ("bank_name", "iban", "account_name", "company", "account_type", "balance", "currency")
    search_fields = ("bank_name", "iban", "account_name")
    list_filter = ("company", "account_type", "currency")

#Fatura Kalemi admin'ine inline ekle
class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1

# Fatura admin'ine inline ekle
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("invoice_number", "company", "customer", "issue_date", "total_amount", "currency", "e_archive")
    search_fields = ("invoice_number", "customer__first_name", "customer__last_name")
    list_filter = ("company", "currency", "issue_date", "e_archive")
    inlines = [InvoiceItemInline]

admin.site.unregister(Invoice)
admin.site.register(Invoice, InvoiceAdmin)

# Admin paneli başlığı ve header'ı özelleştir
admin.site.site_title = _('FinAsis Yönetim Paneli')
admin.site.site_header = _('FinAsis Finansal Yönetim')
admin.site.index_title = _('FinAsis Paneline Hoşgeldiniz')

# Admin paneline logo ve kısa açıklama eklemek için custom AdminSite kullan
class FinAsisAdminSite(admin.AdminSite):
    site_title = _('FinAsis Yönetim Paneli')
    site_header = _('FinAsis Finansal Yönetim')
    index_title = _('FinAsis Paneline Hoşgeldiniz')
    
    def each_context(self, request):
        context = super().each_context(request)
        context['finasis_logo'] = '/static/common/finasis_logo.svg'  # Logo yolunu özelleştir
        context['finasis_desc'] = _('Modern Finansal Yönetim Platformu')
        return context

    def index(self, request, extra_context=None):
        User = get_user_model()
        user_count = User.objects.count()
        company_count = Company.objects.count()
        invoice_count = Invoice.objects.count()
        expense_count = Expense.objects.count()
        last_invoices = Invoice.objects.order_by('-issue_date')[:5]
        last_expenses = Expense.objects.order_by('-expense_date')[:5]
        # Süper kullanıcılar için ekstra aksiyon kısa yolları
        quick_actions = []
        if request.user.is_superuser:
            quick_actions = [
                {"label": "Kullanıcılar", "url": "/admin/auth/user/"},
                {"label": "Gruplar", "url": "/admin/auth/group/"},
                {"label": "Şirketler", "url": "/admin/accounting/company/"},
                {"label": "Faturalar", "url": "/admin/accounting/invoice/"},
                {"label": "Kurallar", "url": "/admin/finance_accounting/autobookingrule/"},
            ]
        context = {
            'user_count': user_count,
            'company_count': company_count,
            'invoice_count': invoice_count,
            'expense_count': expense_count,
            'last_invoices': last_invoices,
            'last_expenses': last_expenses,
            'quick_actions': quick_actions,
        }
        if extra_context:
            context.update(extra_context)
        return super().index(request, extra_context=context)

# Varsayılan admin site ile devam etmek için aşağıdaki satırı yorumda bırakıyoruz
# admin.site = FinAsisAdminSite()
# Eğer tam özelleştirilmiş bir panel isterseniz yukarıdaki satırı aktif edin ve urls.py'da admin.site yerine bu nesneyi kullanın.

admin.site.register(BankTransaction)

@admin.register(CompanyDeleteLog)
class CompanyDeleteLogAdmin(admin.ModelAdmin):
    list_display = ("company", "user", "deleted_at", "reason")
    search_fields = ("company__name", "user__username", "reason")
    list_filter = ("deleted_at",)

@admin.register(EDefter)
class EDefterAdmin(admin.ModelAdmin):
    list_display = ("year", "month", "type", "status", "created_at")
    list_filter = ("year", "month", "type", "status")
    search_fields = ("year", "month", "type")