# -*- coding: utf-8 -*-
import os
import django
from django.conf import settings
from django.template.loader import render_to_string
from django.template import Template, Context

# Django ayarlarını yükle
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FinAsis.settings')
django.setup()

# Template oluşturma fonksiyonları
def create_list_template(app_name, model_name):
    content = '''
{% extends "base.html" %}
{% load static %}

{% block title %}{{ model_name_plural }} Listesi{% endblock %}

{% block content %}
<div class="container mt-4">
    <h2>{{ model_name_plural }}</h2>
    <div class="d-flex justify-content-between mb-3">
        <div>
            <a href="{% url '{{ app_name }}:{{ model_name_lower }}_create' %}" class="btn btn-primary">
                <i class="fas fa-plus"></i> Yeni {{ model_name }}
            </a>
        </div>
        <div class="d-flex">
            <input type="text" class="form-control me-2" id="searchInput" placeholder="Ara...">
            <select class="form-select me-2" id="filterSelect">
                <option value="">Tümü</option>
            </select>
        </div>
    </div>

    <div class="table-responsive">
        <table class="table table-hover">
            <thead>
                <tr>
                    {% for field in fields %}
                    <th>{{ field.verbose_name }}</th>
                    {% endfor %}
                    <th>İşlemler</th>
                </tr>
            </thead>
            <tbody>
                {% for object in object_list %}
                <tr>
                    {% for field in fields %}
                    <td>{{ object|get_field_value:field.name }}</td>
                    {% endfor %}
                    <td>
                        <a href="{% url '{{ app_name }}:{{ model_name_lower }}_detail' object.pk %}" 
                           class="btn btn-info btn-sm">
                            <i class="fas fa-eye"></i>
                        </a>
                        <a href="{% url '{{ app_name }}:{{ model_name_lower }}_update' object.pk %}" 
                           class="btn btn-warning btn-sm">
                            <i class="fas fa-edit"></i>
                        </a>
                        <a href="{% url '{{ app_name }}:{{ model_name_lower }}_delete' object.pk %}" 
                           class="btn btn-danger btn-sm">
                            <i class="fas fa-trash"></i>
                        </a>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>

    {% include "includes/pagination.html" %}
</div>
{% endblock %}

{% block extra_js %}
<script src="{% static 'js/list-view.js' %}"></script>
{% endblock %}
'''
    return content

def create_detail_template(app_name, model_name):
    content = '''
{% extends "base.html" %}
{% load static %}

{% block title %}{{ object }} Detay{% endblock %}

{% block content %}
<div class="container mt-4">
    <div class="card">
        <div class="card-header d-flex justify-content-between align-items-center">
            <h3>{{ object }}</h3>
            <div>
                <a href="{% url '{{ app_name }}:{{ model_name_lower }}_update' object.pk %}" 
                   class="btn btn-warning">
                    <i class="fas fa-edit"></i> Düzenle
                </a>
                <a href="{% url '{{ app_name }}:{{ model_name_lower }}_delete' object.pk %}" 
                   class="btn btn-danger">
                    <i class="fas fa-trash"></i> Sil
                </a>
            </div>
        </div>
        <div class="card-body">
            {% for field in fields %}
            <div class="row mb-3">
                <div class="col-md-3 fw-bold">{{ field.verbose_name }}</div>
                <div class="col-md-9">{{ object|get_field_value:field.name }}</div>
            </div>
            {% endfor %}
        </div>
    </div>

    <div class="mt-3">
        <a href="{% url '{{ app_name }}:{{ model_name_lower }}_list' %}" class="btn btn-secondary">
            <i class="fas fa-arrow-left"></i> Listeye Dön
        </a>
    </div>
</div>
{% endblock %}
'''
    return content

