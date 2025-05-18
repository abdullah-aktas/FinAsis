# -*- coding: utf-8 -*-
#!/usr/bin/env python
"""
Bu script, MVT (Model-View-Template) yapısındaki eksik template'leri oluşturur.
"""
import os
import re
import sys
from pathlib import Path
import shutil

# Django ayarlarını yükle
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
BASE_DIR = Path(__file__).resolve().parent

# İzlenmemesi gereken dizinler
EXCLUDE_DIRS = ['.git', 'venv', '.venv', '__pycache__', 'node_modules', 'staticfiles',
                'static', 'media', 'dist', 'backups', 'all_backups', 'build',
                '.idea', '.vscode']

# Şablonlar - Çift süslü parantez kullanılarak Django template tag'lerini koruyoruz
INDEX_TEMPLATE = '''{% extends "base.html" %}
{% load i18n %}
{% load static %}

{% block title %}{{ title }}{% endblock %}

{% block content %}
<div class="container mt-5">
    <div class="row">
        <div class="col-md-12">
            <h1 class="mb-4">{% trans 'Hoş Geldiniz' %}</h1>
            <p class="lead">{% trans 'Bu {0} modülünün ana sayfasıdır.' %}</p>
            
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
'''

MODEL_LIST_TEMPLATE = '''{% extends "base.html" %}
{% load i18n %}
{% load static %}

{% block title %}{{ title }}{% endblock %}

{% block content %}
<div class="container mt-5">
    <div class="row">
        <div class="col-md-12">
            <h1 class="mb-4">{% trans '{0} Listesi' %}</h1>
            
            <div class="mb-3">
                <a href="{% url '{1}:{2}_create' %}" class="btn btn-primary">
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
                                        <a href="{% url '{1}:{2}_detail' object.id %}" class="btn btn-sm btn-info">
                                            <i class="fas fa-eye"></i>
                                        </a>
                                        <a href="{% url '{1}:{2}_update' object.id %}" class="btn btn-sm btn-warning">
                                            <i class="fas fa-edit"></i>
                                        </a>
                                        <a href="{% url '{1}:{2}_delete' object.id %}" class="btn btn-sm btn-danger">
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
'''

MODEL_DETAIL_TEMPLATE = '''{% extends "base.html" %}
{% load i18n %}
{% load static %}

{% block title %}{{ title }}{% endblock %}

{% block content %}
<div class="container mt-5">
    <div class="row">
        <div class="col-md-12">
            <h1 class="mb-4">{% trans '{0} Detayı' %}</h1>
            
            <div class="mb-3">
                <a href="{% url '{1}:{2}_list' %}" class="btn btn-secondary">
                    <i class="fas fa-arrow-left"></i> {% trans 'Listeye Dön' %}
                </a>
                <a href="{% url '{1}:{2}_update' object.id %}" class="btn btn-warning">
                    <i class="fas fa-edit"></i> {% trans 'Düzenle' %}
                </a>
                <a href="{% url '{1}:{2}_delete' object.id %}" class="btn btn-danger">
                    <i class="fas fa-trash"></i> {% trans 'Sil' %}
                </a>
            </div>
            
            <div class="card">
                <div class="card-body">
                    <dl class="row">
                        <dt class="col-sm-3">ID</dt>
                        <dd class="col-sm-9">{{ object.id }}</dd>
                        
                        <dt class="col-sm-3">{% trans 'Ad' %}</dt>
                        <dd class="col-sm-9">{{ object }}</dd>
                        
                        {% if object.created_at %}
                        <dt class="col-sm-3">{% trans 'Oluşturulma Tarihi' %}</dt>
                        <dd class="col-sm-9">{{ object.created_at|date:"d.m.Y H:i" }}</dd>
                        {% endif %}
                        
                        {% if object.updated_at %}
                        <dt class="col-sm-3">{% trans 'Güncellenme Tarihi' %}</dt>
                        <dd class="col-sm-9">{{ object.updated_at|date:"d.m.Y H:i" }}</dd>
                        {% endif %}
                    </dl>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
'''

MODEL_FORM_TEMPLATE = '''{% extends "base.html" %}
{% load i18n %}
{% load static %}
{% load crispy_forms_tags %}

{% block title %}{{ title }}{% endblock %}

{% block content %}
<div class="container mt-5">
    <div class="row">
        <div class="col-md-12">
            <h1 class="mb-4">{{ title }}</h1>
            
            <div class="mb-3">
                <a href="{% url '{0}:{1}_list' %}" class="btn btn-secondary">
                    <i class="fas fa-arrow-left"></i> {% trans 'Listeye Dön' %}
                </a>
            </div>
            
            <div class="card">
                <div class="card-body">
                    <form method="post">
                        {% csrf_token %}
                        {{ form|crispy }}
                        
                        <div class="mt-3">
                            <button type="submit" class="btn btn-primary">
                                <i class="fas fa-save"></i> {% trans 'Kaydet' %}
                            </button>
                            <a href="{% url '{0}:{1}_list' %}" class="btn btn-light">
                                <i class="fas fa-times"></i> {% trans 'İptal' %}
                            </a>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
'''

