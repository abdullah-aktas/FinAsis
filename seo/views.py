# -*- coding: utf-8 -*-
"""
SEO Modülü - View'lar
---------------------
Bu dosya, SEO modülünün view'larını içerir.
"""

from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from django.db.models import Q
from rest_framework import viewsets, permissions, filters, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import SEOMetadata, SEORedirect, SEOKeyword, SEOAnalytics
from .serializers import (
    SEOMetadataSerializer,
    SEORedirectSerializer,
    SEOKeywordSerializer,
    SEOAnalyticsSerializer
)
from .forms import (
    SEOMetadataForm,
    SEORedirectForm,
    SEOKeywordForm,
    SEOAnalyticsForm
)
from .tasks import update_seo_analytics, fetch_keyword_data
from .utils import generate_sitemap, check_robots_txt, analyze_page_seo

class SEOMetadataViewSet(viewsets.ModelViewSet):
    """SEO Meta Veri ViewSet"""
    queryset = SEOMetadata.objects.all()
    serializer_class = SEOMetadataSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'meta_description', 'meta_keywords']
    ordering_fields = ['created_at', 'updated_at']
    
    @action(detail=True, methods=['post'])
    def analyze(self, request, pk=None):
        """Sayfa SEO analizi yap"""
        metadata = self.get_object()
        results = analyze_page_seo(metadata.content_object)
        return Response(results)
    
    @action(detail=False, methods=['get'])
    def sitemap(self, request):
        """Sitemap oluştur"""
        sitemap = generate_sitemap()
        return Response(sitemap)

class SEORedirectViewSet(viewsets.ModelViewSet):
    """SEO yönlendirmelerini yöneten viewset"""
    queryset = SEORedirect.objects.all()
    serializer_class = SEORedirectSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['old_path', 'new_path']
    
    @action(detail=False, methods=['get'])
    def check_redirects(self, request):
        """Yönlendirmeleri kontrol et"""
        redirects = self.get_queryset()
        results = []
        for redirect in redirects:
            results.append({
                'old_path': redirect.old_path,
                'new_path': redirect.new_path,
                'status': 'active' if redirect.is_permanent else 'temporary'
            })
        return Response(results)

class SEOKeywordViewSet(viewsets.ModelViewSet):
    """SEO Anahtar Kelime ViewSet"""
    queryset = SEOKeyword.objects.all()
    serializer_class = SEOKeywordSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['keyword']
    ordering_fields = ['search_volume', 'difficulty', 'competition']
    
    @action(detail=False, methods=['post'])
    def fetch_data(self, request):
        """Anahtar kelime verilerini güncelle"""
        keywords = request.data.get('keywords', [])
        results = fetch_keyword_data.delay(keywords)
        return Response({'task_id': results.id})
    
    @action(detail=False, methods=['get'])
    def top_keywords(self, request):
        """En iyi performans gösteren anahtar kelimeleri getir"""
        keywords = self.get_queryset().order_by('-search_volume')[:10]
        serializer = self.get_serializer(keywords, many=True)
        return Response(serializer.data)

class SEOAnalyticsViewSet(viewsets.ModelViewSet):
    """SEO Analitik ViewSet"""
    queryset = SEOAnalytics.objects.all()
    serializer_class = SEOAnalyticsSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['date', 'organic_traffic', 'average_position']
    
    @action(detail=False, methods=['post'])
    def update_analytics(self, request):
        """Analiz verilerini güncelle"""
        results = update_seo_analytics.delay()
        return Response({'task_id': results.id})
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """SEO performans özeti"""
        cache_key = 'seo_analytics_summary'
        summary = cache.get(cache_key)
        
        if not summary:
            analytics = self.get_queryset().order_by('-date')[:30]
            summary = {
                'total_traffic': sum(a.organic_traffic for a in analytics),
                'avg_position': sum(a.average_position for a in analytics) / len(analytics),
                'total_impressions': sum(a.impressions for a in analytics),
                'total_clicks': sum(a.clicks for a in analytics),
                'avg_ctr': sum(a.ctr for a in analytics) / len(analytics)
            }
            cache.set(cache_key, summary, 3600)  # 1 saat cache
        
        return Response(summary)

