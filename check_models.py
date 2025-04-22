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
    
    # Modelleri topla
    for module in modules:
        models = collect_models(module)
        all_models[module] = models
        
        # Her modül için URL patternlerini kontrol et
        has_urls, patterns = check_urls_for_module(module)
        module_urls_map[module] = {'has_urls': has_urls, 'patterns': patterns}
        
        # Her model için view ve şablonları kontrol et
        for model in models:
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
    
    print("\n✅ Analiz tamamlandı!")
    
    # Öneriler
    print("\n💡 Öneriler")
    print("---------\n")
    
    print("1. Eksik URL yapılandırması olan modüller için urls.py dosyası oluşturun.")
    print("2. Eksik view tanımı olan modeller için view fonksiyonları veya sınıfları oluşturun.")
    print("3. Eksik şablonları tamamlayın (model_list.html, model_detail.html, model_form.html).")
    print("4. Her modülün urls.py dosyasında app_name tanımladığınızdan emin olun.")
    print("5. Her modülün apps.py dosyasında AppConfig sınıfını doğru yapılandırdığınızdan emin olun.\n")

if __name__ == "__main__":
    analyze_project() 