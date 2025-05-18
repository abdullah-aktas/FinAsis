# -*- coding: utf-8 -*-
#!/usr/bin/env python
"""
Bu script, eksik template dosyalarını otomatik olarak oluşturur.
"""
import os
import sys
from pathlib import Path

# Proje kök dizinini ekle
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# Django ayarlarını yükle
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
import django
django.setup()

from django.apps import apps
from django.template.loader import render_to_string
from django.conf import settings

def create_template(app_label, model_name, template_type):
    """
    Belirtilen model için template dosyası oluşturur.
    """
    template_dir = Path(settings.BASE_DIR) / app_label / 'templates' / app_label
    template_dir.mkdir(parents=True, exist_ok=True)
    
    template_name = f"{model_name.lower()}_{template_type}.html"
    template_path = template_dir / template_name
    
    if template_path.exists():
        print(f"Template zaten mevcut: {template_path}")
        return
    
    context = {
        'app_label': app_label,
        'model_name': model_name,
        'model_name_lower': model_name.lower(),
    }
    
    template_content = render_to_string(f'base/{template_type}.html', context)
    
    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(template_content)
    
    print(f"Template oluşturuldu: {template_path}")

def create_base_templates():
    """
    Temel template dosyalarını oluşturur.
    """
    base_template_dir = Path(settings.BASE_DIR) / 'templates' / 'base'
    base_template_dir.mkdir(parents=True, exist_ok=True)
    
    templates = {
        'list.html': '''
{% extends "base.html" %}
{% load i18n %}

{% block title %}{{ model_name }} Listesi{% endblock %}

{% block content %}
<div class="container">
    <h1>{{ model_name }} Listesi</h1>
    
    <div class="mb-3">
        <a href="{% url '{{ app_label }}:{{ model_name_lower }}_create' %}" class="btn btn-primary">
            <i class="fas fa-plus"></i> Yeni {{ model_name }}
        </a>
    </div>
    
    <div class="card">
        <div class="card-body">
            <div class="table-responsive">
                <table class="table table-striped">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Ad</th>
                            <th>Oluşturulma Tarihi</th>
                            <th>İşlemler</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for object in object_list %}
                        <tr>
                            <td>{{ object.id }}</td>
                            <td>{{ object }}</td>
                            <td>{{ object.created_at|date:"d.m.Y H:i" }}</td>
                            <td>
                                <a href="{% url '{{ app_label }}:{{ model_name_lower }}_detail' object.id %}" class="btn btn-info btn-sm">
                                    <i class="fas fa-eye"></i>
                                </a>
                                <a href="{% url '{{ app_label }}:{{ model_name_lower }}_update' object.id %}" class="btn btn-warning btn-sm">
                                    <i class="fas fa-edit"></i>
                                </a>
                                <a href="{% url '{{ app_label }}:{{ model_name_lower }}_delete' object.id %}" class="btn btn-danger btn-sm">
                                    <i class="fas fa-trash"></i>
                                </a>
                            </td>
                        </tr>
                        {% empty %}
                        <tr>
                            <td colspan="4" class="text-center">Kayıt bulunamadı.</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
            
            {% if is_paginated %}
            <nav aria-label="Page navigation">
                <ul class="pagination justify-content-center">
                    {% if page_obj.has_previous %}
                    <li class="page-item">
                        <a class="page-link" href="?page={{ page_obj.previous_page_number }}">Önceki</a>
                    </li>
                    {% endif %}
                    
                    {% for i in paginator.page_range %}
                    <li class="page-item {% if page_obj.number == i %}active{% endif %}">
                        <a class="page-link" href="?page={{ i }}">{{ i }}</a>
                    </li>
                    {% endfor %}
                    
                    {% if page_obj.has_next %}
                    <li class="page-item">
                        <a class="page-link" href="?page={{ page_obj.next_page_number }}">Sonraki</a>
                    </li>
                    {% endif %}
                </ul>
            </nav>
            {% endif %}
        </div>
    </div>
</div>
{% endblock %}
''',
        'detail.html': '''
{% extends "base.html" %}
{% load i18n %}

{% block title %}{{ object }} Detayı{% endblock %}

{% block content %}
<div class="container">
    <div class="row">
        <div class="col-md-12">
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">{{ object }}</h3>
                </div>
                <div class="card-body">
                    <dl class="row">
                        {% for field in object._meta.fields %}
                        <dt class="col-sm-3">{{ field.verbose_name }}</dt>
                        <dd class="col-sm-9">{{ object|getattribute:field.name }}</dd>
                        {% endfor %}
                    </dl>
                </div>
                <div class="card-footer">
                    <a href="{% url '{{ app_label }}:{{ model_name_lower }}_list' %}" class="btn btn-secondary">
                        <i class="fas fa-arrow-left"></i> Geri
                    </a>
                    <a href="{% url '{{ app_label }}:{{ model_name_lower }}_update' object.id %}" class="btn btn-warning">
                        <i class="fas fa-edit"></i> Düzenle
                    </a>
                    <a href="{% url '{{ app_label }}:{{ model_name_lower }}_delete' object.id %}" class="btn btn-danger">
                        <i class="fas fa-trash"></i> Sil
                    </a>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
''',
        'form.html': '''
{% extends "base.html" %}
{% load i18n %}
{% load crispy_forms_tags %}

{% block title %}
    {% if object %}
        {{ object }} Düzenle
    {% else %}
        Yeni {{ model_name }}
    {% endif %}
{% endblock %}

{% block content %}
<div class="container">
    <div class="row">
        <div class="col-md-12">
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">
                        {% if object %}
                            {{ object }} Düzenle
                        {% else %}
                            Yeni {{ model_name }}
                        {% endif %}
                    </h3>
                </div>
                <form method="post" enctype="multipart/form-data">
                    <div class="card-body">
                        {% csrf_token %}
                        {{ form|crispy }}
                    </div>
                    <div class="card-footer">
                        <button type="submit" class="btn btn-primary">
                            <i class="fas fa-save"></i> Kaydet
                        </button>
                        <a href="{% url '{{ app_label }}:{{ model_name_lower }}_list' %}" class="btn btn-secondary">
                            <i class="fas fa-times"></i> İptal
                        </a>
                    </div>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}
''',
        'confirm_delete.html': '''
{% extends "base.html" %}
{% load i18n %}

{% block title %}{{ object }} Sil{% endblock %}

{% block content %}
<div class="container">
    <div class="row">
        <div class="col-md-12">
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">{{ object }} Sil</h3>
                </div>
                <form method="post">
                    <div class="card-body">
                        {% csrf_token %}
                        <p>{{ object }} kaydını silmek istediğinizden emin misiniz?</p>
                        <p class="text-danger">Bu işlem geri alınamaz!</p>
                    </div>
                    <div class="card-footer">
                        <button type="submit" class="btn btn-danger">
                            <i class="fas fa-trash"></i> Sil
                        </button>
                        <a href="{% url '{{ app_label }}:{{ model_name_lower }}_list' %}" class="btn btn-secondary">
                            <i class="fas fa-times"></i> İptal
                        </a>
                    </div>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}
'''
    }
    
    for template_name, content in templates.items():
        template_path = base_template_dir / template_name
        if not template_path.exists():
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(content.strip())
            print(f"Base template oluşturuldu: {template_path}")

def main():
    """
    Ana fonksiyon
    """
    print("Template oluşturma işlemi başlatılıyor...")
    
    # Temel template'leri oluştur
    create_base_templates()
    
    # Her uygulama için template'leri oluştur
    for app_config in apps.get_app_configs():
        if not app_config.models:
            continue
            
        print(f"\nUygulama: {app_config.label}")
        
        for model in app_config.get_models():
            model_name = model._meta.object_name
            print(f"Model: {model_name}")
            
            # Her model için gerekli template'leri oluştur
            for template_type in ['list', 'detail', 'form', 'confirm_delete']:
                create_template(app_config.label, model_name, template_type)

if __name__ == '__main__':
    main() 