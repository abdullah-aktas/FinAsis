# -*- coding: utf-8 -*-
"""
Mali Müşavir Marketplace Serializers
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal

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

User = get_user_model()


class ConsultantProfileListSerializer(serializers.ModelSerializer):
    """Mali müşavir liste için özet serializer"""
    advisor_name = serializers.CharField(source='advisor.user.get_full_name', read_only=True)
    advisor_type = serializers.CharField(source='advisor.type', read_only=True)
    is_available = serializers.SerializerMethodField()
    
    class Meta:
        model = ConsultantProfile
        fields = [
            'id', 'display_name', 'advisor_name', 'advisor_type',
            'city', 'profile_photo', 'bio', 'specializations',
            'years_of_experience', 'hourly_rate', 'currency',
            'average_rating', 'total_reviews', 'is_featured',
            'is_available', 'availability_status'
        ]
    
    def get_is_available(self, obj):
        return obj.is_available()


class ConsultantProfileDetailSerializer(serializers.ModelSerializer):
    """Mali müşavir detay serializer"""
    advisor_info = serializers.SerializerMethodField()
    services = serializers.SerializerMethodField()
    reviews_summary = serializers.SerializerMethodField()
    
    class Meta:
        model = ConsultantProfile
        fields = [
            'id', 'advisor_info', 'display_name', 'bio', 'profile_photo',
            'office_address', 'city', 'phone', 'website',
            'specializations', 'languages', 'years_of_experience',
            'education', 'certifications',
            'hourly_rate', 'currency', 'commission_rate',
            'availability_status', 'working_hours',
            'total_consultations', 'completed_consultations',
            'average_rating', 'total_reviews',
            'is_featured', 'accepts_new_clients', 'instant_booking',
            'services', 'reviews_summary', 'created_at'
        ]
    
    def get_advisor_info(self, obj):
        return {
            'user_id': obj.advisor.user.id,
            'username': obj.advisor.user.username,
            'full_name': obj.advisor.user.get_full_name(),
            'type': obj.advisor.type,
            'chamber_no': obj.advisor.chamber_no,
        }
    
    def get_services(self, obj):
        services = obj.services.filter(is_active=True)
        return ConsultantServiceSerializer(services, many=True).data
    
    def get_reviews_summary(self, obj):
        return {
            'average_rating': float(obj.average_rating),
            'total_reviews': obj.total_reviews,
            'rating_distribution': self._get_rating_distribution(obj)
        }
    
    def _get_rating_distribution(self, obj):
        """Puan dağılımını hesapla"""
        from django.db.models import Count
        distribution = obj.reviews.values('rating').annotate(count=Count('id'))
        result = {i: 0 for i in range(1, 6)}
        for item in distribution:
            result[item['rating']] = item['count']
        return result


class ConsultantProfileCreateSerializer(serializers.ModelSerializer):
    """Mali müşavir profili oluşturma"""
    
    class Meta:
        model = ConsultantProfile
        fields = [
            'display_name', 'bio', 'profile_photo',
            'office_address', 'city', 'phone', 'website',
            'specializations', 'languages', 'years_of_experience',
            'education', 'certifications', 'hourly_rate',
            'working_hours', 'accepts_new_clients', 'instant_booking',
            'diploma_document', 'graduation_document'  # Zorunlu belgeler
        ]
    
    def validate_hourly_rate(self, value):
        if value <= 0:
            raise serializers.ValidationError("Saatlik ücret pozitif olmalıdır.")
        return value
    
    def validate(self, attrs):
        # Zorunlu belgelerin yüklendiğini kontrol et
        if not attrs.get('diploma_document'):
            raise serializers.ValidationError({
                'diploma_document': 'Diploma/Mezuniyet belgesi zorunludur.'
            })
        if not attrs.get('graduation_document'):
            raise serializers.ValidationError({
                'graduation_document': 'Mezuniyet belgesi zorunludur.'
            })
        return attrs
    
    def create(self, validated_data):
        # AdvisorProfile'dan mali müşavir al
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            advisor = request.user.advisor_profile
            validated_data['advisor'] = advisor
        return super().create(validated_data)


class ConsultantServiceSerializer(serializers.ModelSerializer):
    """Mali müşavir hizmet serializer"""
    consultant_name = serializers.CharField(source='consultant.display_name', read_only=True)
    
    class Meta:
        model = ConsultantService
        fields = [
            'id', 'consultant', 'consultant_name', 'title', 'category',
            'description', 'pricing_type', 'price', 'currency',
            'duration_minutes', 'estimated_delivery_days',
            'includes', 'is_active', 'total_orders'
        ]
        read_only_fields = ['consultant', 'total_orders']


class ConsultationBookingSerializer(serializers.ModelSerializer):
    """Randevu serializer"""
    client_name = serializers.CharField(source='client.get_full_name', read_only=True)
    consultant_name = serializers.CharField(source='consultant.display_name', read_only=True)
    consultant_photo = serializers.ImageField(source='consultant.profile_photo', read_only=True)
    service_name = serializers.CharField(source='service.title', read_only=True)
    
    class Meta:
        model = ConsultationBooking
        fields = [
            'id', 'booking_number', 'client', 'client_name',
            'consultant', 'consultant_name', 'consultant_photo',
            'service', 'service_name', 'meeting_type', 'video_provider',
            'scheduled_date', 'scheduled_time', 'duration_minutes',
            'timezone', 'status', 'subject', 'description',
            'meeting_url', 'meeting_id', 'meeting_password',
            'education_meeting', 'meeting_address',
            'quoted_price', 'final_price', 'payment_status',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'booking_number', 'client', 'meeting_url', 'meeting_id',
            'education_meeting', 'commission_amount',
            'consultant_earning', 'payment_status'
        ]
    
    def validate(self, attrs):
        # Randevu tarihi geçmişte olamaz
        scheduled_datetime = timezone.datetime.combine(
            attrs['scheduled_date'],
            attrs['scheduled_time']
        )
        if scheduled_datetime < timezone.now():
            raise serializers.ValidationError("Geçmiş bir tarih için randevu oluşturamazsınız.")
        
        # Mali müşavirin müsait olup olmadığını kontrol et
        consultant = attrs.get('consultant')
        if consultant and not consultant.is_available():
            raise serializers.ValidationError("Bu mali müşavir şu anda müşteri kabul etmiyor.")
        
        return attrs
    
    def create(self, validated_data):
        # Booking number oluştur
        import uuid
        validated_data['booking_number'] = f"BK-{uuid.uuid4().hex[:8].upper()}"
        
        # Client'ı context'ten al
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            validated_data['client'] = request.user
        
        # Anında rezervasyon kontrolü
        if validated_data['consultant'].instant_booking:
            validated_data['status'] = 'confirmed'
        else:
            validated_data['status'] = 'pending'
        
        booking = super().create(validated_data)
        
        # Komisyon hesapla
        booking.calculate_commission()

        # Anında onaylanan online randevular için toplantı oluştur
        if booking.status == 'confirmed':
            booking.ensure_online_meeting()
        
        return booking


class ConsultationBookingUpdateSerializer(serializers.ModelSerializer):
    """Randevu güncelleme (mali müşavir için)"""
    
    class Meta:
        model = ConsultationBooking
        fields = [
            'status', 'video_provider', 'meeting_url', 'meeting_id', 'meeting_password',
            'consultant_notes', 'actual_start_time', 'actual_end_time',
            'final_price'
        ]
    
    def validate_status(self, value):
        # Duruma göre validasyon kuralları
        if value == 'completed' and self.instance and not self.instance.actual_end_time:
            raise serializers.ValidationError("Randevuyu tamamlamak için bitiş zamanı gereklidir.")
        return value


class ConsultationPaymentSerializer(serializers.ModelSerializer):
    """Ödeme serializer"""
    booking_info = serializers.SerializerMethodField()
    
    class Meta:
        model = ConsultationPayment
        fields = [
            'id', 'booking', 'booking_info', 'client', 'consultant',
            'payment_type', 'payment_method', 'amount', 'commission',
            'consultant_amount', 'currency', 'status',
            'transaction_id', 'paid_at', 'payout_to_consultant_at',
            'created_at'
        ]
        read_only_fields = [
            'commission', 'consultant_amount', 'status',
            'paid_at', 'payout_to_consultant_at'
        ]
    
    def get_booking_info(self, obj):
        return {
            'booking_number': obj.booking.booking_number,
            'scheduled_date': obj.booking.scheduled_date,
            'subject': obj.booking.subject
        }


class ConsultantContractSerializer(serializers.ModelSerializer):
    """Sözleşme serializer"""
    client_name = serializers.CharField(source='client.get_full_name', read_only=True)
    consultant_name = serializers.CharField(source='consultant.display_name', read_only=True)
    is_fully_signed = serializers.SerializerMethodField()
    
    class Meta:
        model = ConsultantContract
        fields = [
            'id', 'contract_number', 'client', 'client_name',
            'consultant', 'consultant_name', 'contract_type',
            'title', 'scope_of_work', 'terms_and_conditions',
            'deliverables', 'contract_value', 'payment_terms',
            'payment_schedule', 'start_date', 'end_date',
            'status', 'client_signed_at', 'consultant_signed_at',
            'is_fully_signed', 'contract_document', 'signed_document',
            'auto_renew', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'contract_number', 'client_signed_at', 'consultant_signed_at',
            'signed_document'
        ]
    
    def get_is_fully_signed(self, obj):
        return obj.is_fully_signed()
    
    def create(self, validated_data):
        # Contract number oluştur
        import uuid
        validated_data['contract_number'] = f"CT-{timezone.now().year}-{uuid.uuid4().hex[:6].upper()}"
        return super().create(validated_data)


class ConsultantReviewSerializer(serializers.ModelSerializer):
    """Değerlendirme serializer"""
    client_name = serializers.CharField(source='client.get_full_name', read_only=True)
    booking_info = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    
    class Meta:
        model = ConsultantReview
        fields = [
            'id', 'consultant', 'client', 'client_name', 'booking',
            'booking_info', 'rating', 'professionalism_rating',
            'communication_rating', 'expertise_rating', 'value_rating',
            'average_rating', 'title', 'comment',
            'consultant_response', 'consultant_responded_at',
            'is_verified', 'is_featured', 'is_published',
            'helpful_count', 'not_helpful_count', 'created_at'
        ]
        read_only_fields = [
            'client', 'consultant_response', 'consultant_responded_at',
            'is_verified', 'is_featured', 'helpful_count', 'not_helpful_count'
        ]
    
    def get_booking_info(self, obj):
        return {
            'booking_number': obj.booking.booking_number,
            'scheduled_date': obj.booking.scheduled_date,
            'subject': obj.booking.subject
        }
    
    def get_average_rating(self, obj):
        """Tüm kategorilerin ortalaması"""
        total = (
            obj.professionalism_rating +
            obj.communication_rating +
            obj.expertise_rating +
            obj.value_rating
        )
        return round(total / 4, 2)
    
    def validate(self, attrs):
        # Sadece tamamlanmış randevular için değerlendirme yapılabilir
        booking = attrs.get('booking')
        if booking and booking.status != 'completed':
            raise serializers.ValidationError("Sadece tamamlanmış randevular için değerlendirme yapabilirsiniz.")
        
        # Müşteri daha önce değerlendirme yapmış mı?
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            if ConsultantReview.objects.filter(booking=booking, client=request.user).exists():
                raise serializers.ValidationError("Bu randevu için zaten değerlendirme yaptınız.")
        
        return attrs
    
    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            validated_data['client'] = request.user
        validated_data['consultant'] = validated_data['booking'].consultant
        return super().create(validated_data)


class ConsultantAvailabilitySerializer(serializers.ModelSerializer):
    """Müsaitlik serializer"""
    day_name = serializers.CharField(source='get_day_of_week_display', read_only=True)
    
    class Meta:
        model = ConsultantAvailability
        fields = [
            'id', 'consultant', 'day_of_week', 'day_name',
            'start_time', 'end_time', 'specific_date',
            'is_available', 'is_recurring'
        ]
        read_only_fields = ['consultant']
    
    def validate(self, attrs):
        # Başlangıç saati bitiş saatinden önce olmalı
        if attrs['start_time'] >= attrs['end_time']:
            raise serializers.ValidationError("Başlangıç saati bitiş saatinden önce olmalıdır.")
        
        return attrs


class ConsultantDocumentSerializer(serializers.ModelSerializer):
    """Belge serializer"""
    is_expired = serializers.SerializerMethodField()
    
    class Meta:
        model = ConsultantDocument
        fields = [
            'id', 'consultant', 'document_type', 'title', 'description',
            'file', 'file_size', 'verification_status',
            'issue_date', 'expiry_date', 'is_expired', 'uploaded_at'
        ]
        read_only_fields = [
            'consultant', 'verification_status', 'verified_by',
            'verified_at', 'file_size'
        ]
    
    def get_is_expired(self, obj):
        return obj.is_expired()


class ConsultantPayoutSerializer(serializers.ModelSerializer):
    """Mali müşavir ödemesi serializer"""
    consultant_name = serializers.CharField(source='consultant.display_name', read_only=True)
    
    class Meta:
        model = ConsultantPayout
        fields = [
            'id', 'consultant', 'consultant_name', 'amount', 'currency',
            'period_start', 'period_end', 'included_payments',
            'bank_name', 'account_holder', 'iban',
            'status', 'transaction_reference', 'processed_at',
            'notes', 'created_at'
        ]
        read_only_fields = [
            'status', 'transaction_reference', 'processed_at'
        ]


# ============================================================================
# İSTATİSTİK VE DASHBOARD SERİALİZERLERI
# ============================================================================

class ConsultantDashboardSerializer(serializers.Serializer):
    """Mali müşavir dashboard istatistikleri"""
    total_earnings = serializers.DecimalField(max_digits=12, decimal_places=2)
    pending_earnings = serializers.DecimalField(max_digits=12, decimal_places=2)
    this_month_earnings = serializers.DecimalField(max_digits=12, decimal_places=2)
    
    total_consultations = serializers.IntegerField()
    completed_consultations = serializers.IntegerField()
    upcoming_bookings = serializers.IntegerField()
    pending_bookings = serializers.IntegerField()
    
    average_rating = serializers.DecimalField(max_digits=3, decimal_places=2)
    total_reviews = serializers.IntegerField()
    
    active_clients = serializers.IntegerField()
    total_clients = serializers.IntegerField()


class ClientDashboardSerializer(serializers.Serializer):
    """Müşteri dashboard istatistikleri"""
    total_bookings = serializers.IntegerField()
    completed_bookings = serializers.IntegerField()
    upcoming_bookings = serializers.IntegerField()
    
    total_spent = serializers.DecimalField(max_digits=12, decimal_places=2)
    this_month_spent = serializers.DecimalField(max_digits=12, decimal_places=2)
    
    active_contracts = serializers.IntegerField()
    favorite_consultants = serializers.ListField()
