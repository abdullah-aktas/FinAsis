from django.contrib import admin
from .models import Customer, CustomerNote, CustomerDocument

class CustomerNoteInline(admin.TabularInline):
    model = CustomerNote
    extra = 1

class CustomerDocumentInline(admin.TabularInline):
    model = CustomerDocument
    extra = 1

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'company', 'phone', 'created_by', 'created_at', 'is_active')
    list_filter = ('is_active', 'created_by', 'created_at')
    search_fields = ('name', 'email', 'company', 'phone')
    inlines = [CustomerNoteInline, CustomerDocumentInline]
    date_hierarchy = 'created_at'

@admin.register(CustomerNote)
class CustomerNoteAdmin(admin.ModelAdmin):
    list_display = ('customer', 'title', 'created_by', 'created_at')
    list_filter = ('created_by', 'created_at')
    search_fields = ('customer__name', 'title', 'content')
    date_hierarchy = 'created_at'

@admin.register(CustomerDocument)
class CustomerDocumentAdmin(admin.ModelAdmin):
    list_display = ('customer', 'title', 'created_by', 'created_at')
    list_filter = ('created_by', 'created_at')
    search_fields = ('customer__name', 'title', 'description')
    date_hierarchy = 'created_at'
