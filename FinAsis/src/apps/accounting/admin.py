from django.contrib import admin
from .models import Company, Customer, Invoice, Expense, Product, Sale, Payment, BankAccount, InvoiceItem, BankTransaction, CompanyDeleteLog, EDefter, Vendor, PurchaseInvoice, VendorPayment, BankStatement, BankStatementLine
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.urls import reverse, NoReverseMatch

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "tax_number", "phone", "sector", "created_at", "is_active_colored")
    search_fields = ("name", "tax_number", "sector")
    list_filter = ("sector", "created_at", "is_active")
    actions = ["restore_companies", "archive_companies"]

    @admin.display(description="Durum")
    def is_active_colored(self, obj):
        if not obj.is_active:
            return format_html('<span style="color: #888; background: #eee; padding:2px 8px; border-radius:4px;">Pasif</span>')
        return format_html('<span style="color: #388e3c;">Aktif</span>')

    @admin.action(description="Seçili şirketleri yeniden aktifleştir")
    def restore_companies(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} şirket yeniden aktifleştirildi.")

    @admin.action(description="Seçili şirketleri arşivle (soft delete)")
    def archive_companies(self, request, queryset):
        from .models import CompanyDeleteLog
        count = 0
        for obj in queryset:
            # Soft delete: mark inactive and log
            if obj.is_active:
                CompanyDeleteLog.objects.create(company=obj, user=request.user, reason="Admin bulk soft delete")
                obj.is_active = False
                obj.save(update_fields=["is_active", "updated_at"])
                count += 1
        self.message_user(request, f"{count} şirket arşivlendi (soft delete).")

    def has_delete_permission(self, request, obj=None):
        # Sadece süper kullanıcılar için gerçek silme izni; aksi halde soft-delete önerilir
        return bool(request.user and request.user.is_superuser)

    def delete_model(self, request, obj):
        # Tekil silme: gerçek silme yerine arşivle ve log kaydı oluştur
        from .models import CompanyDeleteLog
        try:
            CompanyDeleteLog.objects.create(company=obj, user=request.user, reason="Admin soft delete")
        except Exception:
            pass
        obj.is_active = False
        obj.save(update_fields=["is_active", "updated_at"])

    def delete_queryset(self, request, queryset):
        # Toplu silme: gerçek silme yerine arşivle ve log kaydı oluştur
        from .models import CompanyDeleteLog
        for obj in queryset:
            try:
                CompanyDeleteLog.objects.create(company=obj, user=request.user, reason="Admin bulk soft delete")
            except Exception:
                pass
        queryset.update(is_active=False)

    def get_actions(self, request):
        actions = super().get_actions(request)
        # Varsayılan "delete_selected" toplu silme aksiyonunu kaldır
        if "delete_selected" in actions:
            del actions["delete_selected"]
        return actions

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Kullanıcı açıkça is_active filtresi seçmemişse varsayılan olarak aktif şirketleri göster
        if "is_active__exact" in request.GET:
            return qs
        return qs.filter(is_active=True)

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "email", "phone", "company", "created_at")
    search_fields = ("first_name", "last_name", "email")
    list_filter = ("company",)

# NOTE: Invoice admin is defined below with inline items.

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

try:
    admin.site.unregister(Invoice)
except Exception:
    # Not registered yet
    pass
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
        context['finasis_logo'] = '/static/common/FinAsis_logo.png'
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
            quick_actions = []
            # Users (support custom AUTH_USER_MODEL)
            UserModel = get_user_model()
            user_url_name = f"admin:{UserModel._meta.app_label}_{UserModel._meta.model_name}_changelist"
            try:
                quick_actions.append({"label": "Kullanıcılar", "url": reverse(user_url_name)})
            except NoReverseMatch:
                pass
            # Groups
            try:
                quick_actions.append({"label": "Gruplar", "url": reverse('admin:auth_group_changelist')})
            except NoReverseMatch:
                pass
            # Companies, Invoices, Rules
            for name, urlname in [
                ("Şirketler", 'admin:accounting_company_changelist'),
                ("Faturalar", 'admin:accounting_invoice_changelist'),
                ("Kurallar", 'admin:finance_accounting_autobookingrule_changelist'),
            ]:
                try:
                    quick_actions.append({"label": name, "url": reverse(urlname)})
                except NoReverseMatch:
                    continue
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
@admin.register(BankStatement)
class BankStatementAdmin(admin.ModelAdmin):
    list_display = ("bank_account", "period_start", "period_end", "opening_balance", "closing_balance")
    list_filter = ("bank_account",)

@admin.register(BankStatementLine)
class BankStatementLineAdmin(admin.ModelAdmin):
    list_display = ("statement", "date", "description", "amount", "matched_transaction")
    list_filter = ("statement",)

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

# --- AP Admin ---
@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ("name", "tax_number", "phone", "email", "company", "is_active")
    search_fields = ("name", "tax_number", "email")
    list_filter = ("company", "is_active")

@admin.register(PurchaseInvoice)
class PurchaseInvoiceAdmin(admin.ModelAdmin):
    list_display = ("invoice_number", "company", "vendor", "issue_date", "total_amount", "currency", "status")
    search_fields = ("invoice_number", "vendor__name")
    list_filter = ("company", "currency", "issue_date", "status")

@admin.register(VendorPayment)
class VendorPaymentAdmin(admin.ModelAdmin):
    list_display = ("vendor", "amount", "payment_method", "payment_date", "related_invoice")
    list_filter = ("company", "payment_method", "payment_date")
    search_fields = ("vendor__name", "related_invoice__invoice_number")