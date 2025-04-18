from django import forms
from .models import SEOMetadata, SEOAnalysis, KeywordRanking, CompetitorAnalysis

class SEOMetadataForm(forms.ModelForm):
    class Meta:
        model = SEOMetadata
        fields = ['page_url', 'title', 'description', 'keywords', 'canonical_url', 'robots', 'og_title', 'og_description', 'og_image', 'twitter_card', 'twitter_title', 'twitter_description', 'twitter_image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'keywords': forms.Textarea(attrs={'rows': 2}),
            'og_description': forms.Textarea(attrs={'rows': 3}),
            'twitter_description': forms.Textarea(attrs={'rows': 3}),
        }

class SEOAnalysisForm(forms.ModelForm):
    class Meta:
        model = SEOAnalysis
        fields = ['page_url', 'title_length', 'description_length', 'keyword_density', 'heading_structure', 'image_alt_tags', 'internal_links', 'external_links', 'load_time', 'mobile_friendly', 'ssl_secure', 'xml_sitemap', 'robots_txt', 'meta_robots', 'canonical_url', 'schema_markup', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 4}),
        }

class KeywordRankingForm(forms.ModelForm):
    class Meta:
        model = KeywordRanking
        fields = ['keyword', 'search_volume', 'difficulty', 'position', 'url', 'last_checked', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
            'last_checked': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class CompetitorAnalysisForm(forms.ModelForm):
    class Meta:
        model = CompetitorAnalysis
        fields = ['competitor_url', 'domain_authority', 'page_authority', 'backlinks', 'referring_domains', 'organic_keywords', 'organic_traffic', 'top_keywords', 'content_gaps', 'notes']
        widgets = {
            'top_keywords': forms.Textarea(attrs={'rows': 3}),
            'content_gaps': forms.Textarea(attrs={'rows': 4}),
            'notes': forms.Textarea(attrs={'rows': 4}),
        } 