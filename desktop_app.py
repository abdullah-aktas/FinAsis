import os
import sys
import webbrowser
import threading
import subprocess
import time
import ctypes
import platform
from http.client import HTTPConnection
import socket
import signal
import tkinter as tk
from tkinter import ttk, messagebox
import logging
import traceback
from pathlib import Path

# Loglama ayarları
logging.basicConfig(
    filename='finasis.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def get_resource_path(relative_path):
    """Get the path to a resource, works for dev and for PyInstaller"""
    try:
        if getattr(sys, 'frozen', False):
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
            logging.debug(f"Running in PyInstaller bundle. Base path: {base_path}")
            logging.debug(f"Looking for resource: {relative_path}")
            full_path = os.path.join(base_path, relative_path)
            logging.debug(f"Full resource path: {full_path}")
            logging.debug(f"Resource exists: {os.path.exists(full_path)}")
            if os.path.exists(full_path):
                if os.path.isdir(full_path):
                    logging.debug(f"Directory contents: {os.listdir(full_path)}")
            return full_path
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)
    except Exception as e:
        logging.error(f"get_resource_path hatası: {str(e)}\n{traceback.format_exc()}")
        raise

def setup_django_environment():
    """Setup Django environment for the application"""
    try:
        base_path = get_resource_path(".")
        logging.debug(f"Django setup - Base path: {base_path}")
        
        # Python yolunu ayarla
        if base_path not in sys.path:
            sys.path.insert(0, base_path)
        logging.debug(f"sys.path: {sys.path}")
        
        # Config dizinini kontrol et
        config_path = os.path.join(base_path, "config")
        if not os.path.exists(config_path):
            logging.error(f"Config dizini bulunamadı: {config_path}")
            return False
        logging.debug(f"Config dizini içeriği: {os.listdir(config_path)}")
        
        # Settings dizinini kontrol et
        settings_path = os.path.join(config_path, "settings")
        if not os.path.exists(settings_path):
            logging.error(f"Settings dizini bulunamadı: {settings_path}")
            return False
        logging.debug(f"Settings dizini içeriği: {os.listdir(settings_path)}")
        
        # Gerekli dizinleri oluştur
        media_path = os.path.join(base_path, "media")
        logs_path = os.path.join(base_path, "logs")
        os.makedirs(media_path, exist_ok=True)
        os.makedirs(logs_path, exist_ok=True)
        
        # Django ayarları için ortam değişkenlerini ayarla
        os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings.dev"
        os.environ["DJANGO_SECRET_KEY"] = "django-insecure-development-key"
        os.environ["DJANGO_DEBUG"] = "True"
        os.environ["DJANGO_ALLOWED_HOSTS"] = "localhost,127.0.0.1"
        
        logging.debug(f"DJANGO_SETTINGS_MODULE: {os.environ.get('DJANGO_SETTINGS_MODULE')}")
        
        # Django'yu başlat
        import django
        logging.debug(f"Django sürümü: {django.get_version()}")
        
        # BASE_DIR'i ayarla
        from django.conf import settings
        import config.settings.base as base_settings
        base_settings.BASE_DIR = Path(base_path)
        
        django.setup()
        logging.debug("Django setup tamamlandı")
        
        # Ayarları kontrol et
        logging.debug("Django setup başarılı")
        logging.debug(f"BASE_DIR: {settings.BASE_DIR}")
        logging.debug(f"INSTALLED_APPS: {settings.INSTALLED_APPS}")
        logging.debug(f"DATABASES: {settings.DATABASES}")
        
        return True
    except Exception as e:
        logging.error(f"Django setup hatası: {str(e)}\n{traceback.format_exc()}")
        return False

