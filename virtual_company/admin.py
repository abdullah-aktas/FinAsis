from django.contrib import admin
from .models import (
    Company, Department, Employee, Project,
    Budget, Report, Product, StockMovement,
    ProductionOrder, BillOfMaterials, QualityControl,
    ModuleSetting, DailyTask, UserDailyTask,
    KnowledgeBase, KnowledgeBaseRelatedItem
)

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'tax_number', 'email', 'phone', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'tax_number', 'email')
    ordering = ('-created_at',)

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'company', 'manager', 'budget', 'is_active')
    list_filter = ('company', 'is_active')
    search_fields = ('name', 'company__name')
    ordering = ('company', 'name')

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('user', 'company', 'department', 'position', 'hire_date', 'is_active')
    list_filter = ('company', 'department', 'is_active')
    search_fields = ('user__username', 'user__email', 'position')
    ordering = ('-hire_date',)

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'company', 'manager', 'start_date', 'end_date', 'status')
    list_filter = ('company', 'status', 'department')
    search_fields = ('name', 'company__name', 'manager__username')
    ordering = ('-created_at',)

@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ('company', 'department', 'type', 'amount', 'date')
    list_filter = ('company', 'department', 'type')
    search_fields = ('company__name', 'department__name')
    ordering = ('-date',)

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'type', 'created_by', 'created_at')
    list_filter = ('company', 'type')
    search_fields = ('title', 'company__name', 'created_by__username')
    ordering = ('-created_at',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'unit_price', 'stock_quantity')
    list_filter = ('created_at',)
    search_fields = ('name', 'code')
    ordering = ('name',)

@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ('product', 'movement_type', 'quantity', 'unit_price', 'created_at')
    list_filter = ('movement_type', 'created_at')
    search_fields = ('product__name', 'reference')
    ordering = ('-created_at',)

@admin.register(ProductionOrder)
class ProductionOrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'product', 'quantity', 'status', 'planned_start_date')
    list_filter = ('status', 'planned_start_date')
    search_fields = ('order_number', 'product__name')
    ordering = ('-created_at',)

@admin.register(BillOfMaterials)
class BillOfMaterialsAdmin(admin.ModelAdmin):
    list_display = ('product', 'component', 'quantity', 'unit', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('product__name', 'component__name')
    ordering = ('product', 'component')

@admin.register(QualityControl)
class QualityControlAdmin(admin.ModelAdmin):
    list_display = ('production_order', 'inspection_date', 'inspector', 'result')
    list_filter = ('result', 'inspection_date')
    search_fields = ('production_order__order_number', 'inspector__username')
    ordering = ('-inspection_date',)

@admin.register(ModuleSetting)
class ModuleSettingAdmin(admin.ModelAdmin):
    list_display = ('module', 'company', 'key', 'is_global')
    list_filter = ('module', 'is_global')
    search_fields = ('module', 'key', 'company__name')
    ordering = ('module', 'key')

@admin.register(DailyTask)
class DailyTaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'difficulty', 'xp_reward', 'is_active')
    list_filter = ('category', 'difficulty', 'is_active')
    search_fields = ('title', 'description')
    ordering = ('title',)

@admin.register(UserDailyTask)
class UserDailyTaskAdmin(admin.ModelAdmin):
    list_display = ('user', 'task', 'status', 'started_at', 'completed_at')
    list_filter = ('status', 'started_at')
    search_fields = ('user__username', 'task__title')
    ordering = ('-started_at',)

@admin.register(KnowledgeBase)
class KnowledgeBaseAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'created_by', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('title', 'content', 'tags')
    ordering = ('-created_at',)

@admin.register(KnowledgeBaseRelatedItem)
class KnowledgeBaseRelatedItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'knowledge_base', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('title', 'description', 'knowledge_base__title')
    ordering = ('title',) 