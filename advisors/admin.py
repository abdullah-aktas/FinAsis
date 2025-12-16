from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.db.models import Count
from .models import (
    AdvisorProfile,
    AdvisorRegistrySource,
    TaxpayerProfile,
    Engagement,
    AdvisorService,
    ConsultationSession,
    AdvisorReport,
    ClientContract,
    AdvisorTimeTracking,
    ClientDocument,
    AdvisorTask,
)


@admin.register(AdvisorProfile)
class AdvisorProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "type", "chamber_no", "client_count", "verified_at", "is_active")
    list_filter = ("type", "verified_at", "created_at")
    search_fields = ("user__username", "user__email", "chamber_no", "mersis_no")
    readonly_fields = ("verified_at", "created_at", "updated_at", "client_count_display")
    date_hierarchy = "verified_at"
    
    fieldsets = (
        (_("Kullanıcı Bilgisi"), {
            "fields": ("user", "type")
        }),
        (_("Oda ve Sertifika Bilgileri"), {
            "fields": ("chamber_no", "mersis_no", "e_signature_serial", "mali_muhur_fingerprint")
        }),
        (_("Durum"), {
            "fields": ("verified_at", "is_active")
        }),
        (_("İstatistikler"), {
            "fields": ("client_count_display",),
            "classes": ("collapse",)
        }),
        (_("Bilgiler"), {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )
    
    def client_count(self, obj):
        """Aktif müşteri sayısı"""
        return obj.engagements.filter(status='active').count()
    client_count.short_description = "Aktif Müşteri"
    
    def client_count_display(self, obj):
        """Detay sayfasında gösterilecek müşteri bilgisi"""
        count = obj.engagements.filter(status='active').count()
        total = obj.engagements.count()
        return f"{count} aktif / {total} toplam müşteri"
    client_count_display.short_description = "Müşteri Durumu"
    
    def is_active(self, obj):
        """Mali müşavir aktif mi?"""
        return obj.verified_at is not None
    is_active.boolean = True
    is_active.short_description = "Aktif"


@admin.register(AdvisorRegistrySource)
class AdvisorRegistrySourceAdmin(admin.ModelAdmin):
    list_display = ("source", "external_id", "fetched_at")
    search_fields = ("source", "external_id")
    readonly_fields = ("fetched_at",)


@admin.register(TaxpayerProfile)
class TaxpayerProfileAdmin(admin.ModelAdmin):
    list_display = ("name", "vkn_tckn", "mersis_no", "company", "advisor_count", "created_at")
    search_fields = ("name", "vkn_tckn", "mersis_no")
    list_filter = ("company", "created_at")
    readonly_fields = ("created_at", "updated_at", "advisor_count_display")
    date_hierarchy = "created_at"
    
    fieldsets = (
        (_("Temel Bilgiler"), {
            "fields": ("name", "vkn_tckn", "mersis_no")
        }),
        (_("Şirket Bağlantısı"), {
            "fields": ("company",)
        }),
        (_("İstatistikler"), {
            "fields": ("advisor_count_display",),
            "classes": ("collapse",)
        }),
        (_("Bilgiler"), {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )
    
    def advisor_count(self, obj):
        """Aktif danışman sayısı"""
        return obj.engagements.filter(status='active').count()
    advisor_count.short_description = "Danışman"
    
    def advisor_count_display(self, obj):
        """Detay sayfasında gösterilecek danışman bilgisi"""
        count = obj.engagements.filter(status='active').count()
        return f"{count} aktif danışman"
    advisor_count_display.short_description = "Danışman Durumu"


@admin.register(Engagement)
class EngagementAdmin(admin.ModelAdmin):
    list_display = ("advisor", "taxpayer", "scope", "status", "created_at", "is_active_badge")
    list_filter = ("scope", "status", "created_at")
    search_fields = ("advisor__user__username", "taxpayer__name", "taxpayer__vkn_tckn")
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "created_at"
    
    fieldsets = (
        (_("Taraflar"), {
            "fields": ("advisor", "taxpayer")
        }),
        (_("İş Kapsamı"), {
            "fields": ("scope", "status")
        }),
        (_("Bilgiler"), {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )
    
    @admin.display(description="Durum")
    def is_active_badge(self, obj):
        """Durum badge"""
        colors = {
            "active": "#28a745",
            "pending": "#ffc107",
            "revoked": "#dc3545",
        }
        color = colors.get(obj.status, "#6c757d")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display(),
        )


@admin.register(AdvisorService)
class AdvisorServiceAdmin(admin.ModelAdmin):
    list_display = (
        "service_name",
        "advisor",
        "service_type",
        "pricing_model",
        "price",
        "currency",
        "is_active",
        "created_at",
    )
    list_filter = ("service_type", "pricing_model", "is_active", "currency", "created_at")
    search_fields = ("service_name", "description", "advisor__user__username")
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "created_at"
    
    fieldsets = (
        (_("Hizmet Bilgisi"), {
            "fields": ("advisor", "service_name", "service_type", "description")
        }),
        (_("Fiyatlandırma"), {
            "fields": ("pricing_model", "price", "currency")
        }),
        (_("Durum"), {
            "fields": ("is_active",)
        }),
        (_("Bilgiler"), {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )


@admin.register(ConsultationSession)
class ConsultationSessionAdmin(admin.ModelAdmin):
    list_display = (
        "taxpayer",
        "advisor",
        "session_type",
        "scheduled_date",
        "scheduled_time",
        "status_badge",
        "billable",
        "billing_amount",
    )
    list_filter = ("status", "session_type", "billable", "scheduled_date")
    search_fields = ("taxpayer__name", "advisor__user__username", "agenda", "notes")
    readonly_fields = ("created_at", "updated_at", "actual_duration")
    date_hierarchy = "scheduled_date"
    
    fieldsets = (
        (_("Taraflar"), {
            "fields": ("advisor", "taxpayer", "session_type")
        }),
        (_("Zamanlama"), {
            "fields": ("scheduled_date", "scheduled_time", "duration_minutes", "actual_start", "actual_end", "actual_duration")
        }),
        (_("İçerik"), {
            "fields": ("agenda", "notes", "action_items")
        }),
        (_("Takip"), {
            "fields": ("follow_up_required", "follow_up_date")
        }),
        (_("Faturalandırma"), {
            "fields": ("billable", "billing_amount", "invoice_generated")
        }),
        (_("Durum"), {
            "fields": ("status",)
        }),
        (_("Bilgiler"), {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )
    
    @admin.display(description="Durum")
    def status_badge(self, obj):
        """Durum badge"""
        colors = {
            "scheduled": "#17a2b8",
            "in_progress": "#007bff",
            "completed": "#28a745",
            "cancelled": "#dc3545",
            "rescheduled": "#ffc107",
        }
        color = colors.get(obj.status, "#6c757d")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display(),
        )
    
    def actual_duration(self, obj):
        """Gerçek süre hesapla"""
        if obj.actual_start and obj.actual_end:
            delta = obj.actual_end - obj.actual_start
            minutes = int(delta.total_seconds() / 60)
            return f"{minutes} dakika"
        return "-"
    actual_duration.short_description = "Gerçek Süre"


@admin.register(AdvisorReport)
class AdvisorReportAdmin(admin.ModelAdmin):
    list_display = ("title", "advisor", "taxpayer", "report_type", "is_approved", "delivered_at", "created_at")
    list_filter = ("report_type", "is_approved", "created_at")
    search_fields = ("title", "taxpayer__name", "advisor__user__username", "executive_summary")
    readonly_fields = ("created_at", "updated_at", "delivered_at")
    date_hierarchy = "created_at"
    
    fieldsets = (
        (_("Temel Bilgiler"), {
            "fields": ("advisor", "taxpayer", "report_type", "title")
        }),
        (_("İçerik"), {
            "fields": ("executive_summary", "detailed_content", "findings", "recommendations")
        }),
        (_("Dönem"), {
            "fields": ("period_start", "period_end")
        }),
        (_("Dosyalar"), {
            "fields": ("report_file", "attachments")
        }),
        (_("Onay ve Teslimat"), {
            "fields": ("is_approved", "approved_by", "delivered_at")
        }),
        (_("Bilgiler"), {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )


@admin.register(ClientContract)
class ClientContractAdmin(admin.ModelAdmin):
    list_display = (
        "contract_number",
        "taxpayer",
        "advisor",
        "contract_type",
        "status_badge",
        "contract_value",
        "start_date",
        "end_date",
        "is_active",
    )
    list_filter = ("contract_type", "status", "auto_renew", "start_date", "end_date")
    search_fields = ("contract_number", "taxpayer__name", "title", "scope_of_work")
    readonly_fields = ("created_at", "updated_at", "signed_at", "is_active")
    date_hierarchy = "start_date"
    
    fieldsets = (
        (_("Taraflar"), {
            "fields": ("advisor", "taxpayer")
        }),
        (_("Sözleşme Bilgileri"), {
            "fields": ("contract_number", "contract_type", "title")
        }),
        (_("İçerik"), {
            "fields": ("scope_of_work", "terms_and_conditions")
        }),
        (_("Finansal"), {
            "fields": ("contract_value", "payment_terms")
        }),
        (_("Tarihler"), {
            "fields": ("start_date", "end_date", "renewal_date", "auto_renew", "renewal_notice_days")
        }),
        (_("Durum"), {
            "fields": ("status", "signed_at", "is_active")
        }),
        (_("Dosyalar"), {
            "fields": ("contract_file", "signed_contract")
        }),
        (_("Bilgiler"), {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )
    
    @admin.display(description="Durum")
    def status_badge(self, obj):
        """Durum badge"""
        colors = {
            "draft": "#6c757d",
            "pending_signature": "#ffc107",
            "active": "#28a745",
            "expired": "#ff9800",
            "terminated": "#dc3545",
        }
        color = colors.get(obj.status, "#6c757d")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display(),
        )
    
    def is_active(self, obj):
        """Sözleşme aktif mi?"""
        from django.utils import timezone
        if obj.status != 'active':
            return False
        if obj.end_date and obj.end_date < timezone.now().date():
            return False
        return True
    is_active.boolean = True
    is_active.short_description = "Aktif"


@admin.register(AdvisorTimeTracking)
class AdvisorTimeTrackingAdmin(admin.ModelAdmin):
    list_display = (
        "advisor",
        "taxpayer",
        "date",
        "start_time",
        "end_time",
        "duration_display",
        "hourly_rate",
        "total_amount",
        "billable",
        "invoiced",
    )
    list_filter = ("billable", "invoiced", "date", "service_category")
    search_fields = ("advisor__user__username", "taxpayer__name", "task_description", "service_category")
    readonly_fields = ("total_amount", "created_at")
    date_hierarchy = "date"
    
    fieldsets = (
        (_("Taraflar"), {
            "fields": ("advisor", "taxpayer", "session")
        }),
        (_("Zaman"), {
            "fields": ("date", "start_time", "end_time", "duration_minutes", "duration_display")
        }),
        (_("İş Detayı"), {
            "fields": ("task_description", "service_category")
        }),
        (_("Faturalandırma"), {
            "fields": ("billable", "hourly_rate", "total_amount", "invoiced", "invoice_reference")
        }),
        (_("Bilgiler"), {
            "fields": ("created_at",),
            "classes": ("collapse",)
        }),
    )
    
    def duration_display(self, obj):
        """Süre gösterimi"""
        hours = obj.duration_minutes // 60
        minutes = obj.duration_minutes % 60
        if hours > 0:
            return f"{hours}s {minutes}dk"
        return f"{minutes}dk"
    duration_display.short_description = "Süre"


@admin.register(ClientDocument)
class ClientDocumentAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "taxpayer",
        "document_type",
        "uploaded_by",
        "document_date",
        "is_confidential",
        "file_size_display",
        "uploaded_at",
    )
    list_filter = ("document_type", "is_confidential", "document_date", "uploaded_at")
    search_fields = ("title", "description", "taxpayer__name", "tags")
    readonly_fields = ("uploaded_at", "file_size", "file_size_display", "access_log_display")
    date_hierarchy = "uploaded_at"
    
    fieldsets = (
        (_("Doküman Bilgisi"), {
            "fields": ("taxpayer", "uploaded_by", "document_type", "title", "description")
        }),
        (_("Dosya"), {
            "fields": ("file", "file_size_display", "document_date")
        }),
        (_("Etiketler ve Güvenlik"), {
            "fields": ("tags", "is_confidential", "access_log_display")
        }),
        (_("Bilgiler"), {
            "fields": ("uploaded_at",),
            "classes": ("collapse",)
        }),
    )
    
    def file_size_display(self, obj):
        """Dosya boyutu gösterimi"""
        if obj.file_size:
            if obj.file_size < 1024:
                return f"{obj.file_size} B"
            elif obj.file_size < 1024 * 1024:
                return f"{obj.file_size / 1024:.2f} KB"
            else:
                return f"{obj.file_size / (1024 * 1024):.2f} MB"
        return "-"
    file_size_display.short_description = "Dosya Boyutu"
    
    def access_log_display(self, obj):
        """Erişim logu gösterimi"""
        if obj.access_log:
            return f"{len(obj.access_log)} erişim kaydı"
        return "Henüz erişim yok"
    access_log_display.short_description = "Erişim Logu"


@admin.register(AdvisorTask)
class AdvisorTaskAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "advisor",
        "taxpayer",
        "task_type",
        "priority_badge",
        "due_date",
        "is_completed",
        "days_until_due",
    )
    list_filter = ("task_type", "priority", "is_completed", "due_date")
    search_fields = ("title", "description", "advisor__user__username", "taxpayer__name")
    readonly_fields = ("created_at", "completed_at", "days_until_due")
    date_hierarchy = "due_date"
    
    fieldsets = (
        (_("Görev Bilgisi"), {
            "fields": ("advisor", "taxpayer", "task_type", "title", "description")
        }),
        (_("Öncelik ve Tarih"), {
            "fields": ("priority", "due_date", "days_until_due")
        }),
        (_("Durum"), {
            "fields": ("is_completed", "completed_at", "completion_notes")
        }),
        (_("Bildirimler"), {
            "fields": ("reminder_sent", "reminder_date")
        }),
        (_("Bilgiler"), {
            "fields": ("created_at",),
            "classes": ("collapse",)
        }),
    )
    
    @admin.display(description="Öncelik")
    def priority_badge(self, obj):
        """Öncelik badge"""
        colors = {
            "low": "#6c757d",
            "medium": "#17a2b8",
            "high": "#ffc107",
            "urgent": "#dc3545",
        }
        color = colors.get(obj.priority, "#6c757d")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_priority_display(),
        )
    
    def days_until_due(self, obj):
        """Kalan gün sayısı"""
        from django.utils import timezone
        if obj.is_completed:
            return "Tamamlandı"
        if obj.due_date:
            delta = obj.due_date - timezone.now().date()
            days = delta.days
            if days < 0:
                return f"{abs(days)} gün geçmiş"
            elif days == 0:
                return "Bugün"
            else:
                return f"{days} gün kaldı"
        return "-"
    days_until_due.short_description = "Kalan Süre"
    
    actions = ["mark_as_completed", "mark_as_incomplete"]
    
    @admin.action(description="Seçili görevleri tamamlandı olarak işaretle")
    def mark_as_completed(self, request, queryset):
        from django.utils import timezone
        count = queryset.filter(is_completed=False).update(
            is_completed=True,
            completed_at=timezone.now()
        )
        self.message_user(request, f"{count} görev tamamlandı olarak işaretlendi.")
    
    @admin.action(description="Seçili görevleri tamamlanmadı olarak işaretle")
    def mark_as_incomplete(self, request, queryset):
        count = queryset.filter(is_completed=True).update(
            is_completed=False,
            completed_at=None
        )
        self.message_user(request, f"{count} görev tamamlanmadı olarak işaretlendi.")
