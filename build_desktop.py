import os
import sys
import subprocess
import shutil
import platform

def build_desktop_app():
    """
    Build the desktop application using PyInstaller
    """
    print("FinAsis Masaüstü Uygulaması Derleyicisi")
    print("="*50)
    
    # Ensure PyInstaller is installed
    try:
        import PyInstaller
        print("PyInstaller sürümü:", PyInstaller.__version__)
    except ImportError:
        print("PyInstaller yüklü değil. Yükleniyor...")
        subprocess.call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Clean previous build
    print("Önceki derleme temizleniyor...")
    build_paths = ["build", "dist", "FinAsis.spec"]
    for path in build_paths:
        try:
            if os.path.isfile(path):
                os.remove(path)
            elif os.path.isdir(path):
                shutil.rmtree(path)
        except Exception as e:
            print(f"Uyarı: {path} temizlenemedi: {e}")
    
    # Create build directory if it doesn't exist
    build_dir = "build/desktop"
    if not os.path.exists(build_dir):
        os.makedirs(build_dir)
    
    # Copy project files
    print("Proje dosyaları kopyalanıyor...")
    project_files = [
        "manage.py",
        "config",
        "core",
        "users",
        "api",
        "static",
        "templates",
        "db.sqlite3"  # If exists
    ]
    
    for item in project_files:
        if os.path.exists(item):
            dest = os.path.join(build_dir, item)
            print(f"{item} kopyalanıyor...")
            if os.path.isfile(item):
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                shutil.copy2(item, dest)
            else:
                if os.path.exists(dest):
                    shutil.rmtree(dest)
                shutil.copytree(item, dest)
    
    # Prepare PyInstaller command
    icon_path = "static/img/favicon.ico" if os.path.exists("static/img/favicon.ico") else None
    
    pyinstaller_cmd = [
        "pyinstaller",
        "--name=FinAsis",
        "--onefile",
        "--windowed",
        "--clean",
        "--log-level=DEBUG",
        "--noconfirm",
    ]
    
    if icon_path:
        pyinstaller_cmd.append(f"--icon={icon_path}")
    
    # Add data files
    separator = ";" if platform.system() == "Windows" else ":"
    for item in project_files:
        if os.path.exists(item):
            if os.path.isfile(item):
                pyinstaller_cmd.append(f"--add-data={item}{separator}.")
            else:
                pyinstaller_cmd.append(f"--add-data={item}{separator}{item}")
    
    # Add hidden imports
    hidden_imports = [
        "django",
        "django.core",
        "django.contrib",
        "django.conf",
        "django.template",
        "django.template.loader",
        "django.template.context_processors",
        "django.template.loaders",
        "django.template.loaders.filesystem",
        "django.template.loaders.app_directories",
        "django.middleware",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.staticfiles",
    ]
    
    for imp in hidden_imports:
        pyinstaller_cmd.append(f"--hidden-import={imp}")
    
    # Add the main script
    pyinstaller_cmd.append("desktop_app.py")
    
    # Execute PyInstaller
    print("PyInstaller çalıştırılıyor...")
    print(" ".join(pyinstaller_cmd))
    
    result = subprocess.run(pyinstaller_cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print("Hata oluştu:")
        print(result.stderr)
        sys.exit(1)
    
    print("\nDerleme tamamlandı!")
    print("Çalıştırılabilir dosya: 'dist/FinAsis.exe'")

if __name__ == "__main__":
    build_desktop_app() 