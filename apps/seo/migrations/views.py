from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import SEOMetadata, SEOAnalysis, KeywordRanking, CompetitorAnalysis
from .forms import SEOMetadataForm, SEOAnalysisForm, KeywordRankingForm, CompetitorAnalysisForm
from .serializers import (
    SeoMetadataSerializer, SeoAnalysisSerializer,
    KeywordRankingSerializer, CompetitorAnalysisSerializer
)

# SEO Metadata Views
class SEOMetadataListView(LoginRequiredMixin, ListView):
    model = SEOMetadata
    template_name = 'seo/metadata_list.html'
    context_object_name = 'metadata_list'
    ordering = ['-created_at']

class SEOMetadataDetailView(LoginRequiredMixin, DetailView):
    model = SEOMetadata
    template_name = 'seo/metadata_detail.html'
    context_object_name = 'metadata'

class SEOMetadataCreateView(LoginRequiredMixin, CreateView):
    model = SEOMetadata
    form_class = SEOMetadataForm
    template_name = 'seo/metadata_form.html'
    success_url = reverse_lazy('seo:metadata_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'SEO metadata başarıyla oluşturuldu.')
        return super().form_valid(form)

class SEOMetadataUpdateView(LoginRequiredMixin, UpdateView):
    model = SEOMetadata
    form_class = SEOMetadataForm
    template_name = 'seo/metadata_form.html'
    success_url = reverse_lazy('seo:metadata_list')

    def form_valid(self, form):
        messages.success(self.request, 'SEO metadata başarıyla güncellendi.')
        return super().form_valid(form)

class SEOMetadataDeleteView(LoginRequiredMixin, DeleteView):
    model = SEOMetadata
    template_name = 'seo/metadata_confirm_delete.html'
    success_url = reverse_lazy('seo:metadata_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'SEO metadata başarıyla silindi.')
        return super().delete(request, *args, **kwargs)

# SEO Analysis Views
class SEOAnalysisListView(LoginRequiredMixin, ListView):
    model = SEOAnalysis
    template_name = 'seo/analysis_list.html'
    context_object_name = 'analysis_list'
    ordering = ['-created_at']

class SEOAnalysisDetailView(LoginRequiredMixin, DetailView):
    model = SEOAnalysis
    template_name = 'seo/analysis_detail.html'
    context_object_name = 'analysis'

class SEOAnalysisCreateView(LoginRequiredMixin, CreateView):
    model = SEOAnalysis
    form_class = SEOAnalysisForm
    template_name = 'seo/analysis_form.html'
    success_url = reverse_lazy('seo:analysis_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'SEO analizi başarıyla oluşturuldu.')
        return super().form_valid(form)

class SEOAnalysisUpdateView(LoginRequiredMixin, UpdateView):
    model = SEOAnalysis
    form_class = SEOAnalysisForm
    template_name = 'seo/analysis_form.html'
    success_url = reverse_lazy('seo:analysis_list')

    def form_valid(self, form):
        messages.success(self.request, 'SEO analizi başarıyla güncellendi.')
        return super().form_valid(form)

class SEOAnalysisDeleteView(LoginRequiredMixin, DeleteView):
    model = SEOAnalysis
    template_name = 'seo/analysis_confirm_delete.html'
    success_url = reverse_lazy('seo:analysis_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'SEO analizi başarıyla silindi.')
        return super().delete(request, *args, **kwargs)

# Keyword Ranking Views
class KeywordRankingListView(LoginRequiredMixin, ListView):
    model = KeywordRanking
    template_name = 'seo/keyword_list.html'
    context_object_name = 'keyword_list'
    ordering = ['-last_checked']

class KeywordRankingDetailView(LoginRequiredMixin, DetailView):
    model = KeywordRanking
    template_name = 'seo/keyword_detail.html'
    context_object_name = 'keyword'

class KeywordRankingCreateView(LoginRequiredMixin, CreateView):
    model = KeywordRanking
    form_class = KeywordRankingForm
    template_name = 'seo/keyword_form.html'
    success_url = reverse_lazy('seo:keyword_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Anahtar kelime sıralaması başarıyla oluşturuldu.')
        return super().form_valid(form)

class KeywordRankingUpdateView(LoginRequiredMixin, UpdateView):
    model = KeywordRanking
    form_class = KeywordRankingForm
    template_name = 'seo/keyword_form.html'
    success_url = reverse_lazy('seo:keyword_list')

    def form_valid(self, form):
        messages.success(self.request, 'Anahtar kelime sıralaması başarıyla güncellendi.')
        return super().form_valid(form)

class KeywordRankingDeleteView(LoginRequiredMixin, DeleteView):
    model = KeywordRanking
    template_name = 'seo/keyword_confirm_delete.html'
    success_url = reverse_lazy('seo:keyword_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Anahtar kelime sıralaması başarıyla silindi.')
        return super().delete(request, *args, **kwargs)

# Competitor Analysis Views
class CompetitorAnalysisListView(LoginRequiredMixin, ListView):
    model = CompetitorAnalysis
    template_name = 'seo/competitor_list.html'
    context_object_name = 'competitor_list'
    ordering = ['-created_at']

class CompetitorAnalysisDetailView(LoginRequiredMixin, DetailView):
    model = CompetitorAnalysis
    template_name = 'seo/competitor_detail.html'
    context_object_name = 'competitor'

class CompetitorAnalysisCreateView(LoginRequiredMixin, CreateView):
    model = CompetitorAnalysis
    form_class = CompetitorAnalysisForm
    template_name = 'seo/competitor_form.html'
    success_url = reverse_lazy('seo:competitor_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Rakip analizi başarıyla oluşturuldu.')
        return super().form_valid(form)

class CompetitorAnalysisUpdateView(LoginRequiredMixin, UpdateView):
    model = CompetitorAnalysis
    form_class = CompetitorAnalysisForm
    template_name = 'seo/competitor_form.html'
    success_url = reverse_lazy('seo:competitor_list')

    def form_valid(self, form):
        messages.success(self.request, 'Rakip analizi başarıyla güncellendi.')
        return super().form_valid(form)

class CompetitorAnalysisDeleteView(LoginRequiredMixin, DeleteView):
    model = CompetitorAnalysis
    template_name = 'seo/competitor_confirm_delete.html'
    success_url = reverse_lazy('seo:competitor_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Rakip analizi başarıyla silindi.')
        return super().delete(request, *args, **kwargs)

# API Views
@login_required
def analyze_url(request):
    if request.method == 'POST':
        url = request.POST.get('url')
        # URL analiz işlemleri burada yapılacak
        return JsonResponse({'status': 'success', 'message': 'URL analizi tamamlandı'})
    return JsonResponse({'status': 'error', 'message': 'Geçersiz istek'}, status=400)

@login_required
def check_keyword_ranking(request):
    if request.method == 'POST':
        keyword = request.POST.get('keyword')
        url = request.POST.get('url')
        # Anahtar kelime sıralama kontrolü burada yapılacak
        return JsonResponse({'status': 'success', 'message': 'Anahtar kelime sıralaması kontrol edildi'})
    return JsonResponse({'status': 'error', 'message': 'Geçersiz istek'}, status=400) 