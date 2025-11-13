from rest_framework import serializers
from .models import Declaration, Submission, SubmissionLog


class DeclarationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Declaration
        fields = ['id', 'code', 'period', 'taxpayer_vkn_tckn', 'payload', 'created_by', 'created_at']
        read_only_fields = ['id', 'created_by', 'created_at']


class SubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = ['id', 'declaration', 'target', 'submitted_by', 'advisor_required', 'submitted_at', 'status', 'external_id']
        read_only_fields = ['id', 'submitted_by', 'submitted_at', 'status', 'external_id']


class SubmissionLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubmissionLog
        fields = ['id', 'submission', 'level', 'message', 'context', 'created_at']
        read_only_fields = ['id', 'created_at']