def create_form_template(app_name, model_name):
    content = '''
{% extends "base.html" %}
{% load static %}
{% load crispy_forms_tags %}

{% block title %}
    {% if object %}{{ object }} Düzenle{% else %}Yeni {{ model_name }}{% endif %}
{% endblock %}

{% block content %}
<div class="container mt-4">
    <div class="card">
        <div class="card-header">
            <h3>{% if object %}{{ object }} Düzenle{% else %}Yeni {{ model_name }}{% endif %}</h3>
        </div>
        <div class="card-body">
            <form method="post" enctype="multipart/form-data">
                {% csrf_token %}
                {{ form|crispy }}
                <div class="mt-3">
                    <button type="submit" class="btn btn-primary">
                        <i class="fas fa-save"></i> Kaydet
                    </button>
                    <a href="{% url '{{ app_name }}:{{ model_name_lower }}_list' %}" 
                       class="btn btn-secondary">
                        <i class="fas fa-times"></i> İptal
                    </a>
                </div>
            </form>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script src="{% static 'js/form-validation.js' %}"></script>
{% endblock %}
'''
    return content

def create_delete_template(app_name, model_name):
    content = '''
{% extends "base.html" %}

{% block title %}{{ object }} Sil{% endblock %}

{% block content %}
<div class="container mt-4">
    <div class="card">
        <div class="card-header">
            <h3>{{ object }} Sil</h3>
        </div>
        <div class="card-body">
            <p>{{ object }} kaydını silmek istediğinizden emin misiniz?</p>
            <form method="post">
                {% csrf_token %}
                <button type="submit" class="btn btn-danger">
                    <i class="fas fa-trash"></i> Evet, Sil
                </button>
                <a href="{% url '{{ app_name }}:{{ model_name_lower }}_list' %}" 
                   class="btn btn-secondary">
                    <i class="fas fa-times"></i> İptal
                </a>
            </form>
        </div>
    </div>
</div>
{% endblock %}
'''
    return content

def generate_templates():
    # Django uygulamalarını ve modellerini al
    from django.apps import apps
    
    missing_templates = {
        'ai_assistant': ['AIModel', 'UserInteraction', 'FinancialPrediction', 'AIFeedback', 
                        'FinancialReport', 'AnomalyDetection', 'TrendAnalysis', 'UserPreference', 
                        'AIInsight', 'Notification'],
        'analytics': ['AnalyticsDashboard', 'DashboardWidget', 'AnalyticsReport', 'DataSource'],
        'assets': ['AssetCategory', 'Asset', 'Depreciation', 'Maintenance', 'AssetTransfer', 
                  'AssetDisposal', 'AssetRental'],
        'assistant': ['AssistantCapability', 'ChatMessage', 'AssistantPerformance'],
        'blockchain': ['BaseModel', 'BlockchainNetwork', 'SmartContract', 'Wallet', 'Token', 
                      'BlockchainTransaction', 'BlockchainLog', 'TokenContract', 'TokenBalance', 
                      'TokenTransaction'],
        'hr_management': ['Employee', 'Department', 'Salary', 'Payroll', 'Leave'],
        'integrations': ['IntegrationConfig', 'SyncLog', 'WebhookLog', 'IntegrationTask'],
        'permissions': ['Permission', 'Role', 'UserRole'],
        'seo': ['SEOMetadata', 'SEORedirect', 'SEOKeyword', 'SEOAnalytics'],
        'stock_management': ['Category', 'StockMovement', 'StockAlert'],
        'users': ['UserProfile', 'UserPreferences', 'UserNotification', 'UserSession', 'UserSettings'],
        'virtual_company': ['VirtualCompany', 'Employee', 'Project', 'PerformanceReview', 'Budget', 
                          'Report', 'Product', 'StockMovement', 'ProductionOrder', 'BillOfMaterials', 
                          'QualityControl', 'ModuleSetting', 'UserDailyTask', 'KnowledgeBaseRelatedItem']
    }

    for app_name, models in missing_templates.items():
        # Template dizinini oluştur
        template_dir = os.path.join(settings.BASE_DIR, app_name, 'templates', app_name)
        os.makedirs(template_dir, exist_ok=True)

        for model_name in models:
            # Her model için template'leri oluştur
            templates = {
                f'{model_name.lower()}_list.html': create_list_template(app_name, model_name),
                f'{model_name.lower()}_detail.html': create_detail_template(app_name, model_name),
                f'{model_name.lower()}_form.html': create_form_template(app_name, model_name),
                f'{model_name.lower()}_confirm_delete.html': create_delete_template(app_name, model_name)
            }

            for template_name, content in templates.items():
                template_path = os.path.join(template_dir, template_name)
                with open(template_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f'Created template: {template_path}')

if __name__ == '__main__':
    generate_templates() 