MODEL_DELETE_TEMPLATE = '''{% extends "base.html" %}
{% load i18n %}
{% load static %}

{% block title %}{{ title }}{% endblock %}

{% block content %}
<div class="container mt-5">
    <div class="row">
        <div class="col-md-12">
            <h1 class="mb-4">{% trans '{0} Silme' %}</h1>
            
            <div class="mb-3">
                <a href="{% url '{1}:{2}_list' %}" class="btn btn-secondary">
                    <i class="fas fa-arrow-left"></i> {% trans 'Listeye Dön' %}
                </a>
            </div>
            
            <div class="card border-danger">
                <div class="card-header bg-danger text-white">
                    <h5>{% trans 'Dikkat!' %}</h5>
                </div>
                <div class="card-body">
                    <p class="lead">{% trans 'Bu {0} kaydını silmek istediğinizden emin misiniz?' %}</p>
                    <p><strong>{{ object }}</strong></p>
                    
                    <form method="post">
                        {% csrf_token %}
                        
                        <div class="mt-3">
                            <button type="submit" class="btn btn-danger">
                                <i class="fas fa-trash"></i> {% trans 'Evet, Sil' %}
                            </button>
                            <a href="{% url '{1}:{2}_list' %}" class="btn btn-light">
                                <i class="fas fa-times"></i> {% trans 'İptal' %}
                            </a>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
'''

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
        print(f"[HATA] {module_name} modellerini analiz ederken hata: {e}")
    
    return models

def create_template_dir(module_name):
    """
    Template dizinlerini oluşturur
    """
    templates_dir = os.path.join(BASE_DIR, module_name, 'templates')
    module_templates_dir = os.path.join(templates_dir, module_name)
    
    if not os.path.exists(templates_dir):
        os.makedirs(templates_dir)
        print(f"[BILGI] {module_name}/templates/ dizini oluşturuldu.")
    
    if not os.path.exists(module_templates_dir):
        os.makedirs(module_templates_dir)
        print(f"[BILGI] {module_name}/templates/{module_name}/ dizini oluşturuldu.")
    
    return module_templates_dir

def create_index_template(module_name, templates_dir):
    """
    index.html şablonunu oluşturur
    """
    index_path = os.path.join(templates_dir, 'index.html')
    
    if os.path.exists(index_path):
        print(f"[BILGI] {module_name}/templates/{module_name}/index.html zaten var.")
        return
    
    app_title = module_name.replace('_', ' ').title()
    content = INDEX_TEMPLATE.format(app_title)
    
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"[BILGI] {module_name}/templates/{module_name}/index.html oluşturuldu.")

def create_model_templates(module_name, model_name, templates_dir):
    """
    Model için şablonları oluşturur
    """
    # Model adını snake_case'e çevir
    model_snake = ''.join(['_'+c.lower() if c.isupper() else c.lower() for c in model_name]).lstrip('_')
    model_title = model_name.replace('_', ' ')
    
    # Liste şablonu
    list_path = os.path.join(templates_dir, f"{model_snake}_list.html")
    if not os.path.exists(list_path):
        with open(list_path, 'w', encoding='utf-8') as f:
            content = MODEL_LIST_TEMPLATE.format(
                model_title,
                module_name,
                model_snake
            )
            f.write(content)
        print(f"[BILGI] {model_snake}_list.html oluşturuldu.")
    
    # Detay şablonu
    detail_path = os.path.join(templates_dir, f"{model_snake}_detail.html")
    if not os.path.exists(detail_path):
        with open(detail_path, 'w', encoding='utf-8') as f:
            content = MODEL_DETAIL_TEMPLATE.format(
                model_title,
                module_name,
                model_snake
            )
            f.write(content)
        print(f"[BILGI] {model_snake}_detail.html oluşturuldu.")
    
    # Form şablonu
    form_path = os.path.join(templates_dir, f"{model_snake}_form.html")
    if not os.path.exists(form_path):
        with open(form_path, 'w', encoding='utf-8') as f:
            content = MODEL_FORM_TEMPLATE.format(
                module_name,
                model_snake
            )
            f.write(content)
        print(f"[BILGI] {model_snake}_form.html oluşturuldu.")
    
    # Silme şablonu
    delete_path = os.path.join(templates_dir, f"{model_snake}_confirm_delete.html")
    if not os.path.exists(delete_path):
        with open(delete_path, 'w', encoding='utf-8') as f:
            content = MODEL_DELETE_TEMPLATE.format(
                model_title,
                module_name,
                model_snake
            )
            f.write(content)
        print(f"[BILGI] {model_snake}_confirm_delete.html oluşturuldu.")

def fix_templates():
    """
    MVT yapısındaki eksik şablonları oluşturur
    """
    print("\nFinAsis - MVT Şablon Düzeltme Aracı")
    print("===================================\n")
    
    # Django modüllerini bul
    modules = find_django_modules()
    print(f"Bulunan Django modülleri: {len(modules)}")
    
    for module_name in modules:
        print(f"\n[{module_name}] modülü işleniyor...")
        
        # Template dizinlerini oluştur
        templates_dir = create_template_dir(module_name)
        
        # index.html şablonunu oluştur
        create_index_template(module_name, templates_dir)
        
        # Modelleri topla
        models = collect_models(module_name)
        
        if models:
            print(f"{module_name} modülünde {len(models)} model bulundu.")
            
            # Her model için şablonları oluştur
            for model_name in models:
                create_model_templates(module_name, model_name, templates_dir)
        else:
            print(f"{module_name} modülünde model bulunamadı.")
    
    print("\nŞablon düzeltme işlemi tamamlandı!")

if __name__ == "__main__":
    fix_templates() 