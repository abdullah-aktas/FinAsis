import os
from pathlib import Path

# Kök dizin
ROOT = Path(__file__).parent.resolve()

# Ortak ve altyapı klasörleri (korunacaklar)
CORE_FOLDERS = {
    'core', 'utils', 'config', 'settings', 'static', 'staticfiles', 'templates', 'scripts', 'docs', 'tests',
    'assets', 'locale', 'build', 'dist', 'deployment', 'docker', '.github', '.vscode', '.zap', 'redis', 'nginx',
    'postgres', 'grafana', 'prometheus', 'pwa', 'monitoring', 'editor', 'frontend', 'backend', 'src', 'checks',
    'ai', 'ai_assistant', 'analytics', 'community_blog', 'desktop_app', 'integration', 'marketplace', 'mobile',
    'notifications', 'permissions', 'products', 'seo', 'social', 'stock', 'stock_management', 'virtual_company',
    'accounts', 'accounting', 'finance', 'hr_management', 'crm', 'education', 'games', 'testapp', 'testsite',
    'FinAsis', 'TestProje', 'backups', 'apps', 'users', 'inventory', 'hr_management', 'integrations',
}

# Örnek/Eski/Geçici klasörler (raporlanacaklar)
EXAMPLE_FOLDERS = {'TestProje', 'testapp', 'testsite', 'backups/old_structure'}

# Her modülde olması gereken temel dosyalar
REQUIRED_FILES = {'__init__.py', 'apps.py', 'README.md'}

# Raporlama için listeler
empty_dirs = []
missing_files = []
example_dirs = []

LANGUAGES = ['tr', 'ku', 'ar', 'en', 'de']

LOCALE_STRUCTURE = [
    '{lang}/LC_MESSAGES/django.po',
]

DOCS_STRUCTURE = [
    '{lang}/index.md',
]

def is_empty_dir(path: Path):
    return path.is_dir() and not any(path.iterdir())

def check_module(module_path: Path):
    missing = []
    for req in REQUIRED_FILES:
        if not (module_path / req).exists():
            missing.append(req)
    return missing

def create_file_if_missing(path: Path, content: str):
    if not path.exists():
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def get_app_name_from_folder(folder: Path):
    return folder.name.replace('_', ' ').title()

def create_missing_files(module_path: Path, missing_files: list):
    created = []
    app_name = module_path.name
    for fname in missing_files:
        fpath = module_path / fname
        if fname == '__init__.py':
            content = f"# {app_name} modülü için init dosyası\n"
        elif fname == 'README.md':
            content = f"# {get_app_name_from_folder(module_path)}\n\nBu modül, {get_app_name_from_folder(module_path)} ile ilgili işlevleri içerir.\n"
        elif fname == 'apps.py':
            class_name = f"{''.join([w.capitalize() for w in app_name.split('_')])}Config"
            content = f"""from django.apps import AppConfig\n\nclass {class_name}(AppConfig):\n    default_auto_field = 'django.db.models.BigAutoField'\n    name = '{app_name}'\n"""
        else:
            content = ''
        if create_file_if_missing(fpath, content):
            created.append(fname)
    return created

def create_locale_structure(base_path: Path):
    for lang in LANGUAGES:
        for rel_path in LOCALE_STRUCTURE:
            target = base_path / 'locale' / rel_path.format(lang=lang)
            target.parent.mkdir(parents=True, exist_ok=True)
            if not target.exists():
                with open(target, 'w', encoding='utf-8') as f:
                    f.write(f'# {lang} çeviri dosyası\nmsgid ""\nmsgstr ""\n')

def create_docs_structure(base_path: Path, module_name=None):
    for lang in LANGUAGES:
        for rel_path in DOCS_STRUCTURE:
            target = base_path / 'docs' / rel_path.format(lang=lang)
            target.parent.mkdir(parents=True, exist_ok=True)
            if not target.exists():
                with open(target, 'w', encoding='utf-8') as f:
                    title = module_name if module_name else 'Proje Dokümantasyonu'
                    f.write(f'# {title} ({lang})\n\nBu dokümantasyon {lang} dili içindir.\n')

