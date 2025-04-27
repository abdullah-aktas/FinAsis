#!/usr/bin/env python
"""
MVT (Model-View-Template) yapısını kontrol eden script
"""
import os
import re
import sys
from pathlib import Path
import tkinter as tk
from tkinter import ttk, scrolledtext
import threading

# Django ayarlarını yükle
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
BASE_DIR = Path(__file__).resolve().parent

# İzlenmemesi gereken dizinler
EXCLUDE_DIRS = ['.git', 'venv', '.venv', '__pycache__', 'node_modules', 'staticfiles',
                'static', 'media', 'dist', 'backups', 'all_backups', 'build',
                '.idea', '.vscode']

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
            if content is None or len(content) < 2:
                print(f"❗ {models_path} dosyası boş veya çok kısa!")
                # Gerekirse otomatik düzeltme eklenebilir
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

def check_views_for_model(module_name, model_name):
    """
    Bir model için view'lerin varlığını kontrol eder
    """
    views_path = os.path.join(BASE_DIR, module_name, 'views.py')
    views_dir = os.path.join(BASE_DIR, module_name, 'views')
    
    found_views = False
    view_files = []
    
    # views.py dosyasını kontrol et
    if os.path.exists(views_path):
        try:
            with open(views_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            if re.search(rf'{model_name}\b', content):
                found_views = True
                view_files.append('views.py')
        except Exception as e:
            print(f"[HATA] {views_path} okunurken hata: {e}")
    
    # views/ dizinini kontrol et
    if os.path.exists(views_dir) and os.path.isdir(views_dir):
        for view_file in os.listdir(views_dir):
            if view_file.endswith('.py'):
                view_file_path = os.path.join(views_dir, view_file)
                try:
                    with open(view_file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if re.search(rf'{model_name}\b', content):
                        found_views = True
                        view_files.append(f'views/{view_file}')
                except Exception as e:
                    print(f"[HATA] {view_file_path} okunurken hata: {e}")
    
    return found_views, view_files

def check_templates_for_model(module_name, model_name):
    """
    Bir model için şablonların varlığını kontrol eder
    """
    templates_dir = os.path.join(BASE_DIR, module_name, 'templates', module_name)
    if not os.path.exists(templates_dir):
        return False, []
    
    # Model adını snake_case'e çevir
    model_snake = ''.join(['_'+c.lower() if c.isupper() else c.lower() for c in model_name]).lstrip('_')
    
    found_templates = False
    template_files = []
    
    # Şablon dosyalarını tara
    for root, _, files in os.walk(templates_dir):
        for file in files:
            if file.endswith('.html') and model_snake in file:
                found_templates = True
                template_files.append(os.path.join(os.path.relpath(root, BASE_DIR), file))
    
    return found_templates, template_files

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
            
        # URL desenleri sayısını çıkar
        path_matches = re.findall(r'path\(', content)
        url_count = len(path_matches)
        
        # app_name tanımlı mı?
        app_name_match = re.search(r'app_name\s*=\s*[\'"](\w+)[\'"]', content)
        app_name = app_name_match.group(1) if app_name_match else None
        
        return True, {'count': url_count, 'app_name': app_name}
        
    except Exception as e:
        print(f"[HATA] {urls_path} okunurken hata: {e}")
        return False, []

def check_apps_config(module_name):
    """
    apps.py dosyasını kontrol eder
    """
    apps_path = os.path.join(BASE_DIR, module_name, 'apps.py')
    
    if not os.path.exists(apps_path):
        return False, {}
    
    try:
        with open(apps_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # name değerini çıkar
        name_match = re.search(r'name\s*=\s*[\'"]([^\'"]*)[\'"]', content)
        name = name_match.group(1) if name_match else None
        
        # verbose_name tanımlı mı?
        verbose_name_match = re.search(r'verbose_name\s*=\s*[\'"]([^\'"]*)[\'"]', content)
        verbose_name = verbose_name_match.group(1) if verbose_name_match else None
        
        return True, {'name': name, 'verbose_name': verbose_name}
        
    except Exception as e:
        print(f"[HATA] {apps_path} okunurken hata: {e}")
        return False, {}

def generate_module_report(module_name):
    """
    Bir modül için rapor oluşturur
    """
    report = {
        'module_name': module_name,
        'apps_config': {},
        'urls': {},
        'models': {},
        'templates_dir': False
    }
    
    # apps.py kontrolü
    has_apps, apps_data = check_apps_config(module_name)
    report['has_apps'] = has_apps
    report['apps_config'] = apps_data
    
    # urls.py kontrolü
    has_urls, urls_data = check_urls_for_module(module_name)
    report['has_urls'] = has_urls
    report['urls'] = urls_data
    
    # models.py kontrolü
    models = collect_models(module_name)
    report['models_count'] = len(models)
    report['models'] = {}
    
    # Templates dizini kontrolü
    templates_dir = os.path.join(BASE_DIR, module_name, 'templates', module_name)
    report['templates_dir'] = os.path.exists(templates_dir)
    
    # Her model için view ve template kontrolü
    for model in models:
        has_views, view_files = check_views_for_model(module_name, model)
        has_templates, template_files = check_templates_for_model(module_name, model)
        
        report['models'][model] = {
            'has_views': has_views,
            'view_files': view_files,
            'has_templates': has_templates,
            'template_files': template_files
        }
    
    return report

def print_module_report(report):
    """
    Modül raporunu ekrana yazdırır
    """
    module_name = report['module_name']
    print(f"\n[{module_name}]")
    
    # apps.py bilgileri
    if report['has_apps']:
        print(f"  AppConfig: Var")
        if report['apps_config']['name'] != module_name:
            print(f"  [UYARI] AppConfig name değeri: '{report['apps_config']['name']}' (Olması gereken: '{module_name}')")
    else:
        print(f"  [UYARI] AppConfig: Yok")
    
    # urls.py bilgileri
    if report['has_urls']:
        print(f"  URLs: Var ({report['urls'].get('count', 0)} URL tanımı)")
        if report['urls'].get('app_name') != module_name:
            print(f"  [UYARI] app_name değeri: '{report['urls'].get('app_name')}' (Olması gereken: '{module_name}')")
    else:
        print(f"  [UYARI] URLs: Yok")
    
    # Model sayısı
    print(f"  Modeller: {report['models_count']}")
    
    # Templates dizini
    if not report['templates_dir']:
        print(f"  [UYARI] Templates Dizini: Yok")
    
    # Her model için bilgiler
    missing_views = []
    missing_templates = []
    
    for model, model_data in report['models'].items():
        if not model_data['has_views']:
            missing_views.append(model)
        
        if not model_data['has_templates']:
            missing_templates.append(model)
    
    if missing_views:
        print(f"  [UYARI] View eksik modeller: {', '.join(missing_views)}")
    
    if missing_templates:
        print(f"  [UYARI] Template eksik modeller: {', '.join(missing_templates)}")

def analyze_mvt_structure():
    """
    Tüm MVT yapısını analiz eder ve bir rapor oluşturur
    """
    print("\nFinAsis - MVT Yapı Analizi")
    print("==============================\n")
    
    modules = find_django_modules()
    print(f"Bulunan Django modülleri: {len(modules)}")
    
    all_reports = {}
    
    for module_name in modules:
        report = generate_module_report(module_name)
        all_reports[module_name] = report
        print_module_report(report)
    
    # Genel eksiklikler
    print("\nGenel Eksiklik Raporu")
    print("=====================\n")
    
    modules_without_apps = [m for m, r in all_reports.items() if not r['has_apps']]
    if modules_without_apps:
        print(f"[UYARI] AppConfig eksik modüller: {', '.join(modules_without_apps)}")
    
    modules_without_urls = [m for m, r in all_reports.items() if not r['has_urls']]
    if modules_without_urls:
        print(f"[UYARI] URLs eksik modüller: {', '.join(modules_without_urls)}")
    
    modules_without_templates = [m for m, r in all_reports.items() if not r['templates_dir']]
    if modules_without_templates:
        print(f"[UYARI] Templates dizini eksik modüller: {', '.join(modules_without_templates)}")
    
    all_missing_views = []
    all_missing_templates = []
    
    for module_name, report in all_reports.items():
        for model, model_data in report['models'].items():
            if not model_data['has_views']:
                all_missing_views.append(f"{module_name}.{model}")
            
            if not model_data['has_templates']:
                all_missing_templates.append(f"{module_name}.{model}")
    
    if all_missing_views:
        print(f"\n[UYARI] View eksik modeller ({len(all_missing_views)}):")
        for model in sorted(all_missing_views):
            print(f"  - {model}")
    
    if all_missing_templates:
        print(f"\n[UYARI] Template eksik modeller ({len(all_missing_templates)}):")
        for model in sorted(all_missing_templates):
            print(f"  - {model}")
    
    # Öneriler
    print("\nÖneriler")
    print("---------\n")
    
    print("1. Eksik AppConfig dosyalarını oluşturun.")
    print("2. Eksik URLs dosyalarını oluşturun ve app_name değerini ayarlayın.")
    print("3. Eksik template dizinlerini oluşturun.")
    print("4. Her model için view tanımlarını ekleyin.")
    print("5. Her model için şablonları oluşturun.")
    print("   a. *_list.html - Liste görünümü")
    print("   b. *_detail.html - Detay görünümü")
    print("   c. *_form.html - Ekleme/düzenleme formu")
    print("   d. *_confirm_delete.html - Silme onayı")

class MVTCheckerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("FinAsis MVT Yapı Analiz Aracı")
        self.root.geometry("800x600")
        
        # Ana frame
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Kontrol butonu
        self.check_button = ttk.Button(self.main_frame, text="Analiz Başlat", command=self.start_analysis)
        self.check_button.grid(row=0, column=0, pady=10)
        
        # Sonuç alanı
        self.result_text = scrolledtext.ScrolledText(self.main_frame, width=80, height=30)
        self.result_text.grid(row=1, column=0, pady=10)
        
        # İlerleme çubuğu
        self.progress = ttk.Progressbar(self.main_frame, length=400, mode='indeterminate')
        self.progress.grid(row=2, column=0, pady=10)
    
    def start_analysis(self):
        self.check_button.config(state='disabled')
        self.progress.start()
        self.result_text.delete(1.0, tk.END)
        
        # Analizi ayrı bir thread'de başlat
        analysis_thread = threading.Thread(target=self.run_analysis)
        analysis_thread.start()
    
    def run_analysis(self):
        try:
            # Analiz sonuçlarını yakala
            import io
            from contextlib import redirect_stdout
            
            output = io.StringIO()
            with redirect_stdout(output):
                analyze_mvt_structure()
            
            # Sonuçları göster
            self.result_text.insert(tk.END, output.getvalue())
            
        except Exception as e:
            self.result_text.insert(tk.END, f"Hata oluştu: {str(e)}")
        
        finally:
            self.progress.stop()
            self.check_button.config(state='normal')

def main():
    root = tk.Tk()
    app = MVTCheckerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--gui":
        main()
    else:
        analyze_mvt_structure() 