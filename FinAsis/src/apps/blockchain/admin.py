from django.contrib import admin
from .models import ChainRecord

@admin.register(ChainRecord)
class ChainRecordAdmin(admin.ModelAdmin):
    list_display = ("reference", "hash_hex", "status", "created_at")
    search_fields = ("reference", "hash_hex")
    list_filter = ("status", "created_at")

# Register your models here.
