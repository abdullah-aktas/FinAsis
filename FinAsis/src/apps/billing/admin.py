from django.contrib import admin
from .models import Plan, Price, Module, PlanModule, SubscriptionProfile, Transaction, BankTransfer, EnterpriseInquiry

@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('code','name','audience','is_active')
    list_filter = ('audience','is_active')

@admin.register(Price)
class PriceAdmin(admin.ModelAdmin):
    list_display = ('plan','period','amount','currency','is_active')
    list_filter = ('period','currency','is_active','plan')
    search_fields = ('plan__name', 'plan__code')

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('code','name','is_active')

@admin.register(PlanModule)
class PlanModuleAdmin(admin.ModelAdmin):
    list_display = ('plan','module')

@admin.register(SubscriptionProfile)
class SubscriptionProfileAdmin(admin.ModelAdmin):
    list_display = ('user','plan','status','current_period_end','provider')
    list_filter = ('status','provider','plan')
    search_fields = ('user__username','user__email','plan__name','plan__code')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user','plan','amount','currency','method','status','created_at')
    list_filter = ('method','status','currency','plan')
    search_fields = ('user__username','user__email','external_id')

@admin.register(BankTransfer)
class BankTransferAdmin(admin.ModelAdmin):
    list_display = ('user','plan','amount','currency','reference_code','is_confirmed','created_at')
    list_filter = ('is_confirmed','currency','plan')
    search_fields = ('user__username','user__email','reference_code')

@admin.register(EnterpriseInquiry)
class EnterpriseInquiryAdmin(admin.ModelAdmin):
    list_display = ('name','email','company','plan','created_at')
    search_fields = ('name','email','company')
