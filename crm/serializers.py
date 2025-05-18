# -*- coding: utf-8 -*-
from rest_framework import serializers
from django.utils import timezone
from django.core.exceptions import ValidationError
from .models import (
    Customer, Contact, Opportunity, Activity,
    Document, Communication, Note
)

class CustomerSerializer(serializers.ModelSerializer):
    """Müşteri serializer'ı"""
    risk_level_display = serializers.CharField(source='get_risk_level_display', read_only=True)
    industry_display = serializers.CharField(source='get_industry_display', read_only=True)
    total_opportunities = serializers.SerializerMethodField()
    total_activities = serializers.SerializerMethodField()
    total_documents = serializers.SerializerMethodField()
    total_communications = serializers.SerializerMethodField()
    total_notes = serializers.SerializerMethodField()
    last_activity = serializers.SerializerMethodField()
    next_activity = serializers.SerializerMethodField()
    credit_score_category = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = [
            'id', 'company_name', 'tax_number', 'tax_office',
            'address', 'phone', 'email', 'website',
            'industry', 'industry_display', 'employee_count',
            'annual_revenue', 'credit_score', 'credit_score_category',
            'risk_level', 'risk_level_display', 'is_active',
            'total_opportunities', 'total_activities',
            'total_documents', 'total_communications',
            'total_notes', 'last_activity', 'next_activity',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_total_opportunities(self, obj):
        return obj.opportunities.count()

    def get_total_activities(self, obj):
        return Activity.objects.filter(opportunity__customer=obj).count()

    def get_total_documents(self, obj):
        return obj.documents.count()

    def get_total_communications(self, obj):
        return obj.communications.count()

    def get_total_notes(self, obj):
        return obj.notes.count()

    def get_last_activity(self, obj):
        last_activity = Activity.objects.filter(
            opportunity__customer=obj
        ).order_by('-created_at').first()
        if last_activity:
            return {
                'id': last_activity.id,
                'subject': last_activity.subject,
                'type': last_activity.get_type_display(),
                'created_at': last_activity.created_at
            }
        return None

    def get_next_activity(self, obj):
        next_activity = Activity.objects.filter(
            opportunity__customer=obj,
            completed=False,
            due_date__gt=timezone.now()
        ).order_by('due_date').first()
        if next_activity:
            return {
                'id': next_activity.id,
                'subject': next_activity.subject,
                'type': next_activity.get_type_display(),
                'due_date': next_activity.due_date
            }
        return None

    def get_credit_score_category(self, obj):
        if obj.credit_score >= 800:
            return 'Mükemmel'
        elif obj.credit_score >= 700:
            return 'İyi'
        elif obj.credit_score >= 600:
            return 'Orta'
        elif obj.credit_score >= 500:
            return 'Zayıf'
        return 'Riskli'

    def validate_credit_score(self, value):
        if value < 0 or value > 1000:
            raise ValidationError('Kredi skoru 0-1000 arasında olmalıdır.')
        return value

class ContactSerializer(serializers.ModelSerializer):
    """İletişim kişisi serializer'ı"""
    customer_name = serializers.CharField(source='customer.company_name', read_only=True)
    full_name = serializers.SerializerMethodField()
    position_display = serializers.CharField(source='get_position_display', read_only=True)
    department_display = serializers.CharField(source='get_department_display', read_only=True)

    class Meta:
        model = Contact
        fields = [
            'id', 'customer', 'customer_name', 'first_name',
            'last_name', 'full_name', 'position', 'position_display',
            'department', 'department_display', 'phone', 'mobile',
            'email', 'is_primary', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    def validate(self, data):
        if data.get('is_primary') and Contact.objects.filter(
            customer=data.get('customer'),
            is_primary=True
        ).exclude(id=self.instance.id if self.instance else None).exists():
            raise ValidationError('Bu müşteri için zaten birincil iletişim kişisi tanımlı.')
        return data

class OpportunitySerializer(serializers.ModelSerializer):
    """Fırsat serializer'ı"""
    customer_name = serializers.CharField(source='customer.company_name', read_only=True)
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    stage_display = serializers.CharField(source='get_stage_display', read_only=True)
    probability_percentage = serializers.SerializerMethodField()
    days_to_close = serializers.SerializerMethodField()
    weighted_amount = serializers.SerializerMethodField()
    total_activities = serializers.SerializerMethodField()
    completed_activities = serializers.SerializerMethodField()

    class Meta:
        model = Opportunity
        fields = [
            'id', 'customer', 'customer_name', 'title',
            'description', 'amount', 'probability',
            'probability_percentage', 'stage', 'stage_display',
            'expected_close_date', 'actual_close_date',
            'owner', 'owner_name', 'days_to_close',
            'weighted_amount', 'total_activities',
            'completed_activities', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_probability_percentage(self, obj):
        return f"%{obj.probability}"

    def get_days_to_close(self, obj):
        if obj.expected_close_date:
            delta = obj.expected_close_date - timezone.now().date()
            return delta.days
        return None

    def get_weighted_amount(self, obj):
        return obj.amount * (obj.probability / 100)

    def get_total_activities(self, obj):
        return obj.activities.count()

    def get_completed_activities(self, obj):
        return obj.activities.filter(completed=True).count()

    def validate_probability(self, value):
        if value < 0 or value > 100:
            raise ValidationError('Olasılık 0-100 arasında olmalıdır.')
        return value

    def validate_expected_close_date(self, value):
        if value < timezone.now().date():
            raise ValidationError('Beklenen kapanış tarihi geçmiş bir tarih olamaz.')
        return value

class ActivitySerializer(serializers.ModelSerializer):
    """Aktivite serializer'ı"""
    opportunity_title = serializers.CharField(source='opportunity.title', read_only=True)
    customer_name = serializers.CharField(source='opportunity.customer.company_name', read_only=True)
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    days_until_due = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()

    class Meta:
        model = Activity
        fields = [
            'id', 'opportunity', 'opportunity_title',
            'customer_name', 'type', 'type_display',
            'subject', 'description', 'due_date',
            'completed', 'completed_at', 'assigned_to',
            'assigned_to_name', 'days_until_due',
            'is_overdue', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_days_until_due(self, obj):
        if obj.due_date:
            delta = obj.due_date - timezone.now()
            return delta.days
        return None

    def get_is_overdue(self, obj):
        if obj.due_date and not obj.completed:
            return obj.due_date < timezone.now()
        return False

    def validate_due_date(self, value):
        if value < timezone.now():
            raise ValidationError('Bitiş tarihi geçmiş bir tarih olamaz.')
        return value

class DocumentSerializer(serializers.ModelSerializer):
    """Doküman serializer'ı"""
    customer_name = serializers.CharField(source='customer.company_name', read_only=True)
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    uploaded_by_name = serializers.CharField(source='uploaded_by.get_full_name', read_only=True)
    file_size = serializers.SerializerMethodField()
    file_extension = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = [
            'id', 'customer', 'customer_name', 'title',
            'description', 'file', 'type', 'type_display',
            'uploaded_by', 'uploaded_by_name', 'file_size',
            'file_extension', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_file_size(self, obj):
        if obj.file:
            size = obj.file.size
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024:
                    return f"{size:.2f} {unit}"
                size /= 1024
        return None

    def get_file_extension(self, obj):
        if obj.file:
            return obj.file.name.split('.')[-1].upper()
        return None

class CommunicationSerializer(serializers.ModelSerializer):
    """İletişim kaydı serializer'ı"""
    customer_name = serializers.CharField(source='customer.company_name', read_only=True)
    contact_name = serializers.CharField(source='contact.get_full_name', read_only=True)
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    direction_display = serializers.CharField(source='get_direction_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    duration = serializers.SerializerMethodField()

    class Meta:
        model = Communication
        fields = [
            'id', 'customer', 'customer_name', 'contact',
            'contact_name', 'type', 'type_display', 'subject',
            'content', 'direction', 'direction_display',
            'status', 'status_display', 'created_by',
            'created_by_name', 'duration', 'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_duration(self, obj):
        if obj.duration:
            hours = obj.duration.seconds // 3600
            minutes = (obj.duration.seconds % 3600) // 60
            return f"{hours} saat {minutes} dakika"
        return None

class NoteSerializer(serializers.ModelSerializer):
    """Not serializer'ı"""
    customer_name = serializers.CharField(source='customer.company_name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    is_private_display = serializers.CharField(source='get_is_private_display', read_only=True)
    days_old = serializers.SerializerMethodField()

    class Meta:
        model = Note
        fields = [
            'id', 'customer', 'customer_name', 'title',
            'content', 'is_private', 'is_private_display',
            'created_by', 'created_by_name', 'days_old',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_days_old(self, obj):
        delta = timezone.now() - obj.created_at
        return delta.days 