def main():
    print(f"Proje kökü: {ROOT}\n")
    print("--- Klasörler gözden geçiriliyor ---\n")
    created_files_report = []
    created_locale_report = []
    created_docs_report = []
    # Kök için locale ve docs
    create_locale_structure(ROOT)
    create_docs_structure(ROOT)
    created_locale_report.append('Proje kökü')
    created_docs_report.append('Proje kökü')
    for item in ROOT.iterdir():
        if item.is_dir():
            # Örnek/Eski klasör kontrolü
            if item.name in EXAMPLE_FOLDERS or str(item) in EXAMPLE_FOLDERS:
                example_dirs.append(str(item))
            # Boş klasör kontrolü
            if is_empty_dir(item):
                empty_dirs.append(str(item))
            # Modül kontrolü (core/common dışında)
            elif item.name not in CORE_FOLDERS:
                missing = check_module(item)
                if missing:
                    missing_files.append((item.name, missing))
                    created = create_missing_files(item, missing)
                    if created:
                        created_files_report.append((item.name, created))
                # Her modül için locale ve docs
                create_locale_structure(item)
                create_docs_structure(item, module_name=item.name)
                created_locale_report.append(item.name)
                created_docs_report.append(item.name)

    # Alt klasörlerde eski/örnek klasör arama
    for ex in EXAMPLE_FOLDERS:
        ex_path = ROOT / ex
        if ex_path.exists():
            example_dirs.append(str(ex_path))

    # Rapor
    print("\n--- Temizlik Raporu ---\n")
    if empty_dirs:
        print("Boş klasörler:")
        for d in empty_dirs:
            print(f"  - {d}")
    else:
        print("Boş klasör yok.")

    if missing_files:
        print("\nModüllerde eksik temel dosyalar:")
        for mod, files in missing_files:
            print(f"  - {mod}: {', '.join(files)}")
    else:
        print("Tüm modüllerde temel dosyalar mevcut.")

    if created_files_report:
        print("\nOluşturulan dosyalar:")
        for mod, files in created_files_report:
            print(f"  - {mod}: {', '.join(files)}")

    if created_locale_report:
        print("\nOluşturulan locale klasörleri:")
        for mod in created_locale_report:
            print(f"  - {mod}")
    if created_docs_report:
        print("\nOluşturulan docs klasörleri:")
        for mod in created_docs_report:
            print(f"  - {mod}")

    if example_dirs:
        print("\nKullanılmayan/örnek klasörler:")
        for d in example_dirs:
            print(f"  - {d}")
    else:
        print("Kullanılmayan/örnek klasör yok.")

    # Raporu dosyaya da yaz
    with open(ROOT / 'temizlik_raporu.txt', 'w', encoding='utf-8') as f:
        f.write("--- Temizlik Raporu ---\n\n")
        if empty_dirs:
            f.write("Boş klasörler:\n")
            for d in empty_dirs:
                f.write(f"  - {d}\n")
        else:
            f.write("Boş klasör yok.\n")
        if missing_files:
            f.write("\nModüllerde eksik temel dosyalar:\n")
            for mod, files in missing_files:
                f.write(f"  - {mod}: {', '.join(files)}\n")
        else:
            f.write("Tüm modüllerde temel dosyalar mevcut.\n")
        if created_files_report:
            f.write("\nOluşturulan dosyalar:\n")
            for mod, files in created_files_report:
                f.write(f"  - {mod}: {', '.join(files)}\n")
        if created_locale_report:
            f.write("\nOluşturulan locale klasörleri:\n")
            for mod in created_locale_report:
                f.write(f"  - {mod}\n")
        if created_docs_report:
            f.write("\nOluşturulan docs klasörleri:\n")
            for mod in created_docs_report:
                f.write(f"  - {mod}\n")
        if example_dirs:
            f.write("\nKullanılmayan/örnek klasörler:\n")
            for d in example_dirs:
                f.write(f"  - {d}\n")
        else:
            f.write("Kullanılmayan/örnek klasör yok.\n")
    print("\nRapor 'temizlik_raporu.txt' dosyasına kaydedildi.")

if __name__ == "__main__":
    main() 