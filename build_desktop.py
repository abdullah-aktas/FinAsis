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
    
    # Create build directory if it doesn't exist
    build_dir = "build/desktop"
    if not os.path.exists(build_dir):
        os.makedirs(build_dir)
    
    # Copy static files
    static_dir = "static"
    if os.path.exists(static_dir):
        print("Statik dosyalar kopyalanıyor...")
        dest_static_dir = os.path.join(build_dir, "static")
        if os.path.exists(dest_static_dir):
            shutil.rmtree(dest_static_dir)
        shutil.copytree(static_dir, dest_static_dir)
    
    # Prepare PyInstaller command
    icon_path = "static/img/favicon.ico" if os.path.exists("static/img/favicon.ico") else None
    
    pyinstaller_cmd = [
        "pyinstaller",
        "--name=FinAsis",
        "--onefile",
        "--windowed",
        "--clean",
    ]
    
    if icon_path:
        pyinstaller_cmd.append(f"--icon={icon_path}")
    
    # Add paths to include
    pyinstaller_cmd.extend([
        "--add-data=static;static",
        "--add-data=templates;templates",
    ])
    
    # Add the main script
    pyinstaller_cmd.append("desktop_app.py")
    
    # Convert command for Windows if needed
    if platform.system() == "Windows":
        # Change the path separator for Windows
        pyinstaller_cmd = [cmd.replace(";", ";") for cmd in pyinstaller_cmd]
    
    # Execute PyInstaller
    print("PyInstaller çalıştırılıyor...")
    print(" ".join(pyinstaller_cmd))
    
    subprocess.call(pyinstaller_cmd)
    
    print("\nDerleme tamamlandı!")
    print("Çalıştırılabilir dosya: 'dist/FinAsis.exe'")

if __name__ == "__main__":
    build_desktop_app() 