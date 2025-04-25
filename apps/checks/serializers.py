from rest_framework import serializers
from .models import (
    CheckCategory, CheckType, CheckRule,
    CheckResult, CheckSchedule
)

class CheckCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CheckCategory
        fields = [
            'id', 'name', 'description',
            'priority', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class CheckTypeSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = CheckType
        fields = [
            'id', 'name', 'code', 'description',
            'category', 'category_name', 'severity',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class CheckRuleSerializer(serializers.ModelSerializer):
    check_type_name = serializers.CharField(source='check_type.name', read_only=True)

    class Meta:
        model = CheckRule
        fields = [
            'id', 'check_type', 'check_type_name',
            'name', 'description', 'condition',
            'threshold', 'weight', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_condition(self, value):
        # Koşul doğrulama mantığı buraya eklenecek
        return value

    def validate_threshold(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("Eşik değeri negatif olamaz")
        return value

class CheckResultSerializer(serializers.ModelSerializer):
    check_type_name = serializers.CharField(source='check_type.name', read_only=True)
    check_type_code = serializers.CharField(source='check_type.code', read_only=True)
    check_type_severity = serializers.CharField(source='check_type.severity', read_only=True)

    class Meta:
        model = CheckResult
        fields = [
            'id', 'check_type', 'check_type_name',
            'check_type_code', 'check_type_severity',
            'status', 'score', 'details',
            'started_at', 'completed_at', 'duration',
            'created_at'
        ]
        read_only_fields = [
            'id', 'check_type_name', 'check_type_code',
            'check_type_severity', 'created_at'
        ]

    def validate(self, data):
        if data.get('completed_at') and data.get('started_at'):
            if data['completed_at'] < data['started_at']:
                raise serializers.ValidationError(
                    "Bitiş zamanı başlangıç zamanından önce olamaz"
                )
        return data

class CheckScheduleSerializer(serializers.ModelSerializer):
    check_type_name = serializers.CharField(source='check_type.name', read_only=True)
    check_type_code = serializers.CharField(source='check_type.code', read_only=True)

    class Meta:
        model = CheckSchedule
        fields = [
            'id', 'check_type', 'check_type_name',
            'check_type_code', 'schedule', 'is_active',
            'last_run', 'next_run', 'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id', 'check_type_name', 'check_type_code',
            'last_run', 'created_at', 'updated_at'
        ]

    def validate_schedule(self, value):
        # Zamanlama doğrulama mantığı buraya eklenecek
        return value

    def validate(self, data):
        if data.get('next_run') and data.get('last_run'):
            if data['next_run'] <= data['last_run']:
                raise serializers.ValidationError(
                    "Sonraki çalıştırma zamanı son çalıştırmadan önce olamaz"
                )
        return data 