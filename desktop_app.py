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
import json
import requests
from packaging import version
import sqlite3
import shutil
from datetime import datetime

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
        self.current_version = "1.0.0"
        self.latest_version = None
        self.is_offline_mode = False
        self.last_sync_time = None
        self.local_db_path = os.path.join(os.path.expanduser("~"), ".finasis", "local.db")
        
        # Tema renkleri
        self.colors = {
            'primary': '#2c3e50',
            'secondary': '#34495e',
            'accent': '#3498db',
            'success': '#2ecc71',
            'warning': '#f1c40f',
            'danger': '#e74c3c',
            'light': '#ecf0f1',
            'dark': '#2c3e50',
            'background': '#f5f6fa'
        }
        
        # Loglama ayarları
        self.setup_logging()
        
        # Yerel veritabanı ayarları
        self.setup_local_database()
        
        # Window setup
        self.root.title("FinAsis - Finansal Yönetim Sistemi")
        self.root.geometry("1024x768")
        self.root.minsize(800, 600)
        
        # Tema ayarları
        self.style = ttk.Style()
        self.style.configure('TFrame', background=self.colors['background'])
        self.style.configure('TLabel', background=self.colors['background'], foreground=self.colors['dark'])
        self.style.configure('TButton', background=self.colors['primary'], foreground='white')
        self.style.configure('TProgressbar', background=self.colors['accent'])
        
        try:
            # Django ortamını ayarla
            if not setup_django_environment():
                error_msg = "Django yapılandırması yüklenemedi."
                logging.error(error_msg)
                self.show_error_and_exit(error_msg)
                return
            
            self.setup_ui()
            self.check_server()
            self.check_for_updates()
            
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

    def setup_logging(self):
        """Gelişmiş loglama ayarları"""
        log_dir = os.path.join(os.path.expanduser("~"), ".finasis", "logs")
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, f"finasis_{datetime.now().strftime('%Y%m%d')}.log")
        
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        # Hata yakalama
        sys.excepthook = self.handle_exception

    def handle_exception(self, exc_type, exc_value, exc_traceback):
        """Genel hata yakalama"""
        logging.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
        messagebox.showerror("Hata", f"Beklenmeyen bir hata oluştu: {str(exc_value)}")

    def setup_local_database(self):
        """Yerel veritabanı kurulumu"""
        try:
            os.makedirs(os.path.dirname(self.local_db_path), exist_ok=True)
            
            conn = sqlite3.connect(self.local_db_path)
            cursor = conn.cursor()
            
            # Veritabanı tablolarını oluştur
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sync_status (
                    id INTEGER PRIMARY KEY,
                    last_sync_time TEXT,
                    sync_status TEXT,
                    error_message TEXT
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS offline_data (
                    id INTEGER PRIMARY KEY,
                    table_name TEXT,
                    data TEXT,
                    sync_status TEXT,
                    created_at TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            
            logging.info("Yerel veritabanı başarıyla oluşturuldu")
        except Exception as e:
            logging.error(f"Yerel veritabanı oluşturma hatası: {str(e)}")
            messagebox.showerror("Hata", "Yerel veritabanı oluşturulamadı")

    def check_internet_connection(self):
        """İnternet bağlantısını kontrol et"""
        try:
            requests.get("https://www.google.com", timeout=5)
            return True
        except:
            return False

    def start_offline_mode(self):
        """Offline modu başlat"""
        if not self.is_offline_mode:
            self.is_offline_mode = True
            self.status_label.config(text="Offline mod aktif")
            logging.info("Offline mod başlatıldı")
            
            # Offline modda çalışacak işlemleri başlat
            threading.Thread(target=self.sync_local_data, daemon=True).start()

    def sync_local_data(self):
        """Yerel verileri senkronize et"""
        try:
            while self.is_offline_mode:
                if self.check_internet_connection():
                    # İnternet bağlantısı varsa senkronizasyon yap
                    self.sync_with_server()
                time.sleep(300)  # 5 dakikada bir kontrol et
        except Exception as e:
            logging.error(f"Senkronizasyon hatası: {str(e)}")

    def sync_with_server(self):
        """Sunucu ile senkronizasyon"""
        try:
            conn = sqlite3.connect(self.local_db_path)
            cursor = conn.cursor()
            
            # Senkronize edilmemiş verileri al
            cursor.execute("SELECT * FROM offline_data WHERE sync_status = 'pending'")
            pending_data = cursor.fetchall()
            
            for data in pending_data:
                try:
                    # Veriyi sunucuya gönder
                    response = requests.post(
                        f"{self.server_url}/api/sync",
                        json=json.loads(data[2])
                    )
                    
                    if response.status_code == 200:
                        # Başarılı senkronizasyon
                        cursor.execute(
                            "UPDATE offline_data SET sync_status = 'synced' WHERE id = ?",
                            (data[0],)
                        )
                    else:
                        # Başarısız senkronizasyon
                        cursor.execute(
                            "UPDATE offline_data SET sync_status = 'failed' WHERE id = ?",
                            (data[0],)
                        )
                except Exception as e:
                    logging.error(f"Veri senkronizasyon hatası: {str(e)}")
            
            conn.commit()
            conn.close()
            
            self.last_sync_time = datetime.now()
            logging.info("Senkronizasyon tamamlandı")
        except Exception as e:
            logging.error(f"Senkronizasyon hatası: {str(e)}")

    def setup_ui(self):
        # Ana frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Üst menü çubuğu
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)
        
        # Dosya menüsü
        file_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Dosya", menu=file_menu)
        file_menu.add_command(label="Ayarlar", command=self.show_settings)
        file_menu.add_separator()
        file_menu.add_command(label="Çıkış", command=self.on_closing)
        
        # Yardım menüsü
        help_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Yardım", menu=help_menu)
        help_menu.add_command(label="Kullanıcı Kılavuzu", command=self.show_user_guide)
        help_menu.add_command(label="Güncellemeleri Kontrol Et", command=self.check_for_updates)
        help_menu.add_separator()
        help_menu.add_command(label="Hakkında", command=self.show_about)
        
        # Logo ve başlık
        logo_frame = ttk.Frame(main_frame)
        logo_frame.pack(pady=20)
        
        title_label = ttk.Label(logo_frame, text="FinAsis", font=("Arial", 32, "bold"), foreground=self.colors['primary'])
        title_label.pack()
        
        subtitle_label = ttk.Label(logo_frame, text="Finansal Yönetim Sistemi", font=("Arial", 16), foreground=self.colors['secondary'])
        subtitle_label.pack()
        
        # Durum çerçevesi
        status_frame = ttk.LabelFrame(main_frame, text="Sunucu Durumu", padding="10")
        status_frame.pack(fill=tk.X, pady=20)
        
        self.status_label = ttk.Label(status_frame, text="Kontrol ediliyor...", font=("Arial", 12))
        self.status_label.pack(pady=10)
        
        self.progress = ttk.Progressbar(status_frame, orient=tk.HORIZONTAL, length=300, mode='indeterminate')
        self.progress.pack(pady=10)
        
        # Butonlar çerçevesi
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(pady=20)
        
        # Sunucu başlat butonu
        self.start_button = ttk.Button(buttons_frame, text="Sunucuyu Başlat", command=self.start_server, style='Accent.TButton')
        self.start_button.grid(row=0, column=0, padx=10, pady=10)
        
        # Sunucu durdur butonu
        self.stop_button = ttk.Button(buttons_frame, text="Sunucuyu Durdur", command=self.stop_server, state=tk.DISABLED, style='Danger.TButton')
        self.stop_button.grid(row=0, column=1, padx=10, pady=10)
        
        # Tarayıcıda aç butonu
        self.browser_button = ttk.Button(buttons_frame, text="Tarayıcıda Aç", command=self.open_browser, state=tk.DISABLED, style='Success.TButton')
        self.browser_button.grid(row=0, column=2, padx=10, pady=10)
        
        # Offline mod butonu
        self.offline_button = ttk.Button(
            buttons_frame,
            text="Offline Mod",
            command=self.toggle_offline_mode,
            style='Warning.TButton'
        )
        self.offline_button.grid(row=0, column=3, padx=10, pady=10)
        
        # Sistem bilgileri
        info_frame = ttk.LabelFrame(main_frame, text="Sistem Bilgileri", padding="10")
        info_frame.pack(fill=tk.X, pady=20)
        
        self.version_label = ttk.Label(info_frame, text=f"Versiyon: {self.current_version}")
        self.version_label.pack(anchor=tk.W)
        
        self.update_label = ttk.Label(info_frame, text="Güncelleme durumu kontrol ediliyor...")
        self.update_label.pack(anchor=tk.W)
        
        # Senkronizasyon durumu
        sync_frame = ttk.LabelFrame(main_frame, text="Senkronizasyon Durumu", padding="10")
        sync_frame.pack(fill=tk.X, pady=20)
        
        self.sync_label = ttk.Label(sync_frame, text="Senkronizasyon durumu kontrol ediliyor...")
        self.sync_label.pack(pady=10)
        
        # Alt bilgi
        footer_frame = ttk.Frame(main_frame)
        footer_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=20)
        
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

    def check_for_updates(self):
        """Güncellemeleri kontrol et"""
        try:
            self.update_label.config(text="Güncellemeler kontrol ediliyor...")
            response = requests.get("https://api.finasis.com/version")
            if response.status_code == 200:
                data = response.json()
                self.latest_version = data.get('version')
                if version.parse(self.latest_version) > version.parse(self.current_version):
                    self.update_label.config(text=f"Yeni güncelleme mevcut: {self.latest_version}")
                    if messagebox.askyesno("Güncelleme", "Yeni bir güncelleme mevcut. Şimdi güncellemek ister misiniz?"):
                        self.download_update()
                else:
                    self.update_label.config(text="Uygulama güncel")
            else:
                self.update_label.config(text="Güncelleme kontrolü başarısız")
        except Exception as e:
            logging.error(f"Güncelleme kontrolü hatası: {str(e)}")
            self.update_label.config(text="Güncelleme kontrolü başarısız")

    def download_update(self):
        """Güncellemeyi indir ve kur"""
        try:
            self.update_label.config(text="Güncelleme indiriliyor...")
            
            # Güncelleme dosyasını indir
            response = requests.get(f"https://api.finasis.com/download/{self.latest_version}")
            if response.status_code == 200:
                # Güncelleme dosyasını kaydet
                update_file = os.path.join(os.path.expanduser("~"), ".finasis", "update.exe")
                with open(update_file, "wb") as f:
                    f.write(response.content)
                
                # Güncelleme işlemini başlat
                if platform.system() == "Windows":
                    subprocess.Popen([update_file, "/SILENT"])
                else:
                    subprocess.Popen(["chmod", "+x", update_file])
                    subprocess.Popen([update_file])
                
                messagebox.showinfo("Güncelleme", "Güncelleme başarıyla tamamlandı. Uygulama yeniden başlatılacak.")
                sys.exit(0)
            else:
                raise Exception("Güncelleme dosyası indirilemedi")
        except Exception as e:
            logging.error(f"Güncelleme hatası: {str(e)}")
            messagebox.showerror("Hata", "Güncelleme sırasında bir hata oluştu.")

    def show_settings(self):
        """Ayarlar penceresini göster"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Ayarlar")
        settings_window.geometry("400x300")
        
        # Ayarlar içeriği burada oluşturulacak
        ttk.Label(settings_window, text="Ayarlar").pack(pady=20)

    def show_user_guide(self):
        """Kullanıcı kılavuzunu göster"""
        webbrowser.open("https://docs.finasis.com/user-guide")

    def show_about(self):
        """Hakkında penceresini göster"""
        about_window = tk.Toplevel(self.root)
        about_window.title("Hakkında")
        about_window.geometry("300x200")
        
        ttk.Label(about_window, text="FinAsis", font=("Arial", 16, "bold")).pack(pady=20)
        ttk.Label(about_window, text=f"Versiyon: {self.current_version}").pack()
        ttk.Label(about_window, text="© 2023-2025 FinAsis").pack(pady=20)

    def toggle_offline_mode(self):
        """Offline modu aç/kapat"""
        if not self.is_offline_mode:
            self.start_offline_mode()
            self.offline_button.config(text="Online Mod")
        else:
            self.is_offline_mode = False
            self.offline_button.config(text="Offline Mod")
            self.status_label.config(text="Online mod aktif")
            logging.info("Online moda geçildi")

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