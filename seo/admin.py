from django.contrib import admin
from django.utils.html import format_html
from .models import SeoMetadata, SeoAnalysis, KeywordRanking, CompetitorAnalysis

@admin.register(SeoMetadata)
class SeoMetadataAdmin(admin.ModelAdmin):
    list_display = ('content_type', 'object_id', 'title', 'created_at', 'updated_at')
    list_filter = ('content_type', 'created_at', 'updated_at')
    search_fields = ('title', 'description', 'keywords')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('İçerik Bilgisi', {
            'fields': ('content_type', 'object_id')
        }),
        ('Meta Veriler', {
            'fields': ('title', 'description', 'keywords', 'canonical_url')
        }),
        ('Open Graph', {
            'fields': ('og_title', 'og_description', 'og_image')
        }),
        ('Twitter Card', {
            'fields': ('twitter_title', 'twitter_description', 'twitter_image')
        }),
        ('Zaman Bilgisi', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(SeoAnalysis)
class SeoAnalysisAdmin(admin.ModelAdmin):
    list_display = ('url', 'title', 'score', 'word_count', 'created_at')
    list_filter = ('score', 'created_at')
    search_fields = ('url', 'title')
    readonly_fields = ('created_at',)
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Düzenleme durumunda
            return self.readonly_fields + ('url', 'title', 'score', 'word_count', 'heading_count', 
                                        'image_count', 'images_without_alt', 'link_count', 
                                        'internal_link_count', 'external_link_count', 
                                        'keyword_density', 'suggestions')
        return self.readonly_fields

@admin.register(KeywordRanking)
class KeywordRankingAdmin(admin.ModelAdmin):
    list_display = ('keyword', 'url', 'position', 'search_volume', 'difficulty', 'cpc', 'updated_at')
    list_filter = ('position', 'difficulty', 'updated_at')
    search_fields = ('keyword', 'url')
    readonly_fields = ('created_at', 'updated_at')
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Düzenleme durumunda
            return self.readonly_fields + ('keyword', 'url', 'position', 'search_volume', 
                                        'difficulty', 'cpc')
        return self.readonly_fields

@admin.register(CompetitorAnalysis)
class CompetitorAnalysisAdmin(admin.ModelAdmin):
    list_display = ('competitor_url', 'keyword', 'position', 'domain_authority', 'updated_at')
    list_filter = ('position', 'domain_authority', 'updated_at')
    search_fields = ('competitor_url', 'keyword', 'title', 'description')
    readonly_fields = ('created_at', 'updated_at')
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Düzenleme durumunda
            return self.readonly_fields + ('competitor_url', 'keyword', 'position', 'title', 
                                        'description', 'word_count', 'heading_count', 
                                        'image_count', 'link_count', 'backlink_count', 
                                        'domain_authority')
        return self.readonly_fields 