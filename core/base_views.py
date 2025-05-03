from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.core.cache import cache
from django.utils.translation import gettext_lazy as _
import logging

logger = logging.getLogger(__name__)

class BaseListView(LoginRequiredMixin, ListView):
    paginate_by = 20
    
    def get_queryset(self):
        cache_key = f"{self.__class__.__name__}_{self.request.user.pk}"  # id yerine pk kullan
        queryset = cache.get(cache_key)
        
        if not queryset:
            queryset = super().get_queryset()
            cache.set(cache_key, queryset, 300)
            
        return queryset
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if hasattr(self, 'model') and self.model is not None:
            context['title'] = self.model._meta.verbose_name_plural
        return context

class BaseDetailView(LoginRequiredMixin, DetailView):
    def get_object(self):
        obj = super().get_object()
        if hasattr(obj, '_meta'):
            logger.info(f"{obj._meta.model_name} #{obj.pk} görüntülendi")
        return obj

class BaseCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    def form_valid(self, form):
        response = super().form_valid(form)
        obj = form.instance
        if hasattr(self, 'model') and self.model is not None:
            messages.success(self.request, _(f"{self.model._meta.verbose_name} başarıyla oluşturuldu."))
            logger.info(f"Yeni {self.model._meta.model_name} oluşturuldu: #{obj.pk}")
        return response

class BaseUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView): 
    def form_valid(self, form):
        response = super().form_valid(form)
        obj = form.instance
        if hasattr(self, 'model') and self.model is not None:
            messages.success(self.request, _(f"{self.model._meta.verbose_name} başarıyla güncellendi."))
            logger.info(f"{self.model._meta.model_name} #{obj.pk} güncellendi")
        return response

class BaseDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        response = super().delete(request, *args, **kwargs)
        messages.success(request, _(f"{obj._meta.verbose_name} başarıyla silindi."))
        logger.info(f"{obj._meta.model_name} #{obj.pk} silindi")
        return response
