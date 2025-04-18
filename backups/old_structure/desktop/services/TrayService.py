import os
import sys
import logging
from pathlib import Path
import pystray
from PIL import Image
import threading
import webbrowser

class TrayService:
    def __init__(self, app_name="FinAsis", icon_path=None):
        self.app_name = app_name
        self.logger = logging.getLogger(__name__)
        self.icon = None
        self.tray_icon = None
        self.is_running = False
        
        # Varsayılan icon yolunu belirle
        if icon_path is None:
            # Uygulama dizinindeki assets klasöründen icon'u al
            base_dir = Path(os.path.dirname(os.path.abspath(__file__))).parent
            icon_path = base_dir / "assets" / "icon.png"
        
        # Icon dosyasını yükle
        try:
            self.icon = Image.open(icon_path)
        except Exception as e:
            self.logger.error(f"Icon yüklenirken hata: {str(e)}")
            # Varsayılan bir icon oluştur
            self.icon = Image.new('RGB', (64, 64), color='blue')
    
    def create_menu(self):
        """Sistem tray menüsünü oluşturur"""
        return pystray.Menu(
            pystray.MenuItem(
                "FinAsis'i Aç",
                self.open_app
            ),
            pystray.MenuItem(
                "Web Sitesi",
                self.open_website
            ),
            pystray.MenuItem(
                "Ayarlar",
                self.open_settings
            ),
            pystray.MenuItem(
                "Güncellemeleri Kontrol Et",
                self.check_updates
            ),
            pystray.MenuItem(
                "Çıkış",
                self.quit_app
            )
        )
    
    def open_app(self, icon, item):
        """Ana uygulamayı açar"""
        self.logger.info("Ana uygulama açılıyor...")
        # Ana uygulamayı açmak için gerekli kodu buraya ekle
        # Örneğin: subprocess.Popen(["python", "main.py"])
    
    def open_website(self, icon, item):
        """Web sitesini açar"""
        self.logger.info("Web sitesi açılıyor...")
        webbrowser.open("https://finasis.com")
    
    def open_settings(self, icon, item):
        """Ayarlar penceresini açar"""
        self.logger.info("Ayarlar açılıyor...")
        # Ayarlar penceresini açmak için gerekli kodu buraya ekle
    
    def check_updates(self, icon, item):
        """Güncellemeleri kontrol eder"""
        self.logger.info("Güncellemeler kontrol ediliyor...")
        # Güncelleme kontrolü için gerekli kodu buraya ekle
    
    def quit_app(self, icon, item):
        """Uygulamadan çıkar"""
        self.logger.info("Uygulama kapatılıyor...")
        self.stop()
        # Uygulamayı tamamen kapatmak için gerekli kodu buraya ekle
        # Örneğin: sys.exit(0)
    
    def start(self):
        """Sistem tray servisini başlatır"""
        if self.is_running:
            return
        
        self.is_running = True
        
        # Tray icon'u oluştur
        self.tray_icon = pystray.Icon(
            self.app_name,
            self.icon,
            self.app_name,
            self.create_menu()
        )
        
        # Tray icon'u ayrı bir thread'de çalıştır
        threading.Thread(target=self.tray_icon.run, daemon=True).start()
        self.logger.info("Sistem tray servisi başlatıldı")
    
    def stop(self):
        """Sistem tray servisini durdurur"""
        if not self.is_running:
            return
        
        self.is_running = False
        if self.tray_icon:
            self.tray_icon.stop()
            self.tray_icon = None
        
        self.logger.info("Sistem tray servisi durduruldu")
    
    def update_icon(self, icon_path):
        """Tray icon'unu günceller"""
        try:
            new_icon = Image.open(icon_path)
            if self.tray_icon:
                self.tray_icon.icon = new_icon
                self.icon = new_icon
                self.logger.info("Tray icon'u güncellendi")
        except Exception as e:
            self.logger.error(f"Tray icon'u güncellenirken hata: {str(e)}")
    
    def show_notification(self, title, message):
        """Bildirim gösterir"""
        if self.tray_icon:
            self.tray_icon.notify(message, title)
            self.logger.info(f"Bildirim gösterildi: {title}") 