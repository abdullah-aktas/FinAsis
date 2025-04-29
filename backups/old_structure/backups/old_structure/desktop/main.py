# -*- coding: utf-8 -*-
import os
import sys
import logging
import threading
import time
from pathlib import Path
import tkinter as tk
from tkinter import messagebox

# Servisleri import et
from services.UpdateService import UpdateService
from services.TrayService import TrayService
from services.DatabaseService import DatabaseService

# Loglama yapılandırması
def setup_logging():
    log_dir = Path.home() / ".finasis" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = log_dir / "finasis.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)

class FinasisApp:
    def __init__(self):
        self.logger = setup_logging()
        self.logger.info("FinAsis masaüstü uygulaması başlatılıyor...")
        
        # Uygulama bilgileri
        self.app_name = "FinAsis"
        self.version = "1.0.0"
        self.update_url = "https://api.finasis.com/updates"
        
        # Servisleri başlat
        self.init_services()
        
        # Ana pencere
        self.root = None
        
        # Güncelleme kontrolü için zamanlayıcı
        self.update_timer = None
    
    def init_services(self):
        """Servisleri başlatır"""
        try:
            # Veritabanı servisi
            self.db_service = DatabaseService()
            self.logger.info("Veritabanı servisi başlatıldı")
            
            # Güncelleme servisi
            self.update_service = UpdateService(
                current_version=self.version,
                update_url=self.update_url,
                app_name=self.app_name
            )
            self.logger.info("Güncelleme servisi başlatıldı")
            
            # Tray servisi
            icon_path = Path(os.path.dirname(os.path.abspath(__file__))) / "assets" / "icon.png"
            self.tray_service = TrayService(
                app_name=self.app_name,
                icon_path=icon_path
            )
            self.logger.info("Tray servisi başlatıldı")
            
            # Tray servisini başlat
            self.tray_service.start()
            
        except Exception as e:
            self.logger.error(f"Servis başlatma hatası: {str(e)}")
            messagebox.showerror("Hata", f"Uygulama başlatılamadı: {str(e)}")
            sys.exit(1)
    
    def create_main_window(self):
        """Ana pencereyi oluşturur"""
        self.root = tk.Tk()
        self.root.title(f"{self.app_name} v{self.version}")
        self.root.geometry("800x600")
        
        # Pencere kapatıldığında
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Pencereyi göster
        self.root.deiconify()
    
    def on_closing(self):
        """Pencere kapatıldığında"""
        # Pencereyi gizle, uygulamayı kapatma
        self.root.withdraw()
    
    def check_updates(self):
        """Güncellemeleri kontrol eder"""
        try:
            update_info = self.update_service.check_for_updates()
            
            if update_info.get("available", False):
                # Güncelleme mevcut, kullanıcıya bildir
                self.tray_service.show_notification(
                    "Güncelleme Mevcut",
                    f"FinAsis v{update_info['version']} sürümü mevcut. Güncellemek ister misiniz?"
                )
                
                # Güncelleme menüsünü güncelle
                # Bu kısım TrayService'e eklenebilir
                
            # Bir sonraki kontrol için zamanlayıcıyı ayarla (24 saat)
            self.update_timer = threading.Timer(86400, self.check_updates)
            self.update_timer.daemon = True
            self.update_timer.start()
            
        except Exception as e:
            self.logger.error(f"Güncelleme kontrolü hatası: {str(e)}")
    
    def run(self):
        """Uygulamayı çalıştırır"""
        try:
            # Ana pencereyi oluştur
            self.create_main_window()
            
            # İlk güncelleme kontrolünü başlat
            self.check_updates()
            
            # Ana döngüyü başlat
            self.root.mainloop()
            
        except Exception as e:
            self.logger.error(f"Uygulama çalıştırma hatası: {str(e)}")
            messagebox.showerror("Hata", f"Uygulama çalıştırılamadı: {str(e)}")
        finally:
            # Uygulama kapatılırken
            self.cleanup()
    
    def cleanup(self):
        """Uygulama kapatılırken temizlik yapar"""
        try:
            # Zamanlayıcıyı iptal et
            if self.update_timer:
                self.update_timer.cancel()
            
            # Tray servisini durdur
            if self.tray_service:
                self.tray_service.stop()
            
            # Veritabanı bağlantısını kapat
            if self.db_service:
                self.db_service.close()
            
            self.logger.info("Uygulama kapatıldı")
            
        except Exception as e:
            self.logger.error(f"Temizlik hatası: {str(e)}")

if __name__ == "__main__":
    app = FinasisApp()
    app.run() 