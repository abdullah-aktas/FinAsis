# -*- coding: utf-8 -*-
"""
Mali Müşavir Marketplace Admin
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone

from ..models_marketplace import (
    ConsultantProfile,
    ConsultantService,
    ConsultationBooking,
    ConsultationPayment,
    ConsultantContract,
    ConsultantReview,
    ConsultantAvailability,
    ConsultantDocument,
    ConsultantPayout
)


@admin.register(ConsultantProfile)
class ConsultantProfileAdmin(admin.ModelAdmin):
    """Mali Müşavir Profili Admin"""
    list_display = [
        'display_name', 'city', 'approval_status_badge', 'availability_status',
        'hourly_rate', 'average_rating', 'total_consultations', 'is_featured'
    ]
    list_filter = [
        'approval_status', 'availability_status', 'city', 
        'is_featured', 'accepts_new_clients', 'instant_booking'
    ]
    search_fields = ['display_name', 'advisor__user__username', 'phone', 'city']
    readonly_fields = [
        'total_consultations', 'completed_consultations', 
        'total_earnings', 'average_rating', 'total_reviews',
        'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('Danışman Bilgisi', {
            'fields': ('advisor', 'display_name', 'bio', 'profile_photo')
        }),
        ('Zorunlu Belgeler', {
            'fields': (
                'diploma_document', 'graduation_document',
                'diploma_verified', 'graduation_verified',
                'documents_verified_at', 'documents_verified_by'
            ),
            'classes': ('wide',)
        }),
        ('Blockchain Anlaşma', {
            'fields': (
                'blockchain_contract_address', 'blockchain_transaction_hash',
                'blockchain_contract_created_at', 'blockchain_contract_terms'
            ),
            'classes': ('collapse',)
        }),
        ('Onay ve Durum', {
            'fields': (
                'approval_status', 'approved_by', 'approved_at',
                'rejection_reason', 'availability_status'
            )
        }),
        ('İletişim', {
            'fields': ('office_address', 'city', 'phone', 'website')
        }),
        ('Uzmanlık', {
            'fields': (
                'specializations', 'languages', 'years_of_experience',
                'education', 'certifications'
            )
        }),
        ('Fiyatlandırma', {
            'fields': ('hourly_rate', 'currency', 'commission_rate')
        }),
        ('Müsaitlik', {
            'fields': ('working_hours', 'accepts_new_clients', 'instant_booking')
        }),
        ('İstatistikler', {
            'fields': (
                'total_consultations', 'completed_consultations',
                'total_earnings', 'average_rating', 'total_reviews'
            )
        }),
        ('Öne Çıkarma', {
            'fields': ('is_featured', 'featured_until')
        }),
        ('Meta', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    actions = ['approve_consultants', 'approve_and_blockchain', 'verify_consultant_documents', 'reject_consultants', 'feature_consultants']
    
    @admin.display(description='Onay Durumu')
    def approval_status_badge(self, obj):
        """Onay durumu badge"""
        colors = {
            'pending': '#ffc107',
            'under_review': '#17a2b8',
            'approved': '#28a745',
            'rejected': '#dc3545',
            'suspended': '#6c757d',
            'banned': '#000000',
        }
        color = colors.get(obj.approval_status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_approval_status_display()
        )
    
    def approve_consultants(self, request, queryset):
        """Seçili mali müşavirleri onayla ve blockchain anlaşması oluştur"""
        from advisors.services.blockchain_service import create_agreement_on_approval
        
        count = 0
        for consultant in queryset.filter(approval_status__in=['pending', 'under_review']):
            # Belgeler doğrulanmış mı kontrol et
            if not consultant.documents_all_verified():
                self.message_user(
                    request,
                    f'{consultant.display_name}: Belgeler henüz doğrulanmamış!',
                    level='WARNING'
                )
                continue
            
            # Onay ver
            consultant.approval_status = 'approved'
            consultant.approved_by = request.user
            consultant.approved_at = timezone.now()
            consultant.save()
            
            # Blockchain anlaşması oluştur
            try:
                result = create_agreement_on_approval(consultant, request.user)
                self.message_user(
                    request,
                    f'{consultant.display_name}: Onaylandı ve blockchain anlaşması oluşturuldu. '
                    f'Contract: {result["contract_address"][:16]}...',
                    level='SUCCESS'
                )
                count += 1
            except Exception as e:
                self.message_user(
                    request,
                    f'{consultant.display_name}: Blockchain anlaşması oluşturulamadı: {str(e)}',
                    level='ERROR'
                )
        
        if count > 0:
            self.message_user(request, f'{count} mali müşavir onaylandı ve blockchain anlaşması yapıldı.')
    
    @admin.action(description='Seçili mali müşavirleri reddet')
    def reject_consultants(self, request, queryset):
        """Seçili mali müşavirleri reddet"""
        count = queryset.filter(
            approval_status__in=['pending', 'under_review']
        ).update(approval_status='rejected')
        self.message_user(request, f'{count} mali müşavir reddedildi.')
    
    @admin.action(description='Seçili mali müşavirleri öne çıkar (30 gün)')
    def feature_consultants(self, request, queryset):
        """Seçili mali müşavirleri öne çıkar (30 gün)"""
        from datetime import timedelta
        featured_until = timezone.now() + timedelta(days=30)
        count = queryset.update(is_featured=True, featured_until=featured_until)
        self.message_user(request, f'{count} mali müşavir 30 gün için öne çıkarıldı.')
    
    def verify_documents(self, request, queryset):
        """Seçili mali müşavirlerin belgelerini doğrula"""
        count = 0
        for consultant in queryset:
            if consultant.documents_complete():
                consultant.diploma_verified = True
                consultant.graduation_verified = True
                consultant.documents_verified_at = timezone.now()
                consultant.documents_verified_by = request.user
                consultant.save()
                count += 1
        self.message_user(request, f'{count} mali müşavirin belgeleri doğrulandı.')


@admin.register(ConsultantService)
class ConsultantServiceAdmin(admin.ModelAdmin):
    """Mali Müşavir Hizmeti Admin"""
    list_display = [
        'title', 'consultant', 'category', 'pricing_type',
        'price', 'is_active', 'total_orders'
    ]
    list_filter = ['category', 'pricing_type', 'is_active']
    search_fields = ['title', 'description', 'consultant__display_name']
    readonly_fields = ['total_orders']
    
    fieldsets = (
        ('Hizmet Bilgisi', {
            'fields': ('consultant', 'title', 'category', 'description')
        }),
        ('Fiyatlandırma', {
            'fields': ('pricing_type', 'price', 'currency')
        }),
        ('Süre ve Teslimat', {
            'fields': ('duration_minutes', 'estimated_delivery_days')
        }),
        ('Detaylar', {
            'fields': ('includes', 'is_active', 'total_orders')
        }),
    )


@admin.register(ConsultationBooking)
class ConsultationBookingAdmin(admin.ModelAdmin):
    """Danışmanlık Randevusu Admin"""
    list_display = [
        'booking_number', 'client', 'consultant', 'scheduled_date',
        'scheduled_time', 'status_badge', 'payment_status', 'quoted_price'
    ]
    list_filter = [
        'status', 'meeting_type', 'payment_status', 
        'scheduled_date', 'created_at'
    ]
    search_fields = [
        'booking_number', 'client__username', 'consultant__display_name',
        'subject'
    ]
    readonly_fields = [
        'booking_number', 'commission_amount', 'consultant_earning',
        'education_meeting', 'created_at', 'updated_at'
    ]
    date_hierarchy = 'scheduled_date'
    
    fieldsets = (
        ('Randevu Bilgisi', {
            'fields': (
                'booking_number', 'client', 'consultant', 'service',
                'meeting_type', 'subject', 'description'
            )
        }),
        ('Zamanlama', {
            'fields': (
                'scheduled_date', 'scheduled_time', 'duration_minutes',
                'timezone', 'actual_start_time', 'actual_end_time'
            )
        }),
        ('Durum', {
            'fields': ('status', 'payment_status', 'reminder_sent', 'reminder_sent_at')
        }),
        ('Görüşme Detayları', {
            'fields': (
                'video_provider', 'meeting_url', 'meeting_id', 'meeting_password',
                'education_meeting', 'meeting_address', 'consultant_notes'
            )
        }),
        ('Fiyatlandırma', {
            'fields': (
                'quoted_price', 'final_price', 'commission_amount',
                'consultant_earning', 'paid_at'
            )
        }),
        ('İptal', {
            'fields': ('cancellation_reason', 'cancelled_at'),
            'classes': ('collapse',)
        }),
        ('Meta', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    @admin.display(description='Durum')
    def status_badge(self, obj):
        """Durum badge"""
        colors = {
            'pending': '#ffc107',
            'confirmed': '#28a745',
            'completed': '#17a2b8',
            'cancelled_by_client': '#dc3545',
            'cancelled_by_consultant': '#dc3545',
            'no_show': '#6c757d',
            'rescheduled': '#ff9800',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )


@admin.register(ConsultationPayment)
class ConsultationPaymentAdmin(admin.ModelAdmin):
    """Danışmanlık Ödemesi Admin"""
    list_display = [
        'id', 'booking', 'client', 'consultant',
        'amount', 'commission', 'consultant_amount',
        'status', 'paid_at'
    ]
    list_filter = ['status', 'payment_method', 'payment_type', 'paid_at']
    search_fields = [
        'booking__booking_number', 'client__username',
        'consultant__display_name', 'transaction_id'
    ]
    readonly_fields = ['paid_at', 'payout_to_consultant_at', 'refunded_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Ödeme Bilgisi', {
            'fields': (
                'booking', 'client', 'consultant',
                'payment_type', 'payment_method'
            )
        }),
        ('Tutarlar', {
            'fields': (
                'amount', 'commission', 'consultant_amount', 'currency'
            )
        }),
        ('Durum', {
            'fields': ('status', 'paid_at', 'payout_to_consultant_at')
        }),
        ('Gateway', {
            'fields': ('gateway_name', 'transaction_id', 'gateway_response')
        }),
        ('İade', {
            'fields': ('refund_amount', 'refund_reason', 'refunded_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ConsultantContract)
class ConsultantContractAdmin(admin.ModelAdmin):
    """Mali Müşavir Sözleşmesi Admin"""
    list_display = [
        'contract_number', 'client', 'consultant',
        'contract_type', 'contract_value', 'status',
        'start_date', 'end_date'
    ]
    list_filter = ['status', 'contract_type', 'start_date', 'auto_renew']
    search_fields = [
        'contract_number', 'client__username',
        'consultant__display_name', 'title'
    ]
    readonly_fields = [
        'contract_number', 'client_signed_at', 'consultant_signed_at',
        'client_ip', 'consultant_ip', 'created_at', 'updated_at'
    ]
    date_hierarchy = 'start_date'
    
    fieldsets = (
        ('Sözleşme Bilgisi', {
            'fields': (
                'contract_number', 'client', 'consultant',
                'contract_type', 'title'
            )
        }),
        ('İçerik', {
            'fields': (
                'scope_of_work', 'terms_and_conditions',
                'deliverables'
            )
        }),
        ('Finansal', {
            'fields': (
                'contract_value', 'payment_terms', 'payment_schedule'
            )
        }),
        ('Tarihler', {
            'fields': (
                'start_date', 'end_date', 'auto_renew', 'renewal_notice_days'
            )
        }),
        ('Durum', {
            'fields': ('status',)
        }),
        ('İmzalar', {
            'fields': (
                'client_signed_at', 'client_ip',
                'consultant_signed_at', 'consultant_ip'
            )
        }),
        ('Dosyalar', {
            'fields': (
                'contract_document', 'signed_document', 'attachments'
            )
        }),
        ('Fesih', {
            'fields': (
                'termination_reason', 'terminated_by', 'terminated_at'
            ),
            'classes': ('collapse',)
        }),
    )


@admin.register(ConsultantReview)
class ConsultantReviewAdmin(admin.ModelAdmin):
    """Mali Müşavir Değerlendirmesi Admin"""
    list_display = [
        'consultant', 'client', 'rating', 'title',
        'is_published', 'is_verified', 'is_featured',
        'created_at'
    ]
    list_filter = [
        'rating', 'is_published', 'is_verified', 
        'is_featured', 'created_at'
    ]
    search_fields = [
        'consultant__display_name', 'client__username',
        'title', 'comment'
    ]
    readonly_fields = [
        'consultant_responded_at', 'helpful_count',
        'not_helpful_count', 'created_at', 'updated_at'
    ]
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Değerlendirme', {
            'fields': (
                'consultant', 'client', 'booking',
                'rating', 'title', 'comment'
            )
        }),
        ('Detaylı Puanlar', {
            'fields': (
                'professionalism_rating', 'communication_rating',
                'expertise_rating', 'value_rating'
            )
        }),
        ('Mali Müşavir Yanıtı', {
            'fields': ('consultant_response', 'consultant_responded_at')
        }),
        ('Durum', {
            'fields': (
                'is_verified', 'is_featured', 'is_published'
            )
        }),
        ('Faydalılık', {
            'fields': ('helpful_count', 'not_helpful_count')
        }),
    )
    
    actions = ['publish_reviews', 'feature_reviews']
    
    @admin.action(description='Seçili değerlendirmeleri yayınla')
    def publish_reviews(self, request, queryset):
        count = queryset.update(is_published=True)
        self.message_user(request, f'{count} değerlendirme yayınlandı.')
    
    @admin.action(description='Seçili değerlendirmeleri öne çıkar')
    def feature_reviews(self, request, queryset):
        count = queryset.update(is_featured=True)
        self.message_user(request, f'{count} değerlendirme öne çıkarıldı.')


@admin.register(ConsultantAvailability)
class ConsultantAvailabilityAdmin(admin.ModelAdmin):
    """Mali Müşavir Müsaitlik Admin"""
    list_display = [
        'consultant', 'day_of_week', 'start_time', 'end_time',
        'is_available', 'is_recurring', 'specific_date'
    ]
    list_filter = ['day_of_week', 'is_available', 'is_recurring']
    search_fields = ['consultant__display_name']


@admin.register(ConsultantDocument)
class ConsultantDocumentAdmin(admin.ModelAdmin):
    """Mali Müşavir Belgesi Admin"""
    list_display = [
        'consultant', 'document_type', 'title',
        'verification_status_badge', 'issue_date',
        'expiry_date', 'is_expired_badge'
    ]
    list_filter = [
        'document_type', 'verification_status',
        'issue_date', 'expiry_date'
    ]
    search_fields = ['consultant__display_name', 'title']
    readonly_fields = ['file_size', 'uploaded_at']
    
    fieldsets = (
        ('Belge Bilgisi', {
            'fields': (
                'consultant', 'document_type', 'title',
                'description', 'file', 'file_size'
            )
        }),
        ('Doğrulama', {
            'fields': (
                'verification_status', 'verified_by', 'verified_at',
                'rejection_reason'
            )
        }),
        ('Geçerlilik', {
            'fields': ('issue_date', 'expiry_date')
        }),
    )
    
    actions = ['verify_documents', 'reject_documents']
    
    @admin.display(description='Doğrulama Durumu')
    def verification_status_badge(self, obj):
        colors = {
            'pending': '#ffc107',
            'verified': '#28a745',
            'rejected': '#dc3545',
        }
        color = colors.get(obj.verification_status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_verification_status_display()
        )
    
    @admin.display(description='Geçerlilik')
    def is_expired_badge(self, obj):
        if obj.is_expired():
            return format_html(
                '<span style="color: red; font-weight: bold;">SÜRESİ DOLMUŞ</span>'
            )
        return format_html(
            '<span style="color: green;">Geçerli</span>'
        )
    
    @admin.action(description='Seçili belgeleri doğrula')
    def verify_documents(self, request, queryset):
        count = 0
        for doc in queryset.filter(verification_status='pending'):
            doc.verification_status = 'verified'
            doc.verified_by = request.user
            doc.verified_at = timezone.now()
            doc.save()
            count += 1
        self.message_user(request, f'{count} belge doğrulandı.')
    
    @admin.action(description='Seçili belgeleri reddet')
    def reject_documents(self, request, queryset):
        count = queryset.filter(verification_status='pending').update(
            verification_status='rejected'
        )
        self.message_user(request, f'{count} belge reddedildi.')


@admin.register(ConsultantPayout)
class ConsultantPayoutAdmin(admin.ModelAdmin):
    """Mali Müşavir Ödemesi Admin"""
    list_display = [
        'consultant', 'amount', 'period_start', 'period_end',
        'status', 'processed_at'
    ]
    list_filter = ['status', 'processed_at', 'period_start']
    search_fields = [
        'consultant__display_name', 'account_holder',
        'transaction_reference'
    ]
    readonly_fields = ['processed_at', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Mali Müşavir', {
            'fields': ('consultant', 'amount', 'currency')
        }),
        ('Dönem', {
            'fields': ('period_start', 'period_end', 'included_payments')
        }),
        ('Banka Bilgileri', {
            'fields': ('bank_name', 'account_holder', 'iban')
        }),
        ('İşlem', {
            'fields': (
                'status', 'transaction_reference', 'processed_at', 'notes'
            )
        }),
    )
    
    actions = ['mark_as_completed']
    
    @admin.action(description='Seçili ödemeleri tamamlandı olarak işaretle')
    def mark_as_completed(self, request, queryset):
        count = 0
        for payout in queryset.filter(status__in=['pending', 'processing']):
            payout.status = 'completed'
            payout.processed_at = timezone.now()
            payout.save()
            count += 1
        self.message_user(request, f'{count} ödeme tamamlandı olarak işaretlendi.')
