from rest_framework import serializers
from .models import SEOMetadata, SEOAnalysis, KeywordRanking, CompetitorAnalysis

class SEOMetadataSerializer(serializers.ModelSerializer):
    class Meta:
        model = SEOMetadata
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class SEOAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = SEOAnalysis
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class KeywordRankingSerializer(serializers.ModelSerializer):
    class Meta:
        model = KeywordRanking
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class CompetitorAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompetitorAnalysis
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at') 