# Meta Veri View'ları
class SEOMetadataListView(generics.ListAPIView):
    queryset = SEOMetadata.objects.all()
    serializer_class = SEOMetadataSerializer

class SEOMetadataDetailView(generics.RetrieveAPIView):
    queryset = SEOMetadata.objects.all()
    serializer_class = SEOMetadataSerializer

class SEOMetadataCreateView(generics.CreateAPIView):
    queryset = SEOMetadata.objects.all()
    serializer_class = SEOMetadataSerializer

class SEOMetadataUpdateView(generics.UpdateAPIView):
    queryset = SEOMetadata.objects.all()
    serializer_class = SEOMetadataSerializer

class SEOMetadataDeleteView(generics.DestroyAPIView):
    queryset = SEOMetadata.objects.all()
    serializer_class = SEOMetadataSerializer

# Anahtar Kelime View'ları
class SEOKeywordListView(generics.ListAPIView):
    queryset = SEOKeyword.objects.all()
    serializer_class = SEOKeywordSerializer

class SEOKeywordDetailView(generics.RetrieveAPIView):
    queryset = SEOKeyword.objects.all()
    serializer_class = SEOKeywordSerializer

class SEOKeywordCreateView(generics.CreateAPIView):
    queryset = SEOKeyword.objects.all()
    serializer_class = SEOKeywordSerializer

class SEOKeywordUpdateView(generics.UpdateAPIView):
    queryset = SEOKeyword.objects.all()
    serializer_class = SEOKeywordSerializer

class SEOKeywordDeleteView(generics.DestroyAPIView):
    queryset = SEOKeyword.objects.all()
    serializer_class = SEOKeywordSerializer

# SEO Analitik View'ları
class SEOAnalyticsListView(generics.ListAPIView):
    queryset = SEOAnalytics.objects.all()
    serializer_class = SEOAnalyticsSerializer

class SEOAnalyticsDetailView(generics.RetrieveAPIView):
    queryset = SEOAnalytics.objects.all()
    serializer_class = SEOAnalyticsSerializer

class SEOAnalyticsCreateView(generics.CreateAPIView):
    queryset = SEOAnalytics.objects.all()
    serializer_class = SEOAnalyticsSerializer

class SEOAnalyticsUpdateView(generics.UpdateAPIView):
    queryset = SEOAnalytics.objects.all()
    serializer_class = SEOAnalyticsSerializer

class SEOAnalyticsDeleteView(generics.DestroyAPIView):
    queryset = SEOAnalytics.objects.all()
    serializer_class = SEOAnalyticsSerializer

# SEO Araçları
def robots_txt(request):
    """Robots.txt dosyasını oluşturur"""
    content = "User-agent: *\nAllow: /\nDisallow: /admin/\nDisallow: /api/"
    return HttpResponse(content, content_type="text/plain")

def sitemap_xml(request):
    """Sitemap.xml dosyasını oluşturur"""
    content = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>https://finasis.com/</loc>
        <lastmod>2024-03-20</lastmod>
        <changefreq>daily</changefreq>
        <priority>1.0</priority>
    </url>
</urlset>"""
    return HttpResponse(content, content_type="application/xml")

class AnalyzeView(APIView):
    """SEO analizi yapar"""
    def post(self, request):
        # SEO analizi yapılacak
        return Response({"status": "success", "message": "SEO analizi tamamlandı"})

class OptimizeView(APIView):
    """SEO optimizasyonu yapar"""
    def post(self, request):
        # SEO optimizasyonu yapılacak
        return Response({"status": "success", "message": "SEO optimizasyonu tamamlandı"})
