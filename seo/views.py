from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from django.db.models import Q
from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
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
    """SEO meta verilerini yöneten viewset"""
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
    """SEO anahtar kelimelerini yöneten viewset"""
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
    """SEO analiz verilerini yöneten viewset"""
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

# Template Views
class SEOMetadataListView(LoginRequiredMixin, ListView):
    model = SEOMetadata
    template_name = 'seo/metadata_list.html'
    context_object_name = 'metadata_list'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(meta_description__icontains=search_query) |
                Q(meta_keywords__icontains=search_query)
            )
        return queryset

class SEOMetadataDetailView(LoginRequiredMixin, DetailView):
    model = SEOMetadata
    template_name = 'seo/metadata_detail.html'
    context_object_name = 'metadata'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['analysis'] = analyze_page_seo(self.object.content_object)
        return context

class SEOMetadataCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = SEOMetadata
    form_class = SEOMetadataForm
    template_name = 'seo/metadata_form.html'
    permission_required = 'seo.add_seometadata'
    success_url = reverse_lazy('seo:metadata_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'SEO meta verisi başarıyla oluşturuldu.')
        return super().form_valid(form)

class SEOMetadataUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = SEOMetadata
    form_class = SEOMetadataForm
    template_name = 'seo/metadata_form.html'
    permission_required = 'seo.change_seometadata'
    success_url = reverse_lazy('seo:metadata_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'SEO meta verisi başarıyla güncellendi.')
        return super().form_valid(form)

class SEOMetadataDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = SEOMetadata
    template_name = 'seo/metadata_confirm_delete.html'
    permission_required = 'seo.delete_seometadata'
    success_url = reverse_lazy('seo:metadata_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'SEO meta verisi başarıyla silindi.')
        return super().delete(request, *args, **kwargs)

@require_http_methods(['GET'])
@cache_page(60 * 60)  # 1 saat cache
def robots_txt(request):
    """robots.txt dosyasını oluştur"""
    return render(request, 'seo/robots.txt', content_type='text/plain')

@require_http_methods(['GET'])
@cache_page(60 * 60)  # 1 saat cache
def sitemap_xml(request):
    """sitemap.xml dosyasını oluştur"""
    return render(request, 'seo/sitemap.xml', content_type='application/xml')
