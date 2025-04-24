#!/usr/bin/env python
"""
Bu script, Django projesindeki tüm model-view-template ilişkilerini kontrol eder
ve eksikleri raporlar.
"""
import os
import re
import importlib
import sys
from pathlib import Path
from collections import defaultdict
from typing import Dict, List

# Django ayarlarını yükle
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
BASE_DIR = Path(__file__).resolve().parent

# İzlenmemesi gereken dizinler
EXCLUDE_DIRS = ['.git', 'venv', '.venv', '__pycache__', 'node_modules', 'staticfiles', 
                'static', 'media', 'dist', 'backups', 'all_backups', 'build']

def is_excluded_dir(path):
    """
    Dizinin dışlanması gereken bir dizin olup olmadığını kontrol eder
    """
    for exclude in EXCLUDE_DIRS:
        if exclude in path:
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
        print(f"❌ {module_name} modellerini analiz ederken hata: {e}")
    
    return models

def check_views_for_model(module_name, model_name):
    """
    Bir model için view'lerin varlığını kontrol eder
    """
    views_path = os.path.join(BASE_DIR, module_name, 'views.py')
    views_dir = os.path.join(BASE_DIR, module_name, 'views')
    
    found_in_views = False
    view_references = []
    
    # views.py dosyasını kontrol et
    if os.path.exists(views_path):
        try:
            with open(views_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            if re.search(rf'{model_name}\b', content):
                found_in_views = True
                view_references.append('views.py')
        except Exception as e:
            print(f"❌ {views_path} dosyasını kontrol ederken hata: {e}")
    
    # views/ dizinini kontrol et
    if os.path.exists(views_dir) and os.path.isdir(views_dir):
        for view_file in os.listdir(views_dir):
            if view_file.endswith('.py'):
                view_file_path = os.path.join(views_dir, view_file)
                try:
                    with open(view_file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if re.search(rf'{model_name}\b', content):
                        found_in_views = True
                        view_references.append(f'views/{view_file}')
                except Exception as e:
                    print(f"❌ {view_file_path} dosyasını kontrol ederken hata: {e}")
    
    return found_in_views, view_references

def check_urls_for_module(module_name):
    """
    Bir modülün urls.py dosyasını kontrol eder
    """
    urls_path = os.path.join(BASE_DIR, module_name, 'urls.py')
    
    if not os.path.exists(urls_path):
        return False, []
    
    try:
        with open(urls_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # URL patternlerini bul
        urlpatterns_match = re.search(r'urlpatterns\s*=\s*\[(.*?)\]', content, re.DOTALL)
        if not urlpatterns_match:
            return False, []
            
        urlpatterns_content = urlpatterns_match.group(1)
        path_pattern = r'path\([\'"]([^\'"]*)[\'"].*?[\'"]([^\'"]*)[\'"]'
        url_patterns = re.findall(path_pattern, urlpatterns_content)
        
        return True, url_patterns
    except Exception as e:
        print(f"❌ {urls_path} dosyasını kontrol ederken hata: {e}")
        return False, []

def check_templates_for_model(module_name, model_name):
    """
    Bir model için şablonların varlığını kontrol eder
    """
    templates_dir = os.path.join(BASE_DIR, module_name, 'templates', module_name)
    if not os.path.exists(templates_dir):
        return False, []
    
    # Model adını snake_case'e çevir
    snake_case_model = ''.join(['_'+c.lower() if c.isupper() else c.lower() for c in model_name]).lstrip('_')
    template_files = []
    
    # Şablon dosyalarını tara
    for root, _, files in os.walk(templates_dir):
        for file in files:
            if file.endswith('.html'):
                if snake_case_model in file:
                    template_files.append(os.path.join(os.path.relpath(root, BASE_DIR), file))
    
    return len(template_files) > 0, template_files

def check_model_relationships(model_content: str) -> Dict[str, List[str]]:
    """
    Model ilişkilerini kontrol eder
    
    Args:
        model_content: Model dosyasının içeriği
        
    Returns:
        Dict[str, List[str]]: İlişki türlerine göre tespit edilen alanlar
    """
    relationships = {
        'foreign_key': [],
        'one_to_one': [],
        'many_to_many': [],
        'missing_related_name': [],
        'missing_on_delete': []
    }
    
    # ForeignKey ve OneToOne ilişkilerini bul
    fk_pattern = r'(\w+)\s*=\s*models\.(?:ForeignKey|OneToOneField)\((.*?)\)'
    for match in re.finditer(fk_pattern, model_content, re.DOTALL):
        field_name = match.group(1)
        params = match.group(2)
        
        if 'ForeignKey' in match.group(0):
            relationships['foreign_key'].append(field_name)
        else:
            relationships['one_to_one'].append(field_name)
        
        # related_name kontrolü
        if 'related_name' not in params:
            relationships['missing_related_name'].append(field_name)
        
        # on_delete kontrolü
        if 'on_delete' not in params:
            relationships['missing_on_delete'].append(field_name)
    
    # ManyToMany ilişkilerini bul
    m2m_pattern = r'(\w+)\s*=\s*models\.ManyToManyField\((.*?)\)'
    for match in re.finditer(m2m_pattern, model_content, re.DOTALL):
        field_name = match.group(1)
        relationships['many_to_many'].append(field_name)
        
        # related_name kontrolü
        if 'related_name' not in match.group(2):
            relationships['missing_related_name'].append(field_name)
    
    return relationships

def check_model_validations(model_content: str) -> Dict[str, List[str]]:
    """
    Model validasyonlarını kontrol eder
    
    Args:
        model_content: Model dosyasının içeriği
        
    Returns:
        Dict[str, List[str]]: Validasyon türlerine göre tespit edilen alanlar
    """
    validations = {
        'unique': [],
        'unique_together': [],
        'custom_validators': [],
        'missing_validators': []
    }
    
    # Unique alanları bul
    unique_pattern = r'(\w+)\s*=\s*models\.\w+Field\(.*?unique\s*=\s*True'
    for match in re.finditer(unique_pattern, model_content):
        validations['unique'].append(match.group(1))
    
    # Unique_together tanımlarını bul
    unique_together_pattern = r'unique_together\s*=\s*\[(.*?)\]'
    for match in re.finditer(unique_together_pattern, model_content, re.DOTALL):
        fields = [f.strip().strip("'") for f in match.group(1).split(',')]
        validations['unique_together'].extend(fields)
    
    # Custom validatörleri bul
    validator_pattern = r'validators\s*=\s*\[(.*?)\]'
    for match in re.finditer(validator_pattern, model_content):
        if 'django.core.validators' not in match.group(1):
            validations['custom_validators'].append(match.group(1))
    
    # Validatör eksikliği olan alanları bul
    field_pattern = r'(\w+)\s*=\s*models\.\w+Field\(\)'
    for match in re.finditer(field_pattern, model_content):
        field_name = match.group(1)
        if field_name not in validations['unique'] and field_name not in validations['unique_together']:
            validations['missing_validators'].append(field_name)
    
    return validations

def check_model_performance(model_content: str) -> Dict[str, List[str]]:
    """
    Model performans optimizasyonlarını kontrol eder
    
    Args:
        model_content: Model dosyasının içeriği
        
    Returns:
        Dict[str, List[str]]: Performans özelliklerine göre tespit edilen alanlar
    """
    performance = {
        'indexes': [],
        'missing_indexes': [],
        'select_related': [],
        'prefetch_related': []
    }
    
    # İndeksleri bul
    index_pattern = r'class\s+Meta:.*?indexes\s*=\s*\[(.*?)\]'
    for match in re.finditer(index_pattern, model_content, re.DOTALL):
        indexes = [i.strip().strip("'") for i in match.group(1).split(',')]
        performance['indexes'].extend(indexes)
    
    # ForeignKey ve OneToOne alanları için indeks kontrolü
    fk_pattern = r'(\w+)\s*=\s*models\.(?:ForeignKey|OneToOneField)'
    for match in re.finditer(fk_pattern, model_content):
        field_name = match.group(1)
        if field_name not in performance['indexes']:
            performance['missing_indexes'].append(field_name)
    
    # Select_related ve prefetch_related kullanımlarını bul
    query_pattern = r'\.(?:select_related|prefetch_related)\((.*?)\)'
    for match in re.finditer(query_pattern, model_content):
        fields = [f.strip().strip("'") for f in match.group(1).split(',')]
        if 'select_related' in match.group(0):
            performance['select_related'].extend(fields)
        else:
            performance['prefetch_related'].extend(fields)
    
    return performance

def check_model_security(model_content: str) -> Dict[str, List[str]]:
    """
    Model güvenlik kontrollerini yapar
    
    Args:
        model_content: Model dosyasının içeriği
        
    Returns:
        Dict[str, List[str]]: Güvenlik özelliklerine göre tespit edilen alanlar
    """
    security = {
        'sensitive_fields': [],
        'encrypted_fields': [],
        'permission_checks': [],
        'missing_permissions': []
    }
    
    # Hassas veri alanlarını bul
    sensitive_patterns = [
        r'password',
        r'secret',
        r'key',
        r'token',
        r'credit',
        r'card',
        r'pin',
        r'passport',
        r'identity'
    ]
    
    for pattern in sensitive_patterns:
        for match in re.finditer(fr'(\w+)\s*=\s*models\.\w+Field\(.*?{pattern}', model_content, re.IGNORECASE):
            field_name = match.group(1)
            if field_name not in security['sensitive_fields']:
                security['sensitive_fields'].append(field_name)
    
    # Şifrelenmiş alanları bul
    encrypted_pattern = r'(\w+)\s*=\s*Encrypted(?:Char|TextField)'
    for match in re.finditer(encrypted_pattern, model_content):
        field_name = match.group(1)
        security['encrypted_fields'].append(field_name)
    
    # İzin kontrollerini bul
    permission_pattern = r'@permission_required\([\'"](.*?)[\'"]\)'
    for match in re.finditer(permission_pattern, model_content):
        permission = match.group(1)
        security['permission_checks'].append(permission)
    
    # Eksik izin kontrollerini bul
    view_pattern = r'def\s+(\w+)\s*\(.*?\):'
    for match in re.finditer(view_pattern, model_content):
        view_name = match.group(1)
        if view_name not in [p.split('.')[-1] for p in security['permission_checks']]:
            security['missing_permissions'].append(view_name)
    
    return security

def analyze_project():
    """
    Projeyi analiz eder ve bir rapor oluşturur
    """
    print("\n🔍 Django MVT Yapısı Analizi")
    print("===============================\n")
    
    modules = find_django_modules()
    print(f"Bulunan Django modülleri: {len(modules)}")
    
    all_models = {}
    model_view_map = {}
    model_template_map = {}
    module_urls_map = {}
    model_relationships = {}
    model_validations = {}
    model_performance = {}
    model_security = {}
    
    # Modelleri topla
    for module in modules:
        models = collect_models(module)
        all_models[module] = models
        
        # Her modül için URL patternlerini kontrol et
        has_urls, patterns = check_urls_for_module(module)
        module_urls_map[module] = {'has_urls': has_urls, 'patterns': patterns}
        
        # Her model için detaylı analiz yap
        for model in models:
            model_path = os.path.join(BASE_DIR, module, 'models.py')
            if os.path.exists(model_path):
                with open(model_path, 'r', encoding='utf-8') as f:
                    model_content = f.read()
                
                # Model ilişkilerini kontrol et
                model_relationships[f"{module}.{model}"] = check_model_relationships(model_content)
                
                # Model validasyonlarını kontrol et
                model_validations[f"{module}.{model}"] = check_model_validations(model_content)
                
                # Model performansını kontrol et
                model_performance[f"{module}.{model}"] = check_model_performance(model_content)
                
                # Model güvenliğini kontrol et
                model_security[f"{module}.{model}"] = check_model_security(model_content)
            
            # View ve şablonları kontrol et
            has_views, view_references = check_views_for_model(module, model)
            has_templates, template_files = check_templates_for_model(module, model)
            
            model_view_map[f"{module}.{model}"] = {'has_views': has_views, 'view_references': view_references}
            model_template_map[f"{module}.{model}"] = {'has_templates': has_templates, 'template_files': template_files}
    
    # Rapor oluştur
    print("\n📊 Modül ve Model Analizi")
    print("------------------------\n")
    
    for module, models in all_models.items():
        print(f"\n[{module}]")
        print(f"  📋 Modeller: {len(models)}")
        
        # URLs
        if module_urls_map[module]['has_urls']:
            print(f"  ✅ URL yapılandırması: Var ({len(module_urls_map[module]['patterns'])} pattern)")
        else:
            print(f"  ❌ URL yapılandırması: Yok")
        
        # Her model için detaylar
        for model in models:
            model_key = f"{module}.{model}"
            print(f"    📦 {model}")
            
            # Views
            if model_view_map[model_key]['has_views']:
                print(f"      ✅ View: Var ({', '.join(model_view_map[model_key]['view_references'])})")
            else:
                print(f"      ❌ View: Yok")
            
            # Templates
            if model_template_map[model_key]['has_templates']:
                print(f"      ✅ Template: Var ({len(model_template_map[model_key]['template_files'])} şablon)")
            else:
                print(f"      ❌ Template: Yok")
            
            # İlişkiler
            relationships = model_relationships.get(model_key, {})
            if relationships:
                print("      🔗 İlişkiler:")
                for rel_type, fields in relationships.items():
                    if fields:
                        print(f"        - {rel_type}: {', '.join(fields)}")
            
            # Validasyonlar
            validations = model_validations.get(model_key, {})
            if validations:
                print("      ✓ Validasyonlar:")
                for val_type, fields in validations.items():
                    if fields:
                        print(f"        - {val_type}: {', '.join(fields)}")
            
            # Performans
            performance = model_performance.get(model_key, {})
            if performance:
                print("      ⚡ Performans:")
                for perf_type, fields in performance.items():
                    if fields:
                        print(f"        - {perf_type}: {', '.join(fields)}")
            
            # Güvenlik
            security = model_security.get(model_key, {})
            if security:
                print("      🔒 Güvenlik:")
                for sec_type, fields in security.items():
                    if fields:
                        print(f"        - {sec_type}: {', '.join(fields)}")
    
    # Eksikleri raporla
    print("\n⚠️ Eksiklikler")
    print("-------------\n")
    
    missing_urls = [module for module, data in module_urls_map.items() if not data['has_urls']]
    if missing_urls:
        print(f"❌ URL yapılandırması eksik modüller: {', '.join(missing_urls)}")
    
    missing_views = [key for key, data in model_view_map.items() if not data['has_views']]
    if missing_views:
        print(f"❌ View tanımı eksik modeller: {', '.join(missing_views)}")
    
    missing_templates = [key for key, data in model_template_map.items() if not data['has_templates']]
    if missing_templates:
        print(f"❌ Template eksik modeller: {', '.join(missing_templates)}")
    
    # İlişki eksiklikleri
    for model_key, relationships in model_relationships.items():
        if relationships['missing_related_name']:
            print(f"❌ Related name eksik ilişkiler ({model_key}): {', '.join(relationships['missing_related_name'])}")
        if relationships['missing_on_delete']:
            print(f"❌ On_delete eksik ilişkiler ({model_key}): {', '.join(relationships['missing_on_delete'])}")
    
    # Validasyon eksiklikleri
    for model_key, validations in model_validations.items():
        if validations['missing_validators']:
            print(f"❌ Validatör eksik alanlar ({model_key}): {', '.join(validations['missing_validators'])}")
    
    # Performans eksiklikleri
    for model_key, performance in model_performance.items():
        if performance['missing_indexes']:
            print(f"❌ İndeks eksik alanlar ({model_key}): {', '.join(performance['missing_indexes'])}")
    
    # Güvenlik eksiklikleri
    for model_key, security in model_security.items():
        if security['sensitive_fields'] and not security['encrypted_fields']:
            print(f"❌ Şifrelenmemiş hassas alanlar ({model_key}): {', '.join(security['sensitive_fields'])}")
        if security['missing_permissions']:
            print(f"❌ İzin kontrolü eksik view'lar ({model_key}): {', '.join(security['missing_permissions'])}")
    
    print("\n✅ Analiz tamamlandı!")
    
    # Öneriler
    print("\n💡 Öneriler")
    print("---------\n")
    
    print("1. Eksik URL yapılandırması olan modüller için urls.py dosyası oluşturun.")
    print("2. Eksik view tanımı olan modeller için view fonksiyonları veya sınıfları oluşturun.")
    print("3. Eksik şablonları tamamlayın (model_list.html, model_detail.html, model_form.html).")
    print("4. Her modülün urls.py dosyasında app_name tanımladığınızdan emin olun.")
    print("5. Her modülün apps.py dosyasında AppConfig sınıfını doğru yapılandırdığınızdan emin olun.")
    print("6. İlişkilerde related_name ve on_delete parametrelerini belirtin.")
    print("7. Hassas veri alanlarını şifreleyin.")
    print("8. Performans için gerekli indeksleri ekleyin.")
    print("9. View'larda gerekli izin kontrollerini yapın.")
    print("10. Validasyon kurallarını eksiksiz tanımlayın.\n")

if __name__ == "__main__":
    analyze_project() 