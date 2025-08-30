# -*- coding: utf-8 -*-
"""
FinAsis 3D Ticaret Simülasyonu

Bu modül, Ursina Engine kullanılarak geliştirilmiş finansal eğitim simülasyonunu içerir.
Kullanıcılar 3D ortamda borsa ve yatırım kavramlarını interaktif bir şekilde öğrenebilirler.

Özellikler:
- 3D borsa ortamında gezinme
- Gerçek zamanlı hisse senedi alım satımı
- Finansal danışman ile etkileşim
- Dinamik piyasa simülasyonu
- Portföy yönetim arayüzü
- Çoklu platform desteği (Web, Masaüstü, Mobil)
- Online/Offline mod desteği
"""

from .game import run_game
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import random
import time
import json
import os
import platform
import threading
import queue
import asyncio
from typing import Dict, List, Optional, Union

class FinansalSimulasyonOyunu:
    def __init__(self, online_mode: bool = False):
        self.online_mode = online_mode
        self.oyuncu_bakiyesi = 10000
        self.oyuncu_puani = 0
        self.oyuncu_seviyesi = 1
        self.oyuncu_deneyimi = 0
        self.oyuncu_rozetleri = []
        self.oyuncu_etkilesimleri = []
        self.oyuncu_istatistikleri = {
            'toplam_islem': 0,
            'basarili_islem': 0,
            'basarisiz_islem': 0,
            'kazanilan_para': 0,
            'kaybedilen_para': 0
        }
        
        # Platform kontrolü
        self.platform = self._detect_platform()
        
        # Performans optimizasyonu için
        self.update_queue = queue.Queue()
        self.is_running = True
        self.update_thread = threading.Thread(target=self._update_loop)
        self.update_thread.daemon = True
        self.update_thread.start()
        
        # Veri senkronizasyonu için
        self.sync_lock = threading.Lock()
        self.last_sync = time.time()
        
    def _detect_platform(self) -> str:
        """Platform tespiti yapar"""
        system = platform.system().lower()
        if system == 'windows':
            return 'windows'
        elif system == 'darwin':
            return 'macos'
        elif system == 'linux':
            return 'linux'
        elif 'android' in system:
            return 'android'
        elif 'ios' in system:
            return 'ios'
        else:
            return 'web'
            
    def _update_loop(self):
        """Arka planda çalışan güncelleme döngüsü"""
        while self.is_running:
            try:
                if not self.update_queue.empty():
                    update_data = self.update_queue.get_nowait()
                    self._process_update(update_data)
                time.sleep(0.016)  # ~60 FPS
            except Exception as e:
                print(f"Güncelleme hatası: {str(e)}")
                
    def _process_update(self, update_data: Dict):
        """Güncelleme verilerini işler"""
        with self.sync_lock:
            if 'bakiye' in update_data:
                self.oyuncu_bakiyesi = update_data['bakiye']
            if 'puan' in update_data:
                self.oyuncu_puani = update_data['puan']
            if 'seviye' in update_data:
                self.oyuncu_seviyesi = update_data['seviye']
                
    def islem_yap(self, islem_turu: str, miktar: float, risk_seviyesi: float) -> bool:
        """İşlem yapar ve sonucu döndürür"""
        try:
            with self.sync_lock:
                # İşlem mantığı ve sonuç hesaplama
                basari = random.random() < (0.7 - risk_seviyesi * 0.2)
                
                if basari:
                    self.oyuncu_bakiyesi += miktar
                    self.oyuncu_puani += miktar * 0.1
                    self.oyuncu_istatistikleri['basarili_islem'] += 1
                    self.oyuncu_istatistikleri['kazanilan_para'] += miktar
                else:
                    self.oyuncu_bakiyesi -= miktar
                    self.oyuncu_istatistikleri['basarisiz_islem'] += 1
                    self.oyuncu_istatistikleri['kaybedilen_para'] += miktar
                
                self.oyuncu_istatistikleri['toplam_islem'] += 1
                
                # Online modda sunucuya senkronizasyon
                if self.online_mode:
                    self._sync_with_server()
                    
                return basari
                
        except Exception as e:
            print(f"İşlem hatası: {str(e)}")
            return False
            
    def _sync_with_server(self):
        """Sunucu ile senkronizasyon yapar"""
        if time.time() - self.last_sync > 5:  # 5 saniyede bir senkronizasyon
            try:
                # Senkronizasyon verilerini hazırla
                sync_data = {
                    'bakiye': self.oyuncu_bakiyesi,
                    'puan': self.oyuncu_puani,
                    'seviye': self.oyuncu_seviyesi,
                    'istatistikler': self.oyuncu_istatistikleri
                }
                
                # Burada gerçek bir sunucu senkronizasyonu yapılacak
                # Şimdilik sadece simülasyon
                self.last_sync = time.time()
                
            except Exception as e:
                print(f"Senkronizasyon hatası: {str(e)}")
                
    def save_game(self, file_path: str = 'save_game.json') -> bool:
        """Oyun durumunu kaydeder"""
        try:
            with self.sync_lock:
                save_data = {
                    'oyuncu_bakiyesi': self.oyuncu_bakiyesi,
                    'oyuncu_puani': self.oyuncu_puani,
                    'oyuncu_seviyesi': self.oyuncu_seviyesi,
                    'oyuncu_deneyimi': self.oyuncu_deneyimi,
                    'oyuncu_rozetleri': self.oyuncu_rozetleri,
                    'oyuncu_etkilesimleri': self.oyuncu_etkilesimleri,
                    'oyuncu_istatistikleri': self.oyuncu_istatistikleri,
                    'platform': self.platform,
                    'online_mode': self.online_mode,
                    'last_sync': self.last_sync
                }
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(save_data, f, ensure_ascii=False, indent=4)
                    
                return True
                
        except Exception as e:
            print(f"Kayıt hatası: {str(e)}")
            return False
            
    def load_game(self, file_path: str = 'save_game.json') -> bool:
        """Kaydedilmiş oyun durumunu yükler"""
        try:
            if not os.path.exists(file_path):
                return False
                
            with open(file_path, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
                
            with self.sync_lock:
                self.oyuncu_bakiyesi = save_data['oyuncu_bakiyesi']
                self.oyuncu_puani = save_data['oyuncu_puani']
                self.oyuncu_seviyesi = save_data['oyuncu_seviyesi']
                self.oyuncu_deneyimi = save_data['oyuncu_deneyimi']
                self.oyuncu_rozetleri = save_data['oyuncu_rozetleri']
                self.oyuncu_etkilesimleri = save_data['oyuncu_etkilesimleri']
                self.oyuncu_istatistikleri = save_data['oyuncu_istatistikleri']
                self.platform = save_data['platform']
                self.online_mode = save_data['online_mode']
                self.last_sync = save_data['last_sync']
                
            return True
            
        except Exception as e:
            print(f"Yükleme hatası: {str(e)}")
            return False
            
    def __del__(self):
        """Nesne yok edildiğinde kaynakları temizle"""
        self.is_running = False
        if hasattr(self, 'update_thread'):
            self.update_thread.join(timeout=1.0)

__all__ = ['run_game', 'FinansalSimulasyonOyunu']