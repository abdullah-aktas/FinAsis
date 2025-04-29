# -*- coding: utf-8 -*-
#!/usr/bin/env python
"""
Bu script FinAsis projesindeki MVT (Model-View-Template) yapısını kontrol eder,
eksik dosyaları oluşturur ve canlıya alma öncesi hazırlık yapar.
"""
import os
import re
import sys
from pathlib import Path
import shutil
import datetime
import importlib
import logging

# Logging ayarı
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("mvt_fix.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Django ayarlarını yükle
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
BASE_DIR = Path(__file__).resolve().parent

# İzlenmemesi gereken dizinler
EXCLUDE_DIRS = ['.git', 'venv', '.venv', '__pycache__', 'node_modules', 'staticfiles',
                'static', 'media', 'dist', 'backups', 'all_backups', 'build',
                'logs', '.idea', '.vscode', 'TestProje', 'testapp', 'testsite']

# Şablonlar
URL_TEMPLATE = """from django.urls import path
from . import views

app_name = '{app_name}'

urlpatterns = [
    path('', views.index, name='index'),
    # Buraya ek URL pattern'leri eklenebilir
]
"""

VIEWS_TEMPLATE = """from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from .models import *

@login_required
def index(request):
    \"\"\"
    Modül ana sayfası
    \"\"\"
    return render(request, '{app_name}/index.html', context={{'title': '{app_title}'}})
"""

INDEX_TEMPLATE = """{% extends "base.html" %}
{% load i18n %}
{% load static %}

{% block title %}{{ title }}{% endblock %}

{% block content %}
<div class="container mt-5">
    <div class="row">
        <div class="col-md-12">
            <h1 class="mb-4">{% trans 'Hoş Geldiniz' %}</h1>
            <p class="lead">{% trans 'Bu {app_title} modülünün ana sayfasıdır.' %}</p>
            
            <div class="card mt-4">
                <div class="card-header">
                    <h5>{% trans 'Modül Özellikleri' %}</h5>
                </div>
                <div class="card-body">
                    <ul>
                        <li>{% trans 'Özellik 1' %}</li>
                        <li>{% trans 'Özellik 2' %}</li>
                        <li>{% trans 'Özellik 3' %}</li>
                    </ul>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
"""

MODEL_LIST_TEMPLATE = """{% extends "base.html" %}
{% load i18n %}
{% load static %}

{% block title %}{{ title }}{% endblock %}

{% block content %}
<div class="container mt-5">
    <div class="row">
        <div class="col-md-12">
            <h1 class="mb-4">{% trans '{model_title} Listesi' %}</h1>
            
            <div class="mb-3">
                <a href="{% url '{app_name}:{model_snake}_create' %}" class="btn btn-primary">
                    <i class="fas fa-plus"></i> {% trans 'Yeni Ekle' %}
                </a>
            </div>
            
            <div class="card">
                <div class="card-body">
                    <div class="table-responsive">
                        <table class="table table-hover">
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>{% trans 'Ad' %}</th>
                                    <th>{% trans 'Oluşturulma Tarihi' %}</th>
                                    <th>{% trans 'İşlemler' %}</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for object in object_list %}
                                <tr>
                                    <td>{{ object.id }}</td>
                                    <td>{{ object }}</td>
                                    <td>{{ object.created_at|date:"d.m.Y H:i" }}</td>
                                    <td>
                                        <a href="{% url '{app_name}:{model_snake}_detail' object.id %}" class="btn btn-sm btn-info">
                                            <i class="fas fa-eye"></i>
                                        </a>
                                        <a href="{% url '{app_name}:{model_snake}_update' object.id %}" class="btn btn-sm btn-warning">
                                            <i class="fas fa-edit"></i>
                                        </a>
                                        <a href="{% url '{app_name}:{model_snake}_delete' object.id %}" class="btn btn-sm btn-danger">
                                            <i class="fas fa-trash"></i>
                                        </a>
                                    </td>
                                </tr>
                                {% empty %}
                                <tr>
                                    <td colspan="4" class="text-center">{% trans 'Kayıt bulunamadı' %}</td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
"""

def is_excluded_dir(path):
    """
    Dizinin dışlanması gereken bir dizin olup olmadığını kontrol eder
    """
    for exclude in EXCLUDE_DIRS:
        if exclude in str(path):
            return True
    return False

def find_django_modules():
    """
    Projede tanımlı Django modüllerini bulur
    """
    modules = []
    for item in os.listdir(BASE_DIR):
        if is_excluded_dir(item):
            continue
            
        item_path = os.path.join(BASE_DIR, item)
        if os.path.isdir(item_path):
            apps_py = os.path.join(item_path, 'apps.py')
            if os.path.exists(apps_py):
                modules.append(item)
    
    return modules

def collect_models(module_name):
    """
    Modül içindeki tüm model sınıflarını toplar
    """
    models = []
    models_path = os.path.join(BASE_DIR, module_name, 'models.py')
    
    if not os.path.exists(models_path):
        return []
        
    try:
        with open(models_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Model sınıflarını bul
        model_pattern = r'class\s+(\w+)\((?:models\.Model|.*Model.*)\)'
        found_models = re.findall(model_pattern, content)
        
        if found_models:
            models.extend(found_models)
            
        # models/ dizinini kontrol et
        models_dir = os.path.join(BASE_DIR, module_name, 'models')
        if os.path.exists(models_dir) and os.path.isdir(models_dir):
            for model_file in os.listdir(models_dir):
                if model_file.endswith('.py') and model_file != '__init__.py':
                    model_file_path = os.path.join(models_dir, model_file)
                    with open(model_file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    found_models = re.findall(model_pattern, content)
                    if found_models:
                        models.extend(found_models)
                        
    except Exception as e:
        logger.error(f"❌ {module_name} modellerini analiz ederken hata: {e}")
    
    return models

def create_missing_urls_file(module_name):
    """
    Eksik urls.py dosyasını oluşturur
    """
    urls_path = os.path.join(BASE_DIR, module_name, 'urls.py')
    
    if os.path.exists(urls_path):
        logger.info(f"✓ {module_name}/urls.py zaten mevcut.")
        return
    
    content = URL_TEMPLATE.format(app_name=module_name)
    
    with open(urls_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    logger.info(f"✅ {module_name}/urls.py dosyası oluşturuldu.")

def create_missing_views_file(module_name):
    """
    Eksik views.py dosyasını oluşturur
    """
    views_path = os.path.join(BASE_DIR, module_name, 'views.py')
    
    if os.path.exists(views_path):
        logger.info(f"✓ {module_name}/views.py zaten mevcut.")
        return
    
    app_title = module_name.replace('_', ' ').title()
    content = VIEWS_TEMPLATE.format(app_name=module_name, app_title=app_title)
    
    with open(views_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    logger.info(f"✅ {module_name}/views.py dosyası oluşturuldu.")

def create_missing_template_dir(module_name):
    """
    Eksik template dizinini oluşturur
    """
    templates_dir = os.path.join(BASE_DIR, module_name, 'templates')
    module_templates_dir = os.path.join(templates_dir, module_name)
    
    if not os.path.exists(templates_dir):
        os.makedirs(templates_dir)
        logger.info(f"✅ {module_name}/templates/ dizini oluşturuldu.")
    
    if not os.path.exists(module_templates_dir):
        os.makedirs(module_templates_dir)
        logger.info(f"✅ {module_name}/templates/{module_name}/ dizini oluşturuldu.")
    
    # Index şablonunu oluştur
    index_path = os.path.join(module_templates_dir, 'index.html')
    if not os.path.exists(index_path):
        app_title = module_name.replace('_', ' ').title()
        content = INDEX_TEMPLATE.format(app_title=app_title)
        
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"✅ {module_name}/templates/{module_name}/index.html dosyası oluşturuldu.")

def create_missing_model_templates(module_name, model_names):
    """
    Eksik model şablonlarını oluşturur
    """
    templates_dir = os.path.join(BASE_DIR, module_name, 'templates', module_name)
    
    if not os.path.exists(templates_dir):
        os.makedirs(templates_dir)
    
    for model_name in model_names:
        # Model adını snake_case'e çevir
        model_snake = ''.join(['_'+c.lower() if c.isupper() else c.lower() for c in model_name]).lstrip('_')
        model_title = model_name.replace('_', ' ')
        
        # Liste şablonu
        list_path = os.path.join(templates_dir, f"{model_snake}_list.html")
        if not os.path.exists(list_path):
            content = MODEL_LIST_TEMPLATE.format(
                app_name=module_name, 
                model_snake=model_snake, 
                model_title=model_title
            )
            
            with open(list_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"✅ {model_snake}_list.html şablonu oluşturuldu.")

def update_views_for_models(module_name, model_names):
    """
    View dosyasını güncelleyerek modeller için view'ler ekler
    """
    views_path = os.path.join(BASE_DIR, module_name, 'views.py')
    views_dir = os.path.join(BASE_DIR, module_name, 'views')
    
    if os.path.exists(views_dir) and os.path.isdir(views_dir):
        # views/ dizini zaten var, muhtemelen düzgün yapılandırılmış
        logger.info(f"✓ {module_name}/views/ dizini zaten mevcut, güncelleme yapılmadı.")
        return
    
    # views.py dosyasını oku
    if not os.path.exists(views_path):
        create_missing_views_file(module_name)
    
    with open(views_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Her model için eklenecek içerik
    new_content = content
    for model_name in model_names:
        model_snake = ''.join(['_'+c.lower() if c.isupper() else c.lower() for c in model_name]).lstrip('_')
        
        # Eğer model view'leri zaten tanımlanmışsa ekleme yapma
        if f"class {model_name}ListView" in content:
            continue
        
        # Model için view sınıflarını ekle
        view_classes = f"""

class {model_name}ListView(LoginRequiredMixin, ListView):
    model = {model_name}
    template_name = '{module_name}/{model_snake}_list.html'
    context_object_name = 'object_list'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = '{model_name} Listesi'
        return context

class {model_name}DetailView(LoginRequiredMixin, DetailView):
    model = {model_name}
    template_name = '{module_name}/{model_snake}_detail.html'
    context_object_name = 'object'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = '{model_name} Detayı'
        return context

class {model_name}CreateView(LoginRequiredMixin, CreateView):
    model = {model_name}
    template_name = '{module_name}/{model_snake}_form.html'
    fields = '__all__'
    success_url = reverse_lazy('{module_name}:{model_snake}_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Yeni {model_name} Ekle'
        return context

class {model_name}UpdateView(LoginRequiredMixin, UpdateView):
    model = {model_name}
    template_name = '{module_name}/{model_snake}_form.html'
    fields = '__all__'
    success_url = reverse_lazy('{module_name}:{model_snake}_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = '{model_name} Düzenle'
        return context

class {model_name}DeleteView(LoginRequiredMixin, DeleteView):
    model = {model_name}
    template_name = '{module_name}/{model_snake}_confirm_delete.html'
    success_url = reverse_lazy('{module_name}:{model_snake}_list')
"""
        new_content += view_classes
    
    # İçerik değiştiyse dosyayı güncelle
    if new_content != content:
        with open(views_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        logger.info(f"✅ {module_name}/views.py dosyası modeller için güncellendi.")

def update_urls_for_models(module_name, model_names):
    """
    urls.py dosyasını modeller için güncelleyelim
    """
    urls_path = os.path.join(BASE_DIR, module_name, 'urls.py')
    
    if not os.path.exists(urls_path):
        create_missing_urls_file(module_name)
    
    with open(urls_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # urlpatterns'ı bul
    patterns_match = re.search(r'urlpatterns\s*=\s*\[(.*?)\]', content, re.DOTALL)
    if not patterns_match:
        logger.error(f"❌ {module_name}/urls.py dosyasında urlpatterns bulunamadı.")
        return
    
    patterns_content = patterns_match.group(1)
    
    # Yeni URL desenlerini ekleyelim
    new_patterns = patterns_content
    for model_name in model_names:
        model_snake = ''.join(['_'+c.lower() if c.isupper() else c.lower() for c in model_name]).lstrip('_')
        
        # Model için URL desenleri
        model_urls = f"""
    path('{model_snake}/', views.{model_name}ListView.as_view(), name='{model_snake}_list'),
    path('{model_snake}/<int:pk>/', views.{model_name}DetailView.as_view(), name='{model_snake}_detail'),
    path('{model_snake}/create/', views.{model_name}CreateView.as_view(), name='{model_snake}_create'),
    path('{model_snake}/<int:pk>/update/', views.{model_name}UpdateView.as_view(), name='{model_snake}_update'),
    path('{model_snake}/<int:pk>/delete/', views.{model_name}DeleteView.as_view(), name='{model_snake}_delete'),"""
        
        # URL deseni zaten eklenmiş mi kontrol et
        if f"path('{model_snake}/'," not in content:
            new_patterns += model_urls
    
    # İçerik değiştiyse dosyayı güncelle
    new_content = content.replace(patterns_match.group(1), new_patterns)
    if new_content != content:
        with open(urls_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        logger.info(f"✅ {module_name}/urls.py dosyası modeller için güncellendi.")

def check_apps_config(module_name):
    """
    apps.py dosyasını kontrol eder ve gerekirse düzeltir
    """
    apps_path = os.path.join(BASE_DIR, module_name, 'apps.py')
    
    if not os.path.exists(apps_path):
        logger.error(f"❌ {module_name}/apps.py dosyası bulunamadı.")
        return
    
    with open(apps_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # name değeri doğru mu kontrol et
    name_match = re.search(r'name\s*=\s*[\'"]([^\'"]*)[\'"]', content)
    if not name_match:
        logger.error(f"❌ {module_name}/apps.py dosyasında name değeri bulunamadı.")
        return
    
    current_name = name_match.group(1)
    
    # name değeri düzeltilmeli mi?
    if current_name != module_name and f'apps.{module_name}' in current_name:
        new_content = content.replace(f"name = '{current_name}'", f"name = '{module_name}'")
        
        with open(apps_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        logger.info(f"✅ {module_name}/apps.py dosyasındaki name değeri '{module_name}' olarak güncellendi.")
    elif current_name != module_name:
        logger.warning(f"⚠️ {module_name}/apps.py dosyasındaki name değeri '{current_name}' olarak tanımlanmış, doğruluğunu kontrol edin.")

def fix_templates_dir(module_name):
    """
    Template dizinini oluşturur veya düzeltir
    """
    templates_dir = os.path.join(BASE_DIR, module_name, 'templates')
    module_templates_dir = os.path.join(templates_dir, module_name)
    
    # Templates dizini var mı?
    if not os.path.exists(templates_dir):
        os.makedirs(templates_dir)
        logger.info(f"✅ {module_name}/templates/ dizini oluşturuldu.")
    
    # Module templates dizini var mı?
    if not os.path.exists(module_templates_dir):
        os.makedirs(module_templates_dir)
        logger.info(f"✅ {module_name}/templates/{module_name}/ dizini oluşturuldu.")

def fix_mvt_structure():
    """
    Tüm MVT yapısını kontrol edip düzeltir
    """
    logger.info("\n🔧 FinAsis MVT Yapı Düzeltme Aracı")
    logger.info("===================================\n")
    
    # Django modüllerini bul
    modules = find_django_modules()
    logger.info(f"Bulunan Django modülleri: {len(modules)}")
    
    # Her modül için kontrol ve düzeltme işlemleri
    for module_name in modules:
        logger.info(f"\n[{module_name}] modülü kontrol ediliyor...")
        
        # apps.py kontrolü
        check_apps_config(module_name)
        
        # urls.py kontrolü
        urls_path = os.path.join(BASE_DIR, module_name, 'urls.py')
        if not os.path.exists(urls_path):
            create_missing_urls_file(module_name)
        
        # views.py kontrolü
        views_path = os.path.join(BASE_DIR, module_name, 'views.py')
        views_dir = os.path.join(BASE_DIR, module_name, 'views')
        if not os.path.exists(views_path) and not os.path.exists(views_dir):
            create_missing_views_file(module_name)
        
        # templates dizini kontrolü
        fix_templates_dir(module_name)
        
        # Modelleri topla
        models = collect_models(module_name)
        if models:
            logger.info(f"{module_name} modülünde {len(models)} model bulundu: {', '.join(models)}")
            
            # Model şablonları kontrolü
            create_missing_model_templates(module_name, models)
            
            # View'leri güncelle
            update_views_for_models(module_name, models)
            
            # URL'leri güncelle
            update_urls_for_models(module_name, models)
        else:
            logger.info(f"{module_name} modülünde model bulunamadı.")
    
    logger.info("\n✅ MVT yapısı düzeltme işlemi tamamlandı!")
    logger.info("Lütfen yapılan değişiklikleri kontrol edin ve gerekirse düzenlemeler yapın.")
    logger.info("Detaylı log için mvt_fix.log dosyasını inceleyebilirsiniz.\n")

if __name__ == "__main__":
    fix_mvt_structure() 