from django.contrib import admin
from .models import Plan, Price, Module, PlanModule, SubscriptionProfile, Transaction, BankTransfer

@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('code','name','is_active')

@admin.register(Price)
class PriceAdmin(admin.ModelAdmin):
    list_display = ('plan','period','amount','currency','is_active')

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('code','name','is_active')

@admin.register(PlanModule)
class PlanModuleAdmin(admin.ModelAdmin):
    list_display = ('plan','module')

@admin.register(SubscriptionProfile)
class SubscriptionProfileAdmin(admin.ModelAdmin):
    list_display = ('user','plan','status','current_period_end','provider')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user','plan','amount','currency','method','status','created_at')

@admin.register(BankTransfer)
class BankTransferAdmin(admin.ModelAdmin):
    list_display = ('user','plan','amount','currency','reference_code','is_confirmed','created_at')
