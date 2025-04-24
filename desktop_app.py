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
from typing import Optional, Dict, Any, Union, Callable
import asyncio
import aiohttp
from cryptography.fernet import Fernet
import psutil
from dataclasses import dataclass
from enum import Enum, auto

# Loglama ayarları
logging.basicConfig(
    filename='finasis.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class AppState(Enum):
    INITIALIZING = auto()
    RUNNING = auto()
    STOPPED = auto()
    ERROR = auto()

@dataclass
class AppConfig:
    version: str
    server_url: str
    local_db_path: str
    backup_path: str
    log_path: str
    theme: Dict[str, str]
    encryption_key: Optional[bytes] = None

class FinasisError(Exception):
    """Özel hata sınıfı"""
    def __init__(self, message: str, code: int = 0):
        super().__init__(message)
        self.code = code
        self.timestamp = datetime.now()

# Platform bağımlı işlemler için yardımcı fonksiyonlar
def get_process_group_id(pid: int) -> Optional[int]:
    """Unix benzeri sistemlerde process group ID'sini döndürür"""
    try:
        if platform.system() != 'Windows':
            return os.getpgid(pid)  # type: ignore
    except (AttributeError, OSError):
        pass
    return None

def kill_process_group(pid: int, sig: int = signal.SIGTERM) -> bool:
    """Unix benzeri sistemlerde process grubunu sonlandırır"""
    try:
        if platform.system() != 'Windows':
            pgid = get_process_group_id(pid)
            if pgid is not None:
                os.killpg(pgid, sig)  # type: ignore
                return True
    except (AttributeError, OSError):
        pass
    return False

def get_preexec_fn() -> Optional[Callable]:
    """Unix benzeri sistemler için preexec_fn döndürür"""
    try:
        if platform.system() != 'Windows' and hasattr(os, 'setsid'):
            return os.setsid  # type: ignore
    except AttributeError:
        pass
    return None

class FinasisDesktopApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.state = AppState.INITIALIZING
        self.config = self._load_config()
        self.server_process: Optional[subprocess.Popen] = None
        self.is_server_running = False
        self.is_offline_mode = False
        self.last_sync_time: Optional[datetime] = None
        
        # Asenkron işlemler için event loop
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
        # Güvenlik
        self._setup_encryption()
        
        # Performans izleme
        self._setup_performance_monitoring()
        
        # UI setup
        self._setup_ui()
        
        # Başlangıç kontrolleri
        self._initialize_app()

    def _load_config(self) -> AppConfig:
        """Uygulama yapılandırmasını yükle"""
        try:
            config_path = os.path.join(os.path.expanduser("~"), ".finasis", "config.json")
            if os.path.exists(config_path):
                with open(config_path, "r") as f:
                    config_data = json.load(f)
            else:
                config_data = {
                    "version": "1.0.0",
                    "server_url": "http://127.0.0.1:8000",
                    "local_db_path": os.path.join(os.path.expanduser("~"), ".finasis", "local.db"),
                    "backup_path": os.path.join(os.path.expanduser("~"), ".finasis", "backups"),
                    "log_path": os.path.join(os.path.expanduser("~"), ".finasis", "logs"),
                    "theme": {
                        "primary": "#2c3e50",
                        "secondary": "#34495e",
                        "accent": "#3498db",
                        "success": "#2ecc71",
                        "warning": "#f1c40f",
                        "danger": "#e74c3c",
                        "light": "#ecf0f1",
                        "dark": "#2c3e50",
                        "background": "#f5f6fa"
                    }
                }
                os.makedirs(os.path.dirname(config_path), exist_ok=True)
                with open(config_path, "w") as f:
                    json.dump(config_data, f, indent=4)
            
            return AppConfig(**config_data)
        except Exception as e:
            raise FinasisError(f"Yapılandırma yüklenemedi: {str(e)}", 1001)

    def _setup_encryption(self):
        """Şifreleme anahtarını ayarla"""
        try:
            key_path = os.path.join(os.path.expanduser("~"), ".finasis", ".key")
            if os.path.exists(key_path):
                with open(key_path, "rb") as f:
                    self.config.encryption_key = f.read()
            else:
                key = Fernet.generate_key()
                self.config.encryption_key = key
                os.makedirs(os.path.dirname(key_path), exist_ok=True)
                with open(key_path, "wb") as f:
                    f.write(key)  # type: ignore
        except Exception as e:
            raise FinasisError(f"Şifreleme ayarlanamadı: {str(e)}", 1002)

    def _setup_performance_monitoring(self):
        """Performans izleme sistemini ayarla"""
        try:
            self.performance_monitor = threading.Thread(
                target=self._monitor_performance,
                daemon=True
            )
            self.performance_monitor.start()
        except Exception as e:
            raise FinasisError(f"Performans izleme başlatılamadı: {str(e)}", 1003)

    def _monitor_performance(self):
        """Sistem performansını izle"""
        while True:
            try:
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                
                if cpu_percent > 80:
                    logging.warning(f"Yüksek CPU kullanımı: {cpu_percent}%")
                if memory.percent > 80:
                    logging.warning(f"Yüksek bellek kullanımı: {memory.percent}%")
                if disk.percent > 80:
                    logging.warning(f"Yüksek disk kullanımı: {disk.percent}%")
                
                time.sleep(60)  # Her dakika kontrol et
            except Exception as e:
                logging.error(f"Performans izleme hatası: {str(e)}")
                time.sleep(300)  # Hata durumunda 5 dakika bekle

    def _setup_ui(self):
        """Kullanıcı arayüzünü ayarla"""
        try:
            # Ana pencere ayarları
            self.root.title("FinAsis - Finansal Yönetim Sistemi")
            self.root.geometry("1024x768")
            self.root.minsize(800, 600)
            
            # Tema ayarları
            self.style = ttk.Style()
            self._configure_theme()
            
            # Ana frame
            self.main_frame = ttk.Frame(self.root, padding="20")
            self.main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Menü çubuğu
            self._setup_menu()
            
            # Durum çubuğu
            self._setup_status_bar()
            
            # Ana içerik
            self._setup_main_content()
            
        except Exception as e:
            raise FinasisError(f"UI ayarlanamadı: {str(e)}", 1004)

    def _configure_theme(self):
        """Tema ayarlarını yapılandır"""
        try:
            self.style.configure('TFrame', background=self.config.theme['background'])
            self.style.configure('TLabel', 
                               background=self.config.theme['background'],
                               foreground=self.config.theme['dark'])
            self.style.configure('TButton',
                               background=self.config.theme['primary'],
                               foreground='white')
            self.style.configure('TProgressbar',
                               background=self.config.theme['accent'])
            
            # Özel stiller
            self.style.configure('Accent.TButton',
                               background=self.config.theme['accent'])
            self.style.configure('Success.TButton',
                               background=self.config.theme['success'])
            self.style.configure('Warning.TButton',
                               background=self.config.theme['warning'])
            self.style.configure('Danger.TButton',
                               background=self.config.theme['danger'])
        except Exception as e:
            raise FinasisError(f"Tema ayarlanamadı: {str(e)}", 1005)

    def _setup_menu(self):
        """Menü çubuğunu ayarla"""
        try:
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
        except Exception as e:
            raise FinasisError(f"Menü ayarlanamadı: {str(e)}", 1006)

    def _setup_status_bar(self):
        """Durum çubuğunu ayarla"""
        try:
            self.status_frame = ttk.Frame(self.main_frame)
            self.status_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=5)
            
            self.status_label = ttk.Label(self.status_frame, text="Hazır")
            self.status_label.pack(side=tk.LEFT)
            
            self.progress = ttk.Progressbar(self.status_frame, mode='indeterminate')
            self.progress.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        except Exception as e:
            raise FinasisError(f"Durum çubuğu ayarlanamadı: {str(e)}", 1007)

    def _setup_main_content(self):
        """Ana içeriği ayarla"""
        try:
            # Logo ve başlık
            logo_frame = ttk.Frame(self.main_frame)
            logo_frame.pack(pady=20)
            
            title_label = ttk.Label(logo_frame,
                                  text="FinAsis",
                                  font=("Arial", 32, "bold"),
                                  foreground=self.config.theme['primary'])
            title_label.pack()
            
            subtitle_label = ttk.Label(logo_frame,
                                     text="Finansal Yönetim Sistemi",
                                     font=("Arial", 16),
                                     foreground=self.config.theme['secondary'])
            subtitle_label.pack()
            
            # Butonlar
            buttons_frame = ttk.Frame(self.main_frame)
            buttons_frame.pack(pady=20)
            
            self.start_button = ttk.Button(buttons_frame,
                                         text="Sunucuyu Başlat",
                                         command=self.start_server,
                                         style='Accent.TButton')
            self.start_button.grid(row=0, column=0, padx=10, pady=10)
            
            self.stop_button = ttk.Button(buttons_frame,
                                        text="Sunucuyu Durdur",
                                        command=self.stop_server,
                                        state=tk.DISABLED,
                                        style='Danger.TButton')
            self.stop_button.grid(row=0, column=1, padx=10, pady=10)
            
            self.browser_button = ttk.Button(buttons_frame,
                                           text="Tarayıcıda Aç",
                                           command=self.open_browser,
                                           state=tk.DISABLED,
                                           style='Success.TButton')
            self.browser_button.grid(row=0, column=2, padx=10, pady=10)
            
            self.offline_button = ttk.Button(buttons_frame,
                                           text="Offline Mod",
                                           command=self.toggle_offline_mode,
                                           style='Warning.TButton')
            self.offline_button.grid(row=0, column=3, padx=10, pady=10)
            
            # Sistem bilgileri
            info_frame = ttk.LabelFrame(self.main_frame, text="Sistem Bilgileri", padding="10")
            info_frame.pack(fill=tk.X, pady=20)
            
            self.version_label = ttk.Label(info_frame, text=f"Versiyon: {self.config.version}")
            self.version_label.pack(anchor=tk.W)
            
            self.update_label = ttk.Label(info_frame, text="Güncelleme durumu kontrol ediliyor...")
            self.update_label.pack(anchor=tk.W)
        except Exception as e:
            raise FinasisError(f"Ana içerik ayarlanamadı: {str(e)}", 1008)

    def _initialize_app(self):
        """Uygulamayı başlat"""
        try:
            self.state = AppState.INITIALIZING
            self.status_label.config(text="Başlatılıyor...")
            
            # Gerekli dizinleri oluştur
            os.makedirs(self.config.backup_path, exist_ok=True)
            os.makedirs(self.config.log_path, exist_ok=True)
            
            # Yerel veritabanını ayarla
            self._setup_local_database()
            
            # Django ortamını ayarla
            if not self._setup_django_environment():
                raise FinasisError("Django yapılandırması yüklenemedi", 1009)
            
            # Sunucu durumunu kontrol et
            self.check_server()
            
            # Güncellemeleri kontrol et
            self.check_for_updates()
            
            self.state = AppState.RUNNING
            self.status_label.config(text="Hazır")
            
        except Exception as e:
            self.state = AppState.ERROR
            self._handle_error(e)

    def _handle_error(self, error: Exception):
        """Hata yönetimi"""
        try:
            if isinstance(error, FinasisError):
                error_code = error.code
                error_message = str(error)
            else:
                error_code = 9999
                error_message = f"Beklenmeyen hata: {str(error)}"
            
            logging.error(f"Hata Kodu: {error_code} - {error_message}")
            logging.error(traceback.format_exc())
            
            self.status_label.config(text=f"Hata: {error_message}")
            messagebox.showerror("Hata", f"{error_message}\nDetaylar için log dosyasını kontrol edin.")
            
        except Exception as e:
            logging.critical(f"Kritik hata yönetimi hatası: {str(e)}")
            sys.exit(1)

    def get_resource_path(self, relative_path: str) -> str:
        """Get the path to a resource, works for dev and for PyInstaller"""
        try:
            if getattr(sys, 'frozen', False):
                base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
                logging.debug(f"Running in PyInstaller bundle. Base path: {base_path}")
                full_path = os.path.join(base_path, relative_path)
                if os.path.exists(full_path):
                    return full_path
            return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)
        except Exception as e:
            logging.error(f"get_resource_path hatası: {str(e)}")
            raise FinasisError(f"Kaynak yolu alınamadı: {str(e)}", 1010)

    def _setup_local_database(self):
        """Yerel veritabanı kurulumu"""
        try:
            os.makedirs(os.path.dirname(self.config.local_db_path), exist_ok=True)
            
            conn = sqlite3.connect(self.config.local_db_path)
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
            raise FinasisError(f"Yerel veritabanı oluşturulamadı: {str(e)}", 1003)

    def _setup_django_environment(self) -> bool:
        """Django ortamını ayarla"""
        try:
            base_path = self.get_resource_path(".")
            logging.debug(f"Django setup - Base path: {base_path}")
            
            # Python yolunu ayarla
            if base_path not in sys.path:
                sys.path.insert(0, base_path)
            
            # Config dizinini kontrol et
            config_path = os.path.join(base_path, "config")
            if not os.path.exists(config_path):
                logging.error(f"Config dizini bulunamadı: {config_path}")
                return False
            
            # Settings dizinini kontrol et
            settings_path = os.path.join(config_path, "settings")
            if not os.path.exists(settings_path):
                logging.error(f"Settings dizini bulunamadı: {settings_path}")
                return False
            
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
            
            # Django'yu başlat
            import django
            django.setup()
            
            return True
        except Exception as e:
            logging.error(f"Django setup hatası: {str(e)}")
            return False

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
            conn = sqlite3.connect(self.config.local_db_path)
            cursor = conn.cursor()
            
            # Senkronize edilmemiş verileri al
            cursor.execute("SELECT * FROM offline_data WHERE sync_status = 'pending'")
            pending_data = cursor.fetchall()
            
            for data in pending_data:
                try:
                    # Veriyi sunucuya gönder
                    response = requests.post(
                        f"{self.config.server_url}/api/sync",
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
                manage_py_path = self.get_resource_path("manage.py")
                base_path = self.get_resource_path(".")
                
                # Dosya yollarını logla
                logging.debug(f"Python path: {python_path}")
                logging.debug(f"manage.py path: {manage_py_path}")
                logging.debug(f"Base path: {base_path}")
                
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
                db_path = self.get_resource_path("db.sqlite3")
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
                    # Unix-like sistemler için
                    self.server_process = subprocess.Popen(
                        server_cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        universal_newlines=True,
                        env=env,
                        cwd=base_path,
                        preexec_fn=get_preexec_fn()
                    )
                
                # Sunucunun başlamasını bekle
                for i in range(30):
                    time.sleep(1)
                    try:
                        if self.server_process.poll() is not None:
                            stdout, stderr = self.server_process.communicate()
                            error_msg = f"Sunucu başlatma hatası:\nSTDOUT:\n{stdout}\nSTDERR:\n{stderr}"
                            logging.error(error_msg)
                            raise Exception(error_msg)
                        
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
                    # On Unix-like systems, try to kill process group
                    if not kill_process_group(self.server_process.pid):
                        # Fallback to terminate if process group kill fails
                        self.server_process.terminate()
                
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
        
        webbrowser.open(self.config.server_url)
        
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
                if version.parse(self.latest_version) > version.parse(self.config.version):
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
        ttk.Label(about_window, text=f"Versiyon: {self.config.version}").pack()
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