class FinasisDesktopApp:
    def __init__(self, root):
        self.root = root
        self.server_process = None
        self.server_url = "http://127.0.0.1:8000"
        self.is_server_running = False
        
        # Window setup
        self.root.title("FinAsis - Finansal Yönetim Sistemi")
        self.root.geometry("800x600")
        self.root.minsize(800, 600)
        
        try:
            # Django ortamını ayarla
            if not setup_django_environment():
                error_msg = "Django yapılandırması yüklenemedi."
                logging.error(error_msg)
                self.show_error_and_exit(error_msg)
                return
            
            self.setup_ui()
            self.check_server()
            
            # Pencere kapatma olayını bağla
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            
        except Exception as e:
            error_msg = f"Uygulama başlatma hatası: {str(e)}"
            logging.error(f"{error_msg}\n{traceback.format_exc()}")
            self.show_error_and_exit(error_msg)
    
    def show_error_and_exit(self, message):
        """Show error message and exit application"""
        try:
            messagebox.showerror("Hata", f"{message}\nDetaylar için finasis.log dosyasını kontrol edin.")
        except:
            logging.error("Hata mesajı gösterilemedi")
        finally:
            try:
                self.root.quit()
            except:
                sys.exit(1)

    def setup_ui(self):
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Logo and title
        logo_frame = ttk.Frame(main_frame)
        logo_frame.pack(pady=20)
        
        title_label = ttk.Label(logo_frame, text="FinAsis", font=("Arial", 24, "bold"))
        title_label.pack()
        
        subtitle_label = ttk.Label(logo_frame, text="Finansal Yönetim Sistemi", font=("Arial", 14))
        subtitle_label.pack()
        
        # Status frame
        status_frame = ttk.LabelFrame(main_frame, text="Sunucu Durumu", padding="10")
        status_frame.pack(fill=tk.X, pady=20)
        
        self.status_label = ttk.Label(status_frame, text="Kontrol ediliyor...", font=("Arial", 12))
        self.status_label.pack(pady=10)
        
        self.progress = ttk.Progressbar(status_frame, orient=tk.HORIZONTAL, length=300, mode='indeterminate')
        self.progress.pack(pady=10)
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(pady=20)
        
        # Start server button
        self.start_button = ttk.Button(buttons_frame, text="Sunucuyu Başlat", command=self.start_server)
        self.start_button.grid(row=0, column=0, padx=10, pady=10)
        
        # Stop server button
        self.stop_button = ttk.Button(buttons_frame, text="Sunucuyu Durdur", command=self.stop_server, state=tk.DISABLED)
        self.stop_button.grid(row=0, column=1, padx=10, pady=10)
        
        # Open browser button
        self.browser_button = ttk.Button(buttons_frame, text="Tarayıcıda Aç", command=self.open_browser, state=tk.DISABLED)
        self.browser_button.grid(row=0, column=2, padx=10, pady=10)
        
        # Footer
        footer_frame = ttk.Frame(main_frame)
        footer_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=20)
        
        version_label = ttk.Label(footer_frame, text="Versiyon 1.0.0")
        version_label.pack(side=tk.LEFT)
        
        copyright_label = ttk.Label(footer_frame, text="© 2023-2025 FinAsis")
        copyright_label.pack(side=tk.RIGHT)
        
    def check_server(self):
        """Check if Django server is already running"""
        self.progress.start()
        self.status_label.config(text="Sunucu durumu kontrol ediliyor...")
        
        # Run in a separate thread to avoid blocking the UI
        threading.Thread(target=self._check_server_thread, daemon=True).start()
    
    def _check_server_thread(self):
        """Thread function to check server status"""
        try:
            conn = HTTPConnection("127.0.0.1", 8000, timeout=1)
            conn.request("HEAD", "/")
            response = conn.getresponse()
            
            if response.status < 400:
                self.is_server_running = True
                self.update_ui_server_running()
            else:
                self.is_server_running = False
                self.update_ui_server_stopped()
                
        except (socket.error, socket.timeout) as e:
            self.is_server_running = False
            self.update_ui_server_stopped()
        finally:
            self.progress.stop()
    
    def update_ui_server_running(self):
        """Update UI when server is running"""
        self.root.after(0, lambda: self.status_label.config(text="Sunucu çalışıyor"))
        self.root.after(0, lambda: self.start_button.config(state=tk.DISABLED))
        self.root.after(0, lambda: self.stop_button.config(state=tk.NORMAL))
        self.root.after(0, lambda: self.browser_button.config(state=tk.NORMAL))
        self.root.after(0, lambda: self.progress.stop())
    
    def update_ui_server_stopped(self):
        """Update UI when server is stopped"""
        self.root.after(0, lambda: self.status_label.config(text="Sunucu çalışmıyor"))
        self.root.after(0, lambda: self.start_button.config(state=tk.NORMAL))
        self.root.after(0, lambda: self.stop_button.config(state=tk.DISABLED))
        self.root.after(0, lambda: self.browser_button.config(state=tk.DISABLED))
        self.root.after(0, lambda: self.progress.stop())
    
    def start_server(self):
        """Start the Django development server"""
        if self.is_server_running:
            messagebox.showinfo("Sunucu Durumu", "Sunucu zaten çalışıyor.")
            return
        
        self.progress.start()
        self.status_label.config(text="Sunucu başlatılıyor...")
        
        def run_server():
            try:
                # Python yolunu kontrol et
                python_path = sys.executable
                manage_py_path = get_resource_path("manage.py")
                base_path = get_resource_path(".")
                
                # Dosya yollarını logla
                logging.debug(f"Python path: {python_path}")
                logging.debug(f"manage.py path: {manage_py_path}")
                logging.debug(f"Base path: {base_path}")
                logging.debug(f"Current working directory: {os.getcwd()}")
                logging.debug(f"Directory contents: {os.listdir(base_path)}")
                
                if not os.path.exists(manage_py_path):
                    error_msg = f"manage.py bulunamadı: {manage_py_path}"
                    logging.error(error_msg)
                    messagebox.showerror("Hata", error_msg)
                    return
                
                # Ortam değişkenlerini ayarla
                env = os.environ.copy()
                env["PYTHONPATH"] = base_path
                env["DJANGO_SETTINGS_MODULE"] = "config.settings.dev"
                
                # Veritabanı ayarlarını kontrol et
                db_path = get_resource_path("db.sqlite3")
                if not os.path.exists(db_path):
                    logging.info("Veritabanı bulunamadı, migrate işlemi başlatılıyor...")
                    try:
                        migrate_result = subprocess.run(
                            [python_path, manage_py_path, "migrate"],
                            env=env,
                            check=True,
                            capture_output=True,
                            text=True,
                            cwd=base_path
                        )
                        logging.debug(f"Migrate çıktısı: {migrate_result.stdout}")
                    except subprocess.CalledProcessError as e:
                        error_msg = f"Migrate işlemi başarısız: {e.stderr}"
                        logging.error(error_msg)
                        messagebox.showerror("Hata", error_msg)
                        return
                
                # Sunucuyu başlat
                server_cmd = [python_path, manage_py_path, "runserver", "--noreload"]
                logging.debug(f"Sunucu komutu: {' '.join(server_cmd)}")
                
                if platform.system() == "Windows":
                    self.server_process = subprocess.Popen(
                        server_cmd,
                        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        universal_newlines=True,
                        env=env,
                        cwd=base_path
                    )
                else:
                    self.server_process = subprocess.Popen(
                        server_cmd,
                        preexec_fn=os.setsid,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        universal_newlines=True,
                        env=env,
                        cwd=base_path
                    )
                
                # Sunucunun başlamasını bekle
                for i in range(30):
                    time.sleep(1)
                    try:
                        # Sunucu çıktısını kontrol et
                        if self.server_process.poll() is not None:
                            stdout, stderr = self.server_process.communicate()
                            error_msg = f"Sunucu başlatma hatası:\nSTDOUT:\n{stdout}\nSTDERR:\n{stderr}"
                            logging.error(error_msg)
                            raise Exception(error_msg)
                        
                        # Sunucuya bağlanmayı dene
                        conn = HTTPConnection("127.0.0.1", 8000, timeout=1)
                        conn.request("HEAD", "/")
                        response = conn.getresponse()
                        
                        if response.status < 400:
                            self.is_server_running = True
                            self.update_ui_server_running()
                            logging.info("Sunucu başarıyla başlatıldı")
                            return
                    except (socket.error, socket.timeout):
                        continue
                    except Exception as e:
                        logging.error(f"Bağlantı hatası: {str(e)}")
                        continue
                
                # 30 saniye sonra hala başlamadıysa
                stdout, stderr = self.server_process.communicate()
                error_msg = f"Sunucu 30 saniye içinde başlatılamadı\nSTDOUT:\n{stdout}\nSTDERR:\n{stderr}"
                logging.error(error_msg)
                messagebox.showerror("Hata", error_msg)
                self.stop_server()
                
            except Exception as e:
                error_msg = f"Sunucu başlatılırken hata oluştu: {str(e)}\n{traceback.format_exc()}"
                logging.error(error_msg)
                messagebox.showerror("Hata", f"Sunucu başlatılamadı: {str(e)}")
                self.is_server_running = False
                self.update_ui_server_stopped()
        
        # Sunucuyu ayrı bir thread'de başlat
        threading.Thread(target=run_server, daemon=True).start()
    
    def stop_server(self):
        """Stop the Django development server"""
        if not self.is_server_running:
            messagebox.showinfo("Sunucu Durumu", "Sunucu zaten çalışmıyor.")
            return
        
        self.progress.start()
        self.status_label.config(text="Sunucu durduruluyor...")
        
        try:
            if self.server_process:
                # Send signal to terminate the process
                if platform.system() == "Windows":
                    # On Windows, use CTRL+C signal
                    self.server_process.send_signal(signal.CTRL_C_EVENT)
                else:
                    # On Unix-like systems, use SIGTERM
                    os.killpg(os.getpgid(self.server_process.pid), signal.SIGTERM)
                
                # Wait for process to terminate
                self.server_process.wait(timeout=5)
                self.server_process = None
            
            # Additional check to verify server is stopped
            try:
                conn = HTTPConnection("127.0.0.1", 8000, timeout=1)
                conn.request("HEAD", "/")
                response = conn.getresponse()
                
                # If we can still connect, the server is still running
                self.is_server_running = True
                messagebox.showerror("Hata", "Sunucu durdurulamadı.")
            except (socket.error, socket.timeout):
                self.is_server_running = False
                self.update_ui_server_stopped()
                
        except Exception as e:
            messagebox.showerror("Hata", f"Sunucu durdurulurken hata oluştu: {str(e)}")
        
        self.progress.stop()
    
    def open_browser(self):
        """Open web browser to access the application"""
        if not self.is_server_running:
            messagebox.showinfo("Sunucu Durumu", "Önce sunucuyu başlatmalısınız.")
            return
        
        webbrowser.open(self.server_url)
        
    def on_closing(self):
        """Handle window closing event"""
        if self.is_server_running and messagebox.askyesno("Çıkış", "Sunucu çalışıyor. Çıkmadan önce sunucuyu durdurmak ister misiniz?"):
            self.stop_server()
        
        self.root.destroy()

def set_app_id():
    """Set application ID for Windows taskbar"""
    if platform.system() == "Windows":
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("com.finasis.desktop")

if __name__ == "__main__":
    set_app_id()
    root = tk.Tk()
    
    # Set application icon (replace with actual icon path if available)
    if platform.system() == "Windows":
        try:
            root.iconbitmap("static/img/favicon.ico")
        except:
            pass
    
    app = FinasisDesktopApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop() 