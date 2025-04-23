from django.contrib import admin
from django.utils.html import format_html
from .models import SEOMetadata, SEORedirect, SEOKeyword, SEOAnalytics

@admin.register(SEOMetadata)
class SEOMetadataAdmin(admin.ModelAdmin):
    list_display = ('title', 'content_type', 'object_id', 'created_at', 'updated_at')
    list_filter = ('content_type', 'created_at', 'updated_at')
    search_fields = ('title', 'meta_description', 'meta_keywords')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('content_type', 'object_id', 'title', 'meta_description', 'meta_keywords')
        }),
        ('URL ve Robots', {
            'fields': ('canonical_url', 'robots_meta')
        }),
        ('Open Graph', {
            'fields': ('og_title', 'og_description', 'og_image', 'twitter_card')
        }),
        ('Yapılandırılmış Veri', {
            'fields': ('structured_data',)
        }),
        ('Zaman Bilgileri', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(SEORedirect)
class SEORedirectAdmin(admin.ModelAdmin):
    list_display = ('old_path', 'new_path', 'is_permanent', 'created_at')
    list_filter = ('is_permanent', 'created_at')
    search_fields = ('old_path', 'new_path')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Yönlendirme Bilgileri', {
            'fields': ('old_path', 'new_path', 'is_permanent')
        }),
        ('Zaman Bilgileri', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(SEOKeyword)
class SEOKeywordAdmin(admin.ModelAdmin):
    list_display = ('keyword', 'search_volume', 'difficulty', 'competition', 'cpc')
    list_filter = ('difficulty', 'competition')
    search_fields = ('keyword',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Anahtar Kelime Bilgileri', {
            'fields': ('keyword', 'search_volume', 'difficulty', 'cpc', 'competition')
        }),
        ('Zaman Bilgileri', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(SEOAnalytics)
class SEOAnalyticsAdmin(admin.ModelAdmin):
    list_display = ('date', 'organic_traffic', 'average_position', 'impressions', 'clicks', 'ctr_display')
    list_filter = ('date',)
    readonly_fields = ('created_at', 'updated_at', 'ctr')
    fieldsets = (
        ('Analiz Verileri', {
            'fields': ('date', 'organic_traffic', 'average_position', 'impressions', 'clicks', 'ctr')
        }),
        ('Zaman Bilgileri', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def ctr_display(self, obj):
        return format_html('<b>{:.2f}%</b>', obj.ctr)
    ctr_display.short_description = 'Tıklanma Oranı'
