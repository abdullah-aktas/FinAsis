from __future__ import absolute_import, unicode_literals
import os
import random
from datetime import datetime, timedelta
import json
from ursina import Entity, Vec3, color, window, Ursina, Text, Button, Func, camera, destroy, application, WindowPanel, DirectionalLight, held_keys, mouse
from ursina.prefabs.first_person_controller import FirstPersonController
from . import FinansalSimulasyonOyunu
from .ar_module import ARManager
from .locales.locale_manager import LocaleManager
import time
import platform
from typing import Dict, List, Optional
import threading
from game_integration import GameIntegration

# Django ayarlarını yükle
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
# django.setup() satırı kaldırıldı - circular import sorununa yol açıyor

# Oyun içindeki şirket modelleri yerine sınıflar kullan
class GameCompany:
    def __init__(self, name, sector):
        self.name = name
        self.sector = sector

class GameDepartment:
    def __init__(self, name, company):
        self.name = name
        self.company = company

class GameEmployee:
    def __init__(self, name, department):
        self.name = name
        self.department = department

# Oyun ayarları
game_settings = {
    'difficulty': 'normal',  # easy, normal, hard
    'market_update_interval': 5,  # saniye
    'event_chance': 0.2,  # 0-1 arası
    'starting_money': 100000,
    'tutorial_enabled': True,
    'sound_enabled': True,
    'music_enabled': True,
    'fullscreen': False,
    'show_tooltips': True,
    'auto_save': True,
    'save_interval': 300  # saniye
}

# Piyasa durumu
market_state = {
    'trend': 'stable',  # bull, stable, bear
    'volatility': 0.5,  # 0-1 arası
    'last_update': datetime.now(),
    'market_events': []
}

# UI bileşenleri
ui = {
    'main_panel': None,
    'portfolio_panel': None,
    'market_panel': None,
    'stats_panel': None,
    'quest_panel': None,
    'notification_panel': None,
    'tooltip_panel': None,
    'menu_panel': None,
    'text_elements': {},
    'buttons': {},
    'charts': {},
    'notifications': []
}

# Oyuncu verileri
player = {
    'id': 1,
    'name': 'John Doe',
    'money': game_settings['starting_money'],
    'portfolio': {
        'AAPL': {'shares': 10, 'price': 150, 'sector': 'tech'},
        'GOOGL': {'shares': 5, 'price': 2000, 'sector': 'tech'},
        'TSLA': {'shares': 8, 'price': 700, 'sector': 'auto'},
        'MSFT': {'shares': 0, 'price': 300, 'sector': 'tech'},
        'AMZN': {'shares': 0, 'price': 3000, 'sector': 'retail'},
        'META': {'shares': 0, 'price': 250, 'sector': 'tech'},
        'NFLX': {'shares': 0, 'price': 400, 'sector': 'media'},
        'NVDA': {'shares': 0, 'price': 500, 'sector': 'tech'},
        'JPM': {'shares': 0, 'price': 150, 'sector': 'finance'},
        'BAC': {'shares': 0, 'price': 40, 'sector': 'finance'}
    },
    'stats': {
        'total_trades': 0,
        'successful_trades': 0,
        'failed_trades': 0,
        'profit_trades': 0,
        'loss_trades': 0,
        'total_profit': 0,
        'total_loss': 0,
        'best_trade': 0,
        'worst_trade': 0,
        'longest_holding': 0,
        'shortest_holding': 0,
        'risk_tolerance': 0.7,
        'trading_style': 'balanced',  # aggressive, balanced, conservative
        'debt_to_income': 0.0,  # Borç/gelir oranı
        'portfolio_diversity': 0.0,  # Portföy çeşitliliği
        'total_debt': 0,  # Toplam borç
        'total_income': 0,  # Toplam gelir
        'monthly_income': 0,  # Aylık gelir
        'monthly_expenses': 0  # Aylık giderler
    },
    'skills': {
        'analysis': 1,  # 1-10 arası
        'risk_management': 1,
        'market_knowledge': 1,
        'technical_analysis': 1,
        'fundamental_analysis': 1
    },
    'experience': {
        'level': 1,
        'current_xp': 0,
        'next_level_xp': 1000,
        'total_xp': 0
    },
    'achievements': [],
    'active_quests': [],
    'completed_quests': [],
    'quest_progress': {},
    'tutorial_progress': {
        'basic_trading': False,
        'market_analysis': False,
        'risk_management': False,
        'portfolio_management': False,
        'technical_analysis': False
    },
    'settings': {
        'notifications': True,
        'sound': True,
        'music': True,
        'tooltips': True,
        'auto_save': True
    },
    'trading_history': []
}

# Görev sistemi
quest_system = {
    'daily_quests': [],
    'weekly_quests': [],
    'achievement_quests': [],
    'tutorial_quests': []
}

# Görev tanımlamaları
quest_definitions = {
    # Günlük görevler
    'daily_trade': {
        'id': 'daily_trade',
        'title': 'Günlük İşlem',
        'description': 'Bugün en az 1 hisse senedi alım veya satım işlemi yapın.',
        'reward': {'money': 500, 'experience': 100},
        'type': 'daily',
        'check_completion': lambda: len([t for t in player['trading_history'] if (datetime.now() - t['timestamp']).days < 1]) > 0
    },
    'daily_profit': {
        'id': 'daily_profit',
        'title': 'Günlük Kâr',
        'description': 'Bugün portföyünüzden 1000$ kâr elde edin.',
        'reward': {'money': 1000, 'experience': 200},
        'type': 'daily',
        'check_completion': lambda: calculate_daily_profit() >= 1000
    },
    'daily_diversity': {
        'id': 'daily_diversity',
        'title': 'Çeşitlilik Ustası',
        'description': 'Portföy çeşitliliğinizi 0.7\'nin üzerine çıkarın.',
        'reward': {'money': 800, 'experience': 150},
        'type': 'daily',
        'check_completion': lambda: player['stats']['portfolio_diversity'] > 0.7
    },
    
    # Haftalık görevler
    'weekly_growth': {
        'id': 'weekly_growth',
        'title': 'Haftalık Büyüme',
        'description': 'Portföyünüzü bu hafta %10 büyütün.',
        'reward': {'money': 5000, 'experience': 500},
        'type': 'weekly',
        'check_completion': lambda: calculate_weekly_growth() >= 0.1
    },
    'weekly_trades': {
        'id': 'weekly_trades',
        'title': 'Aktif Trader',
        'description': 'Bu hafta en az 10 işlem yapın.',
        'reward': {'money': 3000, 'experience': 400},
        'type': 'weekly',
        'check_completion': lambda: len([t for t in player['trading_history'] if (datetime.now() - t['timestamp']).days < 7]) >= 10
    },
    'weekly_risk': {
        'id': 'weekly_risk',
        'title': 'Risk Yöneticisi',
        'description': 'Risk skorunuzu 0.5\'in altına düşürün.',
        'reward': {'money': 4000, 'experience': 450},
        'type': 'weekly',
        'check_completion': lambda: calculate_risk_score() < 0.5
    },
    
    # Başarı görevleri
    'achievement_portfolio': {
        'id': 'achievement_portfolio',
        'title': 'Portföy Ustası',
        'description': 'Portföyünüzü 200.000$ değerine ulaştırın.',
        'reward': {'money': 10000, 'experience': 1000, 'achievement': 'portfolio_master'},
        'type': 'achievement',
        'check_completion': lambda: calculate_portfolio_value() >= 200000
    },
    'achievement_diversity': {
        'id': 'achievement_diversity',
        'title': 'Çeşitlilik Kralı',
        'description': 'Portföy çeşitliliğinizi 0.9\'un üzerine çıkarın.',
        'reward': {'money': 8000, 'experience': 800, 'achievement': 'diversity_king'},
        'type': 'achievement',
        'check_completion': lambda: player['stats']['portfolio_diversity'] > 0.9
    },
    'achievement_debt': {
        'id': 'achievement_debt',
        'title': 'Borçsuz Yaşam',
        'description': 'Borç/gelir oranınızı 0.1\'in altına düşürün.',
        'reward': {'money': 6000, 'experience': 600, 'achievement': 'debt_free'},
        'type': 'achievement',
        'check_completion': lambda: player['stats']['debt_to_income'] < 0.1
    },
    
    # Eğitim görevleri
    'tutorial_buy': {
        'id': 'tutorial_buy',
        'title': 'İlk Alım',
        'description': 'İlk hisse senedi alım işleminizi yapın.',
        'reward': {'money': 1000, 'experience': 200},
        'type': 'tutorial',
        'check_completion': lambda: len([t for t in player['trading_history'] if t['type'] == 'buy']) > 0
    },
    'tutorial_sell': {
        'id': 'tutorial_sell',
        'title': 'İlk Satım',
        'description': 'İlk hisse senedi satım işleminizi yapın.',
        'reward': {'money': 1000, 'experience': 200},
        'type': 'tutorial',
        'check_completion': lambda: len([t for t in player['trading_history'] if t['type'] == 'sell']) > 0
    },
    'tutorial_diversity': {
        'id': 'tutorial_diversity',
        'title': 'Çeşitlendirme',
        'description': 'En az 3 farklı hisse senedine yatırım yapın.',
        'reward': {'money': 2000, 'experience': 300},
        'type': 'tutorial',
        'check_completion': lambda: len([s for s in player['portfolio'].values() if s['shares'] > 0]) >= 3
    }
}

# Görev UI elementleri
quest_ui = {
    'panel': None,
    'quest_items': [],
    'active_quests_text': None,
    'completed_quests_text': None
}

class FinansalDunya(Entity):
    def __init__(self, online_mode: bool = False):
        super().__init__()
        self.oyun = FinansalSimulasyonOyunu(online_mode=online_mode)
        self.oyuncu = FirstPersonController()
        self.oyuncu.position = (0, 2, 0)
        
        # Dil yöneticisi
        self.locale_manager = LocaleManager()
        
        # Platform kontrolü
        self.platform = self.oyun.platform
        self.is_mobile = self.platform in ['android', 'ios']
        
        # AR yöneticisini başlat (mobil platformlarda)
        if self.is_mobile:
            self.ar_manager = ARManager(use_aruco=True, show_camera=True)
            self.ar_manager.start()
            
        # Dünya oluşturma
        self.dunya = Entity(
            model='plane',
            texture='white_cube',
            scale=(100, 1, 100),
            color=color.gray
        )
        
        # Binalar ve iş yerleri
        self.binalar = []
        self.is_yerleri = []
        self.olaylar = []
        
        # UI elementleri
        self.ui_elements = {}
        
        # Performans optimizasyonu
        self.last_update = time.time()
        self.update_interval = 0.016  # ~60 FPS
        
        # Oyun durumu
        self.is_paused = False
        self.is_saving = False
        
        # Tuş durumları
        self.held_keys = {'w': False, 'a': False, 's': False, 'd': False, 'left mouse': False, 'right mouse': False}
        
        # İnitialize
        self.bina_olustur()
        self.is_yeri_olustur()
        self.olay_olustur()
        self.ui_olustur()
        
        # Otomatik kayıt
        self.auto_save_thread = threading.Thread(target=self._auto_save_loop)
        self.auto_save_thread.daemon = True
        self.auto_save_thread.start()

    def ui_olustur(self):
        # Ana panel
        self.ui_elements['ana_panel'] = Entity(
            parent=camera.ui,
            model='quad',
            scale=(0.8, 0.6),
            position=(0, 0),
            color=color.rgba(0, 0, 0, 0.7)
        )
        
        # Bakiye göstergesi
        self.ui_elements['bakiye'] = Text(
            parent=self.ui_elements['ana_panel'],
            text=f"{self.locale_manager.get_text('game.stats.balance')}: ${self.oyun.oyuncu_bakiyesi:,.2f}",
            position=(-0.4, 0.4),
            scale=2,
            color=color.green
        )
        
        # Puan göstergesi
        self.ui_elements['puan'] = Text(
            parent=self.ui_elements['ana_panel'],
            text=f"{self.locale_manager.get_text('game.stats.score')}: {self.oyun.oyuncu_puani}",
            position=(0.4, 0.4),
            scale=2,
            color=color.yellow
        )
        
        # Seviye göstergesi
        self.ui_elements['seviye'] = Text(
            parent=self.ui_elements['ana_panel'],
            text=f"{self.locale_manager.get_text('game.stats.level')}: {self.oyun.oyuncu_seviyesi}",
            position=(0, 0.4),
            scale=2,
            color=color.azure
        )
        
        # İşlem butonları
        self.ui_elements['alis_buton'] = Button(
            parent=self.ui_elements['ana_panel'],
            text=self.locale_manager.get_text('game.transactions.buy'),
            color=color.green,
            position=(-0.2, 0),
            scale=(0.2, 0.1),
            on_click=self.alis_yap
        )
        
        self.ui_elements['satis_buton'] = Button(
            parent=self.ui_elements['ana_panel'],
            text=self.locale_manager.get_text('game.transactions.sell'),
            color=color.red,
            position=(0.2, 0),
            scale=(0.2, 0.1),
            on_click=self.satis_yap
        )
        
        # Bildirim paneli
        self.ui_elements['bildirim'] = Text(
            parent=self.ui_elements['ana_panel'],
            text='',
            position=(0, -0.4),
            scale=1.5,
            color=color.white
        )
        
        # Menü butonu
        self.ui_elements['menu_buton'] = Button(
            parent=camera.ui,
            text=self.locale_manager.get_text('game.menu.settings'),
            color=color.azure,
            position=(0.8, 0.45),
            scale=(0.2, 0.05),
            on_click=self.toggle_menu
        )
        
        # Dil seçimi butonu
        self.ui_elements['dil_buton'] = Button(
            parent=camera.ui,
            text=f"Dil: {self.locale_manager.get_current_locale().upper()}",
            color=color.azure,
            position=(0.8, 0.35),
            scale=(0.2, 0.05),
            on_click=self.toggle_language
        )
        
        # Mobil kontroller
        if self.is_mobile:
            self._create_mobile_controls()
            
    def toggle_language(self):
        """Dil seçimini değiştir"""
        available_locales = self.locale_manager.get_available_locales()
        current_index = available_locales.index(self.locale_manager.get_current_locale())
        next_index = (current_index + 1) % len(available_locales)
        self.locale_manager.set_locale(available_locales[next_index])
        
        # UI'ı güncelle
        self.ui_guncelle()
        
    def alis_yap(self):
        if self.oyun.oyuncu_bakiyesi >= 1000:
            basari = self.oyun.islem_yap('alis', 1000, 0.5)
            if basari:
                self.ui_elements['bildirim'].text = self.locale_manager.get_text('game.transactions.success')
                self.ui_elements['bildirim'].color = color.green
            else:
                self.ui_elements['bildirim'].text = self.locale_manager.get_text('game.transactions.fail')
                self.ui_elements['bildirim'].color = color.red
        else:
            self.ui_elements['bildirim'].text = self.locale_manager.get_text('game.transactions.insufficient_balance')
            self.ui_elements['bildirim'].color = color.red
            
        self.ui_guncelle()
        
    def satis_yap(self):
        basari = self.oyun.islem_yap('satis', 1000, 0.3)
        if basari:
            self.ui_elements['bildirim'].text = self.locale_manager.get_text('game.transactions.success')
            self.ui_elements['bildirim'].color = color.green
        else:
            self.ui_elements['bildirim'].text = self.locale_manager.get_text('game.transactions.fail')
            self.ui_elements['bildirim'].color = color.red
            
        self.ui_guncelle()
        
    def ui_guncelle(self):
        self.ui_elements['bakiye'].text = f"{self.locale_manager.get_text('game.stats.balance')}: ${self.oyun.oyuncu_bakiyesi:,.2f}"
        self.ui_elements['puan'].text = f"{self.locale_manager.get_text('game.stats.score')}: {self.oyun.oyuncu_puani}"
        self.ui_elements['seviye'].text = f"{self.locale_manager.get_text('game.stats.level')}: {self.oyun.oyuncu_seviyesi}"
        self.ui_elements['alis_buton'].text = self.locale_manager.get_text('game.transactions.buy')
        self.ui_elements['satis_buton'].text = self.locale_manager.get_text('game.transactions.sell')
        self.ui_elements['menu_buton'].text = self.locale_manager.get_text('game.menu.settings')
        self.ui_elements['dil_buton'].text = f"Dil: {self.locale_manager.get_current_locale().upper()}"
        
    def toggle_menu(self):
        """Menüyü aç/kapat"""
        self.is_paused = not self.is_paused
        
        if self.is_paused:
            # Menü panelini göster
            self.ui_elements['menu_panel'] = Entity(
                parent=camera.ui,
                model='quad',
                scale=(0.4, 0.6),
                position=(0, 0),
                color=color.rgba(0, 0, 0, 0.9)
            )
            
            # Menü butonları
            Button(
                parent=self.ui_elements['menu_panel'],
                text=self.locale_manager.get_text('game.menu.continue'),
                color=color.green,
                position=(0, 0.2),
                scale=(0.3, 0.05),
                on_click=self.toggle_menu
            )
            
            Button(
                parent=self.ui_elements['menu_panel'],
                text='Kaydet',
                color=color.azure,
                position=(0, 0.1),
                scale=(0.3, 0.05),
                on_click=self.oyun.save_game
            )
            
            Button(
                parent=self.ui_elements['menu_panel'],
                text='Yükle',
                color=color.azure,
                position=(0, 0),
                scale=(0.3, 0.05),
                on_click=self.oyun.load_game
            )
            
            Button(
                parent=self.ui_elements['menu_panel'],
                text='Çıkış',
                color=color.red,
                position=(0, -0.2),
                scale=(0.3, 0.05),
                on_click=application.quit
            )
        else:
            # Menü panelini kaldır
            if 'menu_panel' in self.ui_elements:
                destroy(self.ui_elements['menu_panel'])
                del self.ui_elements['menu_panel']
        
    def update(self):
        # Performans kontrolü
        current_time = time.time()
        if current_time - self.last_update < self.update_interval:
            return
        self.last_update = current_time
        
        if self.is_paused:
            return
            
        # Oyun güncellemeleri
        if self.held_keys['left mouse']:
            self.alis_yap()
            
        if self.held_keys['right mouse']:
            self.satis_yap()
            
        # AR güncellemeleri
        if self.is_mobile:
            self.ar_manager.ar_nesne_guncelle()
            
        # Olay güncellemeleri
        self.olay_guncelle()
        
    def olay_guncelle(self):
        simdiki_zaman = time.time()
        for olay in self.olaylar:
            if simdiki_zaman - olay['baslangic'] > olay['sure']:
                # Olay süresi doldu, yeni olay oluştur
                olay['tip'] = random.choice([
                    'Borsa Yükselişi', 'Borsa Düşüşü',
                    'Enflasyon Artışı', 'Enflasyon Düşüşü',
                    'Faiz Artışı', 'Faiz Düşüşü',
                    'Döviz Dalgalanması', 'Altın Fiyatı Değişimi'
                ])
                olay['etki'] = random.uniform(-0.2, 0.2)
                olay['baslangic'] = simdiki_zaman
                
                # Olay bildirimi
                self.ui_elements['bildirim'].text = f"Yeni Olay: {olay['tip']}"
                self.ui_elements['bildirim'].color = color.yellow

def run_game(online_mode: bool = False):
    """Oyunu başlat"""
    app = Ursina()
    dunya = FinansalDunya(online_mode=online_mode)
    app.run()

def create_ui():
    """Ana UI'ı oluştur"""
    # Ana panel
    ui['main_panel'] = Entity(
        parent=camera.ui,
        model='quad',
        scale=(1.8, 1),
        position=(0, 0),
        color=color.rgba(0, 0, 0, 0.8)
    )
    
    # Üst bilgi paneli
    create_top_info_panel()
    
    # Portföy paneli
    create_portfolio_panel()
    
    # Market paneli
    create_market_panel()
    
    # İstatistik paneli
    create_stats_panel()
    
    # Menü butonu
    Button(
        parent=camera.ui,
        text='Menü',
        color=color.azure,
        position=(0.8, 0.45),
        scale=(0.2, 0.05),
        on_click=Func(toggle_menu)
    )

def create_top_info_panel():
    """Üst bilgi panelini oluştur"""
    # Para
    ui['text_elements']['money'] = Text(
        parent=camera.ui,
        text=f"${player['money']:,.2f}",
        position=(-0.8, 0.45),
        scale=2,
        color=color.green
    )
    
    # Portföy değeri
    ui['text_elements']['portfolio_value'] = Text(
        parent=camera.ui,
        text=f"Portföy: ${calculate_portfolio_value():,.2f}",
        position=(-0.4, 0.45),
        scale=2,
        color=color.white
    )
    
    # Risk skoru
    ui['text_elements']['risk_score'] = Text(
        parent=camera.ui,
        text=f"Risk: {calculate_risk_score():.2f}",
        position=(0, 0.45),
        scale=2,
        color=color.yellow
    )

def create_portfolio_panel():
    """Portföy panelini oluştur"""
    ui['portfolio_panel'] = Entity(
        parent=ui['main_panel'],
        model='quad',
        scale=(0.5, 0.8),
        position=(-0.6, -0.05),
        color=color.rgba(0, 0, 0, 0.5)
    )
    
    # Başlık
    Text(
        parent=ui['portfolio_panel'],
        text='Portföy',
        position=(0, 0.35),
        scale=2,
        color=color.white
    )
    
    # Hisse senetleri listesi
    y_pos = 0.25
    for symbol, data in player['portfolio'].items():
        if data['shares'] > 0:
            # Hisse adı ve miktar
            Text(
                parent=ui['portfolio_panel'],
                text=f"{symbol}: {data['shares']} adet",
                position=(-0.2, y_pos),
                scale=1.2,
                color=color.white
            )
            
            # Fiyat
            Text(
                parent=ui['portfolio_panel'],
                text=f"${data['price']:,.2f}",
                position=(0.15, y_pos),
                scale=1.2,
                color=color.green if data['price'] > 0 else color.red
            )
            
            y_pos -= 0.08

def create_market_panel():
    """Market panelini oluştur"""
    ui['market_panel'] = Entity(
        parent=ui['main_panel'],
        model='quad',
        scale=(0.5, 0.8),
        position=(0, -0.05),
        color=color.rgba(0, 0, 0, 0.5)
    )
    
    # Başlık
    Text(
        parent=ui['market_panel'],
        text='Market',
        position=(0, 0.35),
        scale=2,
        color=color.white
    )
    
    # Market trendi
    ui['text_elements']['market_trend'] = Text(
        parent=ui['market_panel'],
        text=f"Trend: {market_state['trend'].upper()}",
        position=(0, 0.25),
        scale=1.5,
        color=color.yellow
    )
    
    # Volatilite
    ui['text_elements']['volatility'] = Text(
        parent=ui['market_panel'],
        text=f"Volatilite: {market_state['volatility']:.2f}",
        position=(0, 0.2),
        scale=1.2,
        color=color.azure
    )
    
    # Hisse senetleri listesi
    y_pos = 0.1
    for symbol, data in player['portfolio'].items():
        # Hisse adı ve fiyat
        Text(
            parent=ui['market_panel'],
            text=f"{symbol}: ${data['price']:,.2f}",
            position=(-0.2, y_pos),
            scale=1.2,
            color=color.white
        )
        
        # Alım butonu
        Button(
            parent=ui['market_panel'],
            text='Al',
            color=color.green,
            position=(0.1, y_pos),
            scale=(0.1, 0.04),
            on_click=Func(lambda s=symbol: buy_stock(s))
        )
        
        # Satım butonu
        Button(
            parent=ui['market_panel'],
            text='Sat',
            color=color.red,
            position=(0.2, y_pos),
            scale=(0.1, 0.04),
            on_click=Func(lambda s=symbol: sell_stock(s))
        )
        
        y_pos -= 0.08

def create_stats_panel():
    """İstatistik panelini oluştur"""
    ui['stats_panel'] = Entity(
        parent=ui['main_panel'],
        model='quad',
        scale=(0.5, 0.8),
        position=(0.6, -0.05),
        color=color.rgba(0, 0, 0, 0.5)
    )
    
    # Başlık
    Text(
        parent=ui['stats_panel'],
        text='İstatistikler',
        position=(0, 0.35),
        scale=2,
        color=color.white
    )
    
    # İstatistikler
    stats = player['stats']
    y_pos = 0.25
    
    # Toplam işlem
    Text(
        parent=ui['stats_panel'],
        text=f"Toplam İşlem: {stats['total_trades']}",
        position=(0, y_pos),
        scale=1.2,
        color=color.white
    )
    y_pos -= 0.08
    
    # Başarılı işlemler
    Text(
        parent=ui['stats_panel'],
        text=f"Başarılı: {stats['successful_trades']}",
        position=(0, y_pos),
        scale=1.2,
        color=color.green
    )
    y_pos -= 0.08
    
    # Başarısız işlemler
    Text(
        parent=ui['stats_panel'],
        text=f"Başarısız: {stats['failed_trades']}",
        position=(0, y_pos),
        scale=1.2,
        color=color.red
    )
    y_pos -= 0.08
    
    # Toplam kâr
    Text(
        parent=ui['stats_panel'],
        text=f"Toplam Kâr: ${stats['total_profit']:,.2f}",
        position=(0, y_pos),
        scale=1.2,
        color=color.green
    )
    y_pos -= 0.08
    
    # Toplam zarar
    Text(
        parent=ui['stats_panel'],
        text=f"Toplam Zarar: ${stats['total_loss']:,.2f}",
        position=(0, y_pos),
        scale=1.2,
        color=color.red
    )

def toggle_menu():
    """Menüyü aç/kapat"""
    if not ui['menu_panel']:
        create_menu()
    else:
        destroy(ui['menu_panel'])
        ui['menu_panel'] = None

def create_menu():
    """Menü panelini oluştur"""
    ui['menu_panel'] = Entity(
        parent=camera.ui,
        model='quad',
        scale=(0.4, 0.6),
        position=(0, 0),
        color=color.rgba(0, 0, 0, 0.9)
    )
    
    # Başlık
    Text(
        parent=ui['menu_panel'],
        text='Menü',
        position=(0, 0.25),
        scale=2,
        color=color.white
    )
    
    # Kaydet butonu
    Button(
        parent=ui['menu_panel'],
        text='Kaydet',
        color=color.azure,
        position=(0, 0.1),
        scale=(0.3, 0.05),
        on_click=Func(save_game)
    )
    
    # Yükle butonu
    Button(
        parent=ui['menu_panel'],
        text='Yükle',
        color=color.azure,
        position=(0, 0),
        scale=(0.3, 0.05),
        on_click=Func(load_game)
    )
    
    # Ayarlar butonu
    Button(
        parent=ui['menu_panel'],
        text='Ayarlar',
        color=color.azure,
        position=(0, -0.1),
        scale=(0.3, 0.05),
        on_click=Func(show_settings)
    )
    
    # Çıkış butonu
    Button(
        parent=ui['menu_panel'],
        text='Çıkış',
        color=color.red,
        position=(0, -0.2),
        scale=(0.3, 0.05),
        on_click=Func(quit_game)
    )

def show_settings():
    """Ayarlar menüsünü göster"""
    # Mevcut menüyü kapat
    destroy(ui['menu_panel'])
    ui['menu_panel'] = None
    
    # Ayarlar paneli
    ui['settings_panel'] = Entity(
        parent=camera.ui,
        model='quad',
        scale=(0.4, 0.6),
        position=(0, 0),
        color=color.rgba(0, 0, 0, 0.9)
    )
    
    # Başlık
    Text(
        parent=ui['settings_panel'],
        text='Ayarlar',
        position=(0, 0.25),
        scale=2,
        color=color.white
    )
    
    # Ses ayarı
    Button(
        parent=ui['settings_panel'],
        text=f"Ses: {'Açık' if game_settings['sound_enabled'] else 'Kapalı'}",
        color=color.azure,
        position=(0, 0.1),
        scale=(0.3, 0.05),
        on_click=Func(toggle_sound)
    )
    
    # Müzik ayarı
    Button(
        parent=ui['settings_panel'],
        text=f"Müzik: {'Açık' if game_settings['music_enabled'] else 'Kapalı'}",
        color=color.azure,
        position=(0, 0),
        scale=(0.3, 0.05),
        on_click=Func(toggle_music)
    )
    
    # Tam ekran ayarı
    Button(
        parent=ui['settings_panel'],
        text=f"Tam Ekran: {'Açık' if game_settings['fullscreen'] else 'Kapalı'}",
        color=color.azure,
        position=(0, -0.1),
        scale=(0.3, 0.05),
        on_click=Func(toggle_fullscreen)
    )
    
    # Geri butonu
    Button(
        parent=ui['settings_panel'],
        text='Geri',
        color=color.red,
        position=(0, -0.2),
        scale=(0.3, 0.05),
        on_click=Func(lambda: (destroy(ui['settings_panel']), create_menu()))
    )

def toggle_sound():
    """Ses ayarını değiştir"""
    game_settings['sound_enabled'] = not game_settings['sound_enabled']
    show_settings()  # Ayarlar menüsünü yenile

def toggle_music():
    """Müzik ayarını değiştir"""
    game_settings['music_enabled'] = not game_settings['music_enabled']
    show_settings()  # Ayarlar menüsünü yenile

def toggle_fullscreen():
    """Tam ekran ayarını değiştir"""
    game_settings['fullscreen'] = not game_settings['fullscreen']
    window.fullscreen = game_settings['fullscreen']
    show_settings()  # Ayarlar menüsünü yenile

def start_tutorial():
    """Eğitim modunu başlat"""
    tutorial_steps = [
        {
            'title': 'Hoş Geldiniz!',
            'description': 'FinAsis finansal eğitim simülasyonuna hoş geldiniz. Size temel özellikleri tanıtacağım.',
            'position': (0, 0)
        },
        {
            'title': 'Portföy Paneli',
            'description': 'Bu panel sahip olduğunuz hisse senetlerini gösterir.',
            'position': (-0.65, 0)
        },
        {
            'title': 'Market Paneli',
            'description': 'Bu panel piyasadaki hisse senetlerini ve fiyatlarını gösterir.',
            'position': (0, 0)
        },
        {
            'title': 'İstatistik Paneli',
            'description': 'Bu panel trading performansınızı gösterir.',
            'position': (0.65, 0)
        }
    ]
    
    # Tutorial paneli
    tutorial_panel = Entity(
        parent=camera.ui,
        model='quad',
        scale=(0.4, 0.2),
        color=color.rgba(0, 0, 0, 0.9)
    )
    
    current_step = 0
    
    def show_step():
        nonlocal current_step
        step = tutorial_steps[current_step]
        
        # Panel pozisyonu
        tutorial_panel.position = step['position']
        
        # Başlık
        if hasattr(tutorial_panel, 'title'):
            destroy(tutorial_panel.title)
        tutorial_panel.title = Text(
            parent=tutorial_panel,
            text=step['title'],
            position=(0, 0.05),
            scale=1.5,
            color=color.yellow
        )
        
        # Açıklama
        if hasattr(tutorial_panel, 'description'):
            destroy(tutorial_panel.description)
        tutorial_panel.description = Text(
            parent=tutorial_panel,
            text=step['description'],
            position=(0, -0.02),
            scale=1,
            color=color.white
        )
        
        # İleri butonu
        if hasattr(tutorial_panel, 'next_button'):
            destroy(tutorial_panel.next_button)
        tutorial_panel.next_button = Button(
            parent=tutorial_panel,
            text='İleri' if current_step < len(tutorial_steps) - 1 else 'Bitir',
            position=(0.1, -0.07),
            scale=(0.2, 0.05),
            color=color.azure,
            on_click=next_step
        )
    
    def next_step():
        nonlocal current_step
        current_step += 1
        if current_step < len(tutorial_steps):
            show_step()
        else:
            # Tutorial'ı bitir
            destroy(tutorial_panel)
            player['tutorial_progress']['basic_trading'] = True
            save_game()
    
    # İlk adımı göster
    show_step()

def save_game():
    """Oyun durumunu kaydet"""
    try:
        # Kaydedilecek verileri hazırla
        save_data = {
            'player': player,
            'market_state': market_state,
            'quest_system': quest_system,
            'game_settings': game_settings,
            'save_time': datetime.now().isoformat()
        }
        
        # datetime nesnelerini ISO formatına dönüştür
        def convert_datetime(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            return obj
        
        # Verileri JSON formatında kaydet
        with open('save_game.json', 'w', encoding='utf-8') as f:
            json.dump(save_data, f, default=convert_datetime, ensure_ascii=False, indent=4)
            
        show_notification('Oyun kaydedildi!', color.green)
    except Exception as e:
        show_notification(f'Kayıt hatası: {str(e)}', color.red)

def load_game():
    """Kaydedilmiş oyun durumunu yükle"""
    try:
        # JSON dosyasını oku
        with open('save_game.json', 'r', encoding='utf-8') as f:
            save_data = json.load(f)
        
        # datetime string'lerini datetime nesnelerine dönüştür
        def parse_datetime(obj):
            for key, value in obj.items():
                if isinstance(value, str) and 'T' in value:
                    try:
                        obj[key] = datetime.fromisoformat(value)
                    except ValueError:
                        pass
                elif isinstance(value, dict):
                    parse_datetime(value)
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            parse_datetime(item)
            return obj
        
        # Verileri yükle
        global player, market_state, quest_system, game_settings
        player = parse_datetime(save_data['player'])
        market_state = parse_datetime(save_data['market_state'])
        quest_system = parse_datetime(save_data['quest_system'])
        game_settings = save_data['game_settings']
        
        show_notification('Oyun yüklendi!', color.green)
    except FileNotFoundError:
        show_notification('Kayıtlı oyun bulunamadı.', color.yellow)
    except Exception as e:
        show_notification(f'Yükleme hatası: {str(e)}', color.red)

def show_notification(message, color=color.white):
    """Bildirim göster"""
    notification = Text(
        text=message,
        position=(0, 0.4),
        scale=2,
        color=color
    )
    destroy(notification, delay=3)

def auto_save():
    """Otomatik kayıt"""
    current_time = datetime.now()
    if not hasattr(auto_save, 'last_save'):
        auto_save.last_save = current_time
    
    if (current_time - auto_save.last_save).seconds >= game_settings['save_interval']:
        save_game()
        auto_save.last_save = current_time

def quit_game():
    """Oyundan çık"""
    # Oyunu kaydet
    save_game()
    
    # Pencereyi kapat
    application.quit()

def initialize_quest_system():
    """Görev sistemini başlat"""
    # Günlük görevleri yükle
    daily_quests = ['daily_trade', 'daily_profit', 'daily_diversity']
    for quest_id in daily_quests:
        if quest_id in quest_definitions:
            quest_system['daily_quests'].append(quest_definitions[quest_id])
    
    # Haftalık görevleri yükle
    weekly_quests = ['weekly_growth', 'weekly_trades', 'weekly_risk']
    for quest_id in weekly_quests:
        if quest_id in quest_definitions:
            quest_system['weekly_quests'].append(quest_definitions[quest_id])
    
    # Başarı görevlerini yükle
    achievement_quests = ['achievement_portfolio', 'achievement_diversity', 'achievement_debt']
    for quest_id in achievement_quests:
        if quest_id in quest_definitions:
            quest_system['achievement_quests'].append(quest_definitions[quest_id])
    
    # Eğitim görevlerini yükle
    tutorial_quests = ['tutorial_buy', 'tutorial_sell', 'tutorial_diversity']
    for quest_id in tutorial_quests:
        if quest_id in quest_definitions:
            quest_system['tutorial_quests'].append(quest_definitions[quest_id])
    
    # Aktif görevleri belirle
    assign_daily_quests()
    assign_weekly_quests()
    
    # Eğitim görevlerini aktif görevlere ekle
    for quest in quest_system['tutorial_quests']:
        if quest['id'] not in player['completed_quests']:
            player['active_quests'].append(quest['id'])
            player['quest_progress'][quest['id']] = 0
    
    # Başarı görevlerini aktif görevlere ekle
    for quest in quest_system['achievement_quests']:
        if quest['id'] not in player['completed_quests']:
            player['active_quests'].append(quest['id'])
            player['quest_progress'][quest['id']] = 0
    
    # Görev UI'ını oluştur
    create_quest_ui()

def assign_daily_quests():
    """Günlük görevleri ata"""
    # Günlük görevleri sıfırla
    player['active_quests'] = [q for q in player['active_quests'] if q not in [d['id'] for d in quest_system['daily_quests']]]
    
    # Rastgele 2 günlük görev seç
    selected_quests = random.sample(quest_system['daily_quests'], min(2, len(quest_system['daily_quests'])))
    
    # Seçilen görevleri aktif görevlere ekle
    for quest in selected_quests:
        player['active_quests'].append(quest['id'])
        player['quest_progress'][quest['id']] = 0

def assign_weekly_quests():
    """Haftalık görevleri ata"""
    # Haftalık görevleri sıfırla
    player['active_quests'] = [q for q in player['active_quests'] if q not in [w['id'] for w in quest_system['weekly_quests']]]
    
    # Rastgele 2 haftalık görev seç
    selected_quests = random.sample(quest_system['weekly_quests'], min(2, len(quest_system['weekly_quests'])))
    
    # Seçilen görevleri aktif görevlere ekle
    for quest in selected_quests:
        player['active_quests'].append(quest['id'])
        player['quest_progress'][quest['id']] = 0

def check_quest_completion():
    """Görev tamamlanma durumunu kontrol et"""
    completed_quests = []
    
    for quest_id in player['active_quests']:
        if quest_id in quest_definitions:
            quest = quest_definitions[quest_id]
            
            # Görev tamamlandı mı kontrol et
            if quest['check_completion']():
                # Görevi tamamlandı olarak işaretle
                completed_quests.append(quest_id)
                
                # Ödülleri ver
                give_quest_rewards(quest)
                
                # Tamamlanan görevi göster
                show_quest_completion(quest)
    
    # Tamamlanan görevleri aktif görevlerden çıkar
    for quest_id in completed_quests:
        player['active_quests'].remove(quest_id)
        player['completed_quests'].append(quest_id)
    
    # Görev UI'ını güncelle
    update_quest_ui()

def give_quest_rewards(quest):
    """Görev ödüllerini ver"""
    reward = quest['reward']
    
    # Para ödülü
    if 'money' in reward:
        player['money'] += reward['money']
    
    # Deneyim ödülü
    if 'experience' in reward:
        player['experience']['current_xp'] += reward['experience']
        player['experience']['total_xp'] += reward['experience']
        
        # Seviye atlama kontrolü
        while player['experience']['current_xp'] >= player['experience']['next_level_xp']:
            player['experience']['current_xp'] -= player['experience']['next_level_xp']
            player['experience']['level'] += 1
            player['experience']['next_level_xp'] = calculate_next_level_xp(player['experience']['level'])
            show_level_up()
    
    # Başarı ödülü
    if 'achievement' in reward:
        if reward['achievement'] not in player['achievements']:
            player['achievements'].append(reward['achievement'])

def show_quest_completion(quest):
    """Görev tamamlanma bildirimini göster"""
    # Ana bildirim metni
    completion_text = Text(
        text=f"Görev Tamamlandı: {quest['title']}",
        position=(0, 0.6),
        scale=2,
        color=color.gold
    )
    
    # Ödül detayları
    reward_text = None
    if 'money' in quest['reward']:
        reward_text = Text(
            text=f"Ödül: +${quest['reward']['money']:,.2f}",
            position=(0, 0.5),
            scale=1.5,
            color=color.green
        )
    
    # Metinleri belirli süre sonra kaldır
    destroy(completion_text, delay=4)
    if reward_text:
        destroy(reward_text, delay=4)

def show_level_up():
    """Seviye atlama bildirimini göster"""
    level_text = Text(
        text=f"Seviye Atladınız! Yeni Seviye: {player['experience']['level']}",
        position=(0, 0.4),
        scale=2,
        color=color.yellow
    )
    destroy(level_text, delay=4)

def calculate_next_level_xp(current_level):
    """Sonraki seviye için gereken XP'yi hesapla"""
    return int(1000 * (1.5 ** (current_level - 1)))

def create_quest_ui():
    """Görev UI'ını oluştur"""
    # Görev paneli
    quest_ui['panel'] = Entity(
        parent=camera.ui,
        model='quad',
        scale=(0.8, 0.6),
        position=(0, 0),
        color=color.rgba(0, 0, 0, 0.7),
        visible=False
    )
    
    # Görev başlığı
    Text(
        parent=quest_ui['panel'],
        text='Görevler',
        position=(0, 0.25),
        scale=2,
        color=color.white
    )
    
    # Aktif görevler başlığı
    quest_ui['active_quests_text'] = Text(
        parent=quest_ui['panel'],
        text='Aktif Görevler:',
        position=(-0.35, 0.15),
        scale=1.5,
        color=color.white
    )
    
    # Tamamlanan görevler başlığı
    quest_ui['completed_quests_text'] = Text(
        parent=quest_ui['panel'],
        text='Tamamlanan Görevler:',
        position=(-0.35, -0.15),
        scale=1.5,
        color=color.white
    )
    
    # Görev kapatma butonu
    Button(
        parent=quest_ui['panel'],
        text='Kapat',
        color=color.red,
        position=(0, -0.25),
        scale=(0.2, 0.05),
        on_click=Func(lambda: setattr(quest_ui['panel'], 'visible', False))
    )
    
    # Görev butonu
    Button(
        parent=camera.ui,
        text='Görevler',
        color=color.azure,
        position=(0.7, 0.4),
        scale=(0.2, 0.05),
        on_click=Func(lambda: setattr(quest_ui['panel'], 'visible', True))
    )
    
    # Görev UI'ını güncelle
    update_quest_ui()

def update_quest_ui():
    """Görev UI'ını güncelle"""
    # Mevcut görev öğelerini temizle
    for item in quest_ui['quest_items']:
        destroy(item)
    quest_ui['quest_items'] = []
    
    # Aktif görevleri göster
    y_position = 0.1
    for quest_id in player['active_quests']:
        if quest_id in quest_definitions:
            quest = quest_definitions[quest_id]
            
            # Görev başlığı
            quest_ui['quest_items'].append(
                Text(
                    parent=quest_ui['panel'],
                    text=quest['title'],
                    position=(-0.3, y_position),
                    scale=1.2,
                    color=color.white
                )
            )
            
            # Görev açıklaması
            quest_ui['quest_items'].append(
                Text(
                    parent=quest_ui['panel'],
                    text=quest['description'],
                    position=(-0.3, y_position - 0.05),
                    scale=0.8,
                    color=color.light_gray
                )
            )
            
            # Görev ödülü
            reward_text = f"Ödül: ${quest['reward']['money']:,.2f}"
            quest_ui['quest_items'].append(
                Text(
                    parent=quest_ui['panel'],
                    text=reward_text,
                    position=(-0.3, y_position - 0.1),
                    scale=0.8,
                    color=color.gold
                )
            )
            
            y_position -= 0.15
    
    # Tamamlanan görevleri göster
    y_position = -0.2
    for quest_id in player['completed_quests'][-5:]:  # Son 5 tamamlanan görevi göster
        if quest_id in quest_definitions:
            quest = quest_definitions[quest_id]
            
            # Görev başlığı
            quest_ui['quest_items'].append(
                Text(
                    parent=quest_ui['panel'],
                    text=quest['title'],
                    position=(-0.3, y_position),
                    scale=1.2,
                    color=color.light_gray
                )
            )
            
            # Tamamlandı işareti
            quest_ui['quest_items'].append(
                Text(
                    parent=quest_ui['panel'],
                    text="✓ Tamamlandı",
                    position=(0.2, y_position),
                    scale=0.8,
                    color=color.green
                )
            )
            
            y_position -= 0.1

def calculate_daily_profit():
    """Günlük kârı hesapla"""
    today = datetime.now().date()
    today_trades = [t for t in player['trading_history'] if t['timestamp'].date() == today]
    
    profit = 0
    for trade in today_trades:
        if trade['type'] == 'sell':
            # Satış işleminden kâr hesapla
            buy_trades = [t for t in player['trading_history'] if t['stock'] == trade['stock'] and t['type'] == 'buy' and t['timestamp'].date() <= today]
            if buy_trades:
                # En eski alım fiyatını bul
                oldest_buy = min(buy_trades, key=lambda t: t['timestamp'])
                buy_price = oldest_buy['price']
                sell_price = trade['price']
                profit += (sell_price - buy_price) * trade['amount']
    
    return profit

def calculate_weekly_growth():
    """Haftalık büyümeyi hesapla"""
    # Başlangıç portföy değeri (1 hafta önce)
    week_ago = datetime.now() - timedelta(days=7)
    week_ago_trades = [t for t in player['trading_history'] if t['timestamp'] <= week_ago]
    
    # Şu anki portföy değeri
    current_value = calculate_portfolio_value()
    
    # Haftalık büyüme oranı
    if current_value > 0:
        return (current_value / 100000) - 1  # Başlangıç değerine göre büyüme
    return 0

def update_market_state():
    """Piyasa durumunu güncelle"""
    current_time = datetime.now()
    if (current_time - market_state['last_update']).seconds >= 30:  # Her 30 saniyede bir güncelle
        # Piyasa trendini güncelle
        trend_chance = random.random()
        if trend_chance < 0.4:
            market_state['trend'] = 'stable'
        elif trend_chance < 0.7:
            market_state['trend'] = 'bull'
        else:
            market_state['trend'] = 'bear'
        
        # Volatiliteyi güncelle
        market_state['volatility'] = random.uniform(0.3, 0.8)
        
        # Piyasa olayları oluştur
        if random.random() < 0.2:  # %20 şans
            event = generate_market_event()
            market_state['market_events'].append(event)
            show_market_event(event)
            apply_market_event(event)
        
        # Oyuncuya özel olaylar oluştur
        if random.random() < 0.15:  # %15 şans
            player_event = generate_player_event()
            if player_event:
                show_player_event(player_event)
                apply_player_event(player_event)
        
        # Görev tamamlanma durumunu kontrol et
        check_quest_completion()
        
        market_state['last_update'] = current_time

def update():
    """Ana oyun döngüsü"""
    # Piyasa güncellemesi
    update_market()
    
    # UI güncellemesi
    update_ui()
    
    # Görev kontrolü
    check_quests()
    
    # Otomatik kayıt
    if game_settings['auto_save']:
        auto_save()

def update_market():
    """Piyasa durumunu güncelle"""
    current_time = datetime.now()
    
    # Piyasa güncellemesi
    if (current_time - market_state['last_update']).seconds >= game_settings['market_update_interval']:
        # Trend güncelleme
        update_market_trend()
        
        # Fiyat güncelleme
        update_stock_prices()
        
        # Olay kontrolü
        check_market_events()
        
        market_state['last_update'] = current_time

def update_market_trend():
    """Piyasa trendini güncelle"""
    trend_chance = random.random()
    
    # Zorluk seviyesine göre trend olasılıkları
    if game_settings['difficulty'] == 'easy':
        if trend_chance < 0.5:  # %50 şans
            market_state['trend'] = 'bull'
        elif trend_chance < 0.8:  # %30 şans
            market_state['trend'] = 'stable'
        else:  # %20 şans
            market_state['trend'] = 'bear'
    elif game_settings['difficulty'] == 'normal':
        if trend_chance < 0.4:  # %40 şans
            market_state['trend'] = 'bull'
        elif trend_chance < 0.7:  # %30 şans
            market_state['trend'] = 'stable'
        else:  # %30 şans
            market_state['trend'] = 'bear'
    else:  # hard
        if trend_chance < 0.3:  # %30 şans
            market_state['trend'] = 'bull'
        elif trend_chance < 0.5:  # %20 şans
            market_state['trend'] = 'stable'
        else:  # %50 şans
            market_state['trend'] = 'bear'
    
    # Volatilite güncelleme
    market_state['volatility'] = random.uniform(
        0.2 if game_settings['difficulty'] == 'easy' else 0.3 if game_settings['difficulty'] == 'normal' else 0.4,
        0.5 if game_settings['difficulty'] == 'easy' else 0.7 if game_settings['difficulty'] == 'normal' else 0.9
    )

def update_stock_prices():
    """Hisse senedi fiyatlarını güncelle"""
    for symbol, data in player['portfolio'].items():
        base_price = data['price']
        
        # Trend etkisi
        trend_effect = {
            'bull': random.uniform(0.001, 0.01),
            'stable': random.uniform(-0.003, 0.003),
            'bear': random.uniform(-0.01, -0.001)
        }[market_state['trend']]
        
        # Sektör etkisi
        sector_effect = calculate_sector_effect(data['sector'])
        
        # Volatilite etkisi
        volatility_effect = random.uniform(-market_state['volatility'], market_state['volatility'])
        
        # Toplam değişim
        total_change = trend_effect + sector_effect + volatility_effect
        
        # Zorluk seviyesine göre değişim sınırlaması
        if game_settings['difficulty'] == 'easy':
            total_change = max(-0.05, min(0.05, total_change))
        elif game_settings['difficulty'] == 'normal':
            total_change = max(-0.1, min(0.1, total_change))
        else:  # hard
            total_change = max(-0.15, min(0.15, total_change))
        
        # Yeni fiyat
        new_price = base_price * (1 + total_change)
        player['portfolio'][symbol]['price'] = max(0.01, new_price)

def calculate_sector_effect(sector):
    """Sektör bazlı fiyat etkisini hesapla"""
    sector_trends = {
        'tech': random.uniform(-0.005, 0.008),
        'auto': random.uniform(-0.004, 0.006),
        'retail': random.uniform(-0.003, 0.005),
        'media': random.uniform(-0.004, 0.007),
        'finance': random.uniform(-0.003, 0.004)
    }
    return sector_trends.get(sector, 0)

def check_market_events():
    """Piyasa olaylarını kontrol et"""
    if random.random() < game_settings['event_chance']:
        event = generate_market_event()
        if event:
            market_state['market_events'].append(event)
            apply_market_event(event)
            show_market_event(event)

def generate_market_event():
    """Piyasa olayı oluştur"""
    event_types = {
        'global': [
            {
                'title': 'Küresel Ekonomik Büyüme',
                'description': 'Küresel ekonomik büyüme beklentileri yükseldi!',
                'effect': {'market_trend': 'bull', 'volatility': -0.1},
                'duration': 300,
                'probability': 0.2
            },
            {
                'title': 'Ekonomik Kriz',
                'description': 'Küresel ekonomik kriz endişeleri artıyor!',
                'effect': {'market_trend': 'bear', 'volatility': 0.2},
                'duration': 300,
                'probability': 0.1
            }
        ],
        'sector': [
            {
                'title': 'Teknoloji Atılımı',
                'description': 'Yeni teknolojik gelişmeler sektörü hareketlendirdi!',
                'effect': {'sector': 'tech', 'change': 0.05},
                'duration': 180,
                'probability': 0.15
            },
            {
                'title': 'Otomotiv Krizi',
                'description': 'Tedarik zinciri sorunları otomotiv sektörünü vuruyor!',
                'effect': {'sector': 'auto', 'change': -0.05},
                'duration': 180,
                'probability': 0.15
            }
        ],
        'company': [
            {
                'title': 'Ürün Lansmanı',
                'description': 'AAPL yeni ürünlerini tanıttı!',
                'effect': {'symbol': 'AAPL', 'change': 0.08},
                'duration': 120,
                'probability': 0.2
            },
            {
                'title': 'CEO İstifası',
                'description': 'TSLA CEO\'su istifa etti!',
                'effect': {'symbol': 'TSLA', 'change': -0.08},
                'duration': 120,
                'probability': 0.1
            }
        ]
    }
    
    # Olay türü seç
    event_type = random.choice(list(event_types.keys()))
    events = event_types[event_type]
    
    # Olasılık kontrolü
    for event in events:
        if random.random() < event['probability']:
            return event
    
    return None

def apply_market_event(event):
    """Piyasa olayını uygula"""
    effect = event['effect']
    
    # Piyasa trendi etkisi
    if 'market_trend' in effect:
        market_state['trend'] = effect['market_trend']
    
    # Volatilite etkisi
    if 'volatility' in effect:
        market_state['volatility'] = max(0.1, min(1.0, market_state['volatility'] + effect['volatility']))
    
    # Sektör etkisi
    if 'sector' in effect:
        for symbol, data in player['portfolio'].items():
            if data['sector'] == effect['sector']:
                data['price'] *= (1 + effect['change'])
    
    # Şirket etkisi
    if 'symbol' in effect:
        if effect['symbol'] in player['portfolio']:
            player['portfolio'][effect['symbol']]['price'] *= (1 + effect['change'])

def show_market_event(event):
    """Piyasa olayını göster"""
    # Bildirim paneli
    notification = Entity(
        parent=camera.ui,
        model='quad',
        scale=(0.6, 0.2),
        position=(0, 0.3),
        color=color.rgba(0, 0, 0, 0.9)
    )
    
    # Başlık
    title_text = Text(
        parent=notification,
        text=event['title'],
        position=(0, 0.05),
        scale=1.5,
        color=color.yellow
    )
    
    # Açıklama
    desc_text = Text(
        parent=notification,
        text=event['description'],
        position=(0, -0.02),
        scale=1.2,
        color=color.white
    )
    
    # Efekt açıklaması
    effect = event['effect']
    effect_text = ""
    
    if 'market_trend' in effect:
        effect_text = "Piyasa trendi değişti!"
    elif 'sector' in effect:
        effect_text = f"{effect['sector'].upper()} sektörü etkilendi!"
    elif 'symbol' in effect:
        effect_text = f"{effect['symbol']} hissesi etkilendi!"
    
    Text(
        parent=notification,
        text=effect_text,
        position=(0, -0.08),
        scale=1,
        color=color.azure
    )
    
    # Bildirimi kaydet
    ui['notifications'].append({
        'entity': notification,
        'created_at': datetime.now(),
        'duration': 5  # 5 saniye sonra kaybolacak
    })

def calculate_portfolio_value():
    """Portföy değerini hesapla"""
    total_value = player['money']
    for symbol, data in player['portfolio'].items():
        total_value += data['shares'] * data['price']
    return total_value

def calculate_risk_score():
    """Risk skorunu hesapla"""
    # Portföy çeşitliliği (0-1 arası)
    portfolio_diversity = calculate_portfolio_diversity()
    
    # Borç/gelir oranı (0-1 arası)
    debt_to_income = calculate_debt_to_income_ratio()
    
    # Toplam risk skoru (0-1 arası)
    risk_score = (1 - portfolio_diversity) * 0.6 + debt_to_income * 0.4
    return min(max(risk_score, 0), 1)

def calculate_portfolio_diversity():
    """Portföy çeşitliliğini hesapla"""
    total_value = calculate_portfolio_value()
    if total_value == 0:
        return 0
    
    # Her sektördeki yatırım oranını hesapla
    sector_weights = {}
    for symbol, data in player['portfolio'].items():
        sector = data['sector']
        value = data['shares'] * data['price']
        sector_weights[sector] = sector_weights.get(sector, 0) + value / total_value
    
    # Herfindahl-Hirschman Index'ini hesapla (ters çevrilmiş)
    hhi = sum(weight * weight for weight in sector_weights.values())
    diversity = 1 - hhi
    return min(max(diversity, 0), 1)

def calculate_debt_to_income_ratio():
    """Borç/gelir oranını hesapla"""
    total_income = sum(t['amount'] for t in player.get('trading_history', []) 
                      if t['type'] == 'profit' and (datetime.now() - t['timestamp']).days <= 30)
    total_debt = sum(t['amount'] for t in player.get('trading_history', [])
                    if t['type'] == 'loss' and (datetime.now() - t['timestamp']).days <= 30)
    
    if total_income == 0:
        return 1 if total_debt > 0 else 0
    
    ratio = total_debt / total_income
    return min(max(ratio, 0), 1)

def update_ui():
    """UI'ı güncelle"""
    # Para ve portföy değerini güncelle
    ui['text_elements']['money'].text = f"Para: ${player['money']:,.2f}"
    ui['text_elements']['portfolio_value'].text = f"Portföy: ${calculate_portfolio_value():,.2f}"
    ui['text_elements']['risk_score'].text = f"Risk: {calculate_risk_score():.2f}"
    
    # Hisse senedi fiyatlarını güncelle
    for symbol, data in player['portfolio'].items():
        if symbol in ui['text_elements']:
            ui['text_elements'][symbol].text = f"{symbol}: ${data['price']:,.2f}"
    
    # Hisse senedi butonlarını güncelle
    update_stock_buttons()
    
    # Görevleri güncelle
    update_quest_ui()
    
    # Bildirimleri güncelle
    update_notifications()

def update_stock_buttons():
    """Hisse senedi butonlarını güncelle"""
    for symbol, data in player['portfolio'].items():
        # Alım butonu
        if symbol + '_buy' in ui['buttons']:
            ui['buttons'][symbol + '_buy'].enabled = player['money'] >= data['price']
        
        # Satım butonu
        if symbol + '_sell' in ui['buttons']:
            ui['buttons'][symbol + '_sell'].enabled = data['shares'] > 0

def update_notifications():
    """Bildirimleri güncelle"""
    current_time = datetime.now()
    
    # Süresi dolmuş bildirimleri kaldır
    ui['notifications'] = [n for n in ui['notifications'] 
                         if (current_time - n['timestamp']).seconds < 5]
    
    # Bildirimleri göster
    for i, notification in enumerate(ui['notifications']):
        if 'text' in notification:
            notification['text'].y = -0.3 - i * 0.1

def buy_stock(symbol):
    """Hisse senedi satın al"""
    stock = player['portfolio'][symbol]
    price = stock['price']
    
    # Yeterli para var mı kontrol et
    if player['money'] < price:
        show_notification('Yeterli paranız yok!', color.red)
        return
    
    # İşlemi gerçekleştir
    player['money'] -= price
    stock['shares'] += 1
    
    # İşlem kaydını tut
    trade = {
        'type': 'buy',
        'symbol': symbol,
        'price': price,
from __future__ import absolute_import, unicode_literals
import os
import random
from datetime import datetime, timedelta
import json
from ursina import Entity, Vec3, color, window, Ursina, Text, Button, Func, camera, destroy, application, WindowPanel, DirectionalLight, held_keys, mouse
from ursina.prefabs.first_person_controller import FirstPersonController
from . import FinansalSimulasyonOyunu
from .ar_module import ARManager
from .locales.locale_manager import LocaleManager
import time
import platform
from typing import Dict, List, Optional
import threading
from game_integration import GameIntegration

# Django ayarlarını yükle
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
# django.setup() satırı kaldırıldı - circular import sorununa yol açıyor

# Oyun içindeki şirket modelleri yerine sınıflar kullan
class GameCompany:
    def __init__(self, name, sector):
        self.name = name
        self.sector = sector

class GameDepartment:
    def __init__(self, name, company):
        self.name = name
        self.company = company

class GameEmployee:
    def __init__(self, name, department):
        self.name = name
        self.department = department

# Oyun ayarları
game_settings = {
    'difficulty': 'normal',  # easy, normal, hard
    'market_update_interval': 5,  # saniye
    'event_chance': 0.2,  # 0-1 arası
    'starting_money': 100000,
    'tutorial_enabled': True,
    'sound_enabled': True,
    'music_enabled': True,
    'fullscreen': False,
    'show_tooltips': True,
    'auto_save': True,
    'save_interval': 300  # saniye
}

# Piyasa durumu
market_state = {
    'trend': 'stable',  # bull, stable, bear
    'volatility': 0.5,  # 0-1 arası
    'last_update': datetime.now(),
    'market_events': []
}

# UI bileşenleri
ui = {
    'main_panel': None,
    'portfolio_panel': None,
    'market_panel': None,
    'stats_panel': None,
    'quest_panel': None,
    'notification_panel': None,
    'tooltip_panel': None,
    'menu_panel': None,
    'text_elements': {},
    'buttons': {},
    'charts': {},
    'notifications': []
}

# Oyuncu verileri
player = {
    'id': 1,
    'name': 'John Doe',
    'money': game_settings['starting_money'],
    'portfolio': {
        'AAPL': {'shares': 10, 'price': 150, 'sector': 'tech'},
        'GOOGL': {'shares': 5, 'price': 2000, 'sector': 'tech'},
        'TSLA': {'shares': 8, 'price': 700, 'sector': 'auto'},
        'MSFT': {'shares': 0, 'price': 300, 'sector': 'tech'},
        'AMZN': {'shares': 0, 'price': 3000, 'sector': 'retail'},
        'META': {'shares': 0, 'price': 250, 'sector': 'tech'},
        'NFLX': {'shares': 0, 'price': 400, 'sector': 'media'},
        'NVDA': {'shares': 0, 'price': 500, 'sector': 'tech'},
        'JPM': {'shares': 0, 'price': 150, 'sector': 'finance'},
        'BAC': {'shares': 0, 'price': 40, 'sector': 'finance'}
    },
    'stats': {
        'total_trades': 0,
        'successful_trades': 0,
        'failed_trades': 0,
        'profit_trades': 0,
        'loss_trades': 0,
        'total_profit': 0,
        'total_loss': 0,
        'best_trade': 0,
        'worst_trade': 0,
        'longest_holding': 0,
        'shortest_holding': 0,
        'risk_tolerance': 0.7,
        'trading_style': 'balanced',  # aggressive, balanced, conservative
        'debt_to_income': 0.0,  # Borç/gelir oranı
        'portfolio_diversity': 0.0,  # Portföy çeşitliliği
        'total_debt': 0,  # Toplam borç
        'total_income': 0,  # Toplam gelir
        'monthly_income': 0,  # Aylık gelir
        'monthly_expenses': 0  # Aylık giderler
    },
    'skills': {
        'analysis': 1,  # 1-10 arası
        'risk_management': 1,
        'market_knowledge': 1,
        'technical_analysis': 1,
        'fundamental_analysis': 1
    },
    'experience': {
        'level': 1,
        'current_xp': 0,
        'next_level_xp': 1000,
        'total_xp': 0
    },
    'achievements': [],
    'active_quests': [],
    'completed_quests': [],
    'quest_progress': {},
    'tutorial_progress': {
        'basic_trading': False,
        'market_analysis': False,
        'risk_management': False,
        'portfolio_management': False,
        'technical_analysis': False
    },
    'settings': {
        'notifications': True,
        'sound': True,
        'music': True,
        'tooltips': True,
        'auto_save': True
    },
    'trading_history': []
}

# Görev sistemi
quest_system = {
    'daily_quests': [],
    'weekly_quests': [],
    'achievement_quests': [],
    'tutorial_quests': []
}

# Görev tanımlamaları
quest_definitions = {
    # Günlük görevler
    'daily_trade': {
        'id': 'daily_trade',
        'title': 'Günlük İşlem',
        'description': 'Bugün en az 1 hisse senedi alım veya satım işlemi yapın.',
        'reward': {'money': 500, 'experience': 100},
        'type': 'daily',
        'check_completion': lambda: len([t for t in player['trading_history'] if (datetime.now() - t['timestamp']).days < 1]) > 0
    },
    'daily_profit': {
        'id': 'daily_profit',
        'title': 'Günlük Kâr',
        'description': 'Bugün portföyünüzden 1000$ kâr elde edin.',
        'reward': {'money': 1000, 'experience': 200},
        'type': 'daily',
        'check_completion': lambda: calculate_daily_profit() >= 1000
    },
    'daily_diversity': {
        'id': 'daily_diversity',
        'title': 'Çeşitlilik Ustası',
        'description': 'Portföy çeşitliliğinizi 0.7\'nin üzerine çıkarın.',
        'reward': {'money': 800, 'experience': 150},
        'type': 'daily',
        'check_completion': lambda: player['stats']['portfolio_diversity'] > 0.7
    },
    
    # Haftalık görevler
    'weekly_growth': {
        'id': 'weekly_growth',
        'title': 'Haftalık Büyüme',
        'description': 'Portföyünüzü bu hafta %10 büyütün.',
        'reward': {'money': 5000, 'experience': 500},
        'type': 'weekly',
        'check_completion': lambda: calculate_weekly_growth() >= 0.1
    },
    'weekly_trades': {
        'id': 'weekly_trades',
        'title': 'Aktif Trader',
        'description': 'Bu hafta en az 10 işlem yapın.',
        'reward': {'money': 3000, 'experience': 400},
        'type': 'weekly',
        'check_completion': lambda: len([t for t in player['trading_history'] if (datetime.now() - t['timestamp']).days < 7]) >= 10
    },
    'weekly_risk': {
        'id': 'weekly_risk',
        'title': 'Risk Yöneticisi',
        'description': 'Risk skorunuzu 0.5\'in altına düşürün.',
        'reward': {'money': 4000, 'experience': 450},
        'type': 'weekly',
        'check_completion': lambda: calculate_risk_score() < 0.5
    },
    
    # Başarı görevleri
    'achievement_portfolio': {
        'id': 'achievement_portfolio',
        'title': 'Portföy Ustası',
        'description': 'Portföyünüzü 200.000$ değerine ulaştırın.',
        'reward': {'money': 10000, 'experience': 1000, 'achievement': 'portfolio_master'},
        'type': 'achievement',
        'check_completion': lambda: calculate_portfolio_value() >= 200000
    },
    'achievement_diversity': {
        'id': 'achievement_diversity',
        'title': 'Çeşitlilik Kralı',
        'description': 'Portföy çeşitliliğinizi 0.9\'un üzerine çıkarın.',
        'reward': {'money': 8000, 'experience': 800, 'achievement': 'diversity_king'},
        'type': 'achievement',
        'check_completion': lambda: player['stats']['portfolio_diversity'] > 0.9
    },
    'achievement_debt': {
        'id': 'achievement_debt',
        'title': 'Borçsuz Yaşam',
        'description': 'Borç/gelir oranınızı 0.1\'in altına düşürün.',
        'reward': {'money': 6000, 'experience': 600, 'achievement': 'debt_free'},
        'type': 'achievement',
        'check_completion': lambda: player['stats']['debt_to_income'] < 0.1
    },
    
    # Eğitim görevleri
    'tutorial_buy': {
        'id': 'tutorial_buy',
        'title': 'İlk Alım',
        'description': 'İlk hisse senedi alım işleminizi yapın.',
        'reward': {'money': 1000, 'experience': 200},
        'type': 'tutorial',
        'check_completion': lambda: len([t for t in player['trading_history'] if t['type'] == 'buy']) > 0
    },
    'tutorial_sell': {
        'id': 'tutorial_sell',
        'title': 'İlk Satım',
        'description': 'İlk hisse senedi satım işleminizi yapın.',
        'reward': {'money': 1000, 'experience': 200},
        'type': 'tutorial',
        'check_completion': lambda: len([t for t in player['trading_history'] if t['type'] == 'sell']) > 0
    },
    'tutorial_diversity': {
        'id': 'tutorial_diversity',
        'title': 'Çeşitlendirme',
        'description': 'En az 3 farklı hisse senedine yatırım yapın.',
        'reward': {'money': 2000, 'experience': 300},
        'type': 'tutorial',
        'check_completion': lambda: len([s for s in player['portfolio'].values() if s['shares'] > 0]) >= 3
    }
}

# Görev UI elementleri
quest_ui = {
    'panel': None,
    'quest_items': [],
    'active_quests_text': None,
    'completed_quests_text': None
}

class FinansalDunya(Entity):
    def __init__(self, online_mode: bool = False):
        super().__init__()
        self.oyun = FinansalSimulasyonOyunu(online_mode=online_mode)
        self.oyuncu = FirstPersonController()
        self.oyuncu.position = (0, 2, 0)
        
        # Dil yöneticisi
        self.locale_manager = LocaleManager()
        
        # Platform kontrolü
        self.platform = self.oyun.platform
        self.is_mobile = self.platform in ['android', 'ios']
        
        # AR yöneticisini başlat (mobil platformlarda)
        if self.is_mobile:
            self.ar_manager = ARManager(use_aruco=True, show_camera=True)
            self.ar_manager.start()
            
        # Dünya oluşturma
        self.dunya = Entity(
            model='plane',
            texture='white_cube',
            scale=(100, 1, 100),
            color=color.gray
        )
        
        # Binalar ve iş yerleri
        self.binalar = []
        self.is_yerleri = []
        self.olaylar = []
        
        # UI elementleri
        self.ui_elements = {}
        
        # Performans optimizasyonu
        self.last_update = time.time()
        self.update_interval = 0.016  # ~60 FPS
        
        # Oyun durumu
        self.is_paused = False
        self.is_saving = False
        
        # Tuş durumları
        self.held_keys = {'w': False, 'a': False, 's': False, 'd': False, 'left mouse': False, 'right mouse': False}
        
        # İnitialize
        self.bina_olustur()
        self.is_yeri_olustur()
        self.olay_olustur()
        self.ui_olustur()
        
        # Otomatik kayıt
        self.auto_save_thread = threading.Thread(target=self._auto_save_loop)
        self.auto_save_thread.daemon = True
        self.auto_save_thread.start()

    def ui_olustur(self):
        # Ana panel
        self.ui_elements['ana_panel'] = Entity(
            parent=camera.ui,
            model='quad',
            scale=(0.8, 0.6),
            position=(0, 0),
            color=color.rgba(0, 0, 0, 0.7)
        )
        
        # Bakiye göstergesi
        self.ui_elements['bakiye'] = Text(
            parent=self.ui_elements['ana_panel'],
            text=f"{self.locale_manager.get_text('game.stats.balance')}: ${self.oyun.oyuncu_bakiyesi:,.2f}",
            position=(-0.4, 0.4),
            scale=2,
            color=color.green
        )
        
        # Puan göstergesi
        self.ui_elements['puan'] = Text(
            parent=self.ui_elements['ana_panel'],
            text=f"{self.locale_manager.get_text('game.stats.score')}: {self.oyun.oyuncu_puani}",
            position=(0.4, 0.4),
            scale=2,
            color=color.yellow
        )
        
        # Seviye göstergesi
        self.ui_elements['seviye'] = Text(
            parent=self.ui_elements['ana_panel'],
            text=f"{self.locale_manager.get_text('game.stats.level')}: {self.oyun.oyuncu_seviyesi}",
            position=(0, 0.4),
            scale=2,
            color=color.azure
        )
        
        # İşlem butonları
        self.ui_elements['alis_buton'] = Button(
            parent=self.ui_elements['ana_panel'],
            text=self.locale_manager.get_text('game.transactions.buy'),
            color=color.green,
            position=(-0.2, 0),
            scale=(0.2, 0.1),
            on_click=self.alis_yap
        )
        
        self.ui_elements['satis_buton'] = Button(
            parent=self.ui_elements['ana_panel'],
            text=self.locale_manager.get_text('game.transactions.sell'),
            color=color.red,
            position=(0.2, 0),
            scale=(0.2, 0.1),
            on_click=self.satis_yap
        )
        
        # Bildirim paneli
        self.ui_elements['bildirim'] = Text(
            parent=self.ui_elements['ana_panel'],
            text='',
            position=(0, -0.4),
            scale=1.5,
            color=color.white
        )
        
        # Menü butonu
        self.ui_elements['menu_buton'] = Button(
            parent=camera.ui,
            text=self.locale_manager.get_text('game.menu.settings'),
            color=color.azure,
            position=(0.8, 0.45),
            scale=(0.2, 0.05),
            on_click=self.toggle_menu
        )
        
        # Dil seçimi butonu
        self.ui_elements['dil_buton'] = Button(
            parent=camera.ui,
            text=f"Dil: {self.locale_manager.get_current_locale().upper()}",
            color=color.azure,
            position=(0.8, 0.35),
            scale=(0.2, 0.05),
            on_click=self.toggle_language
        )
        
        # Mobil kontroller
        if self.is_mobile:
            self._create_mobile_controls()
            
    def toggle_language(self):
        """Dil seçimini değiştir"""
        available_locales = self.locale_manager.get_available_locales()
        current_index = available_locales.index(self.locale_manager.get_current_locale())
        next_index = (current_index + 1) % len(available_locales)
        self.locale_manager.set_locale(available_locales[next_index])
        
        # UI'ı güncelle
        self.ui_guncelle()
        
    def alis_yap(self):
        if self.oyun.oyuncu_bakiyesi >= 1000:
            basari = self.oyun.islem_yap('alis', 1000, 0.5)
            if basari:
                self.ui_elements['bildirim'].text = self.locale_manager.get_text('game.transactions.success')
                self.ui_elements['bildirim'].color = color.green
            else:
                self.ui_elements['bildirim'].text = self.locale_manager.get_text('game.transactions.fail')
                self.ui_elements['bildirim'].color = color.red
        else:
            self.ui_elements['bildirim'].text = self.locale_manager.get_text('game.transactions.insufficient_balance')
            self.ui_elements['bildirim'].color = color.red
            
        self.ui_guncelle()
        
    def satis_yap(self):
        basari = self.oyun.islem_yap('satis', 1000, 0.3)
        if basari:
            self.ui_elements['bildirim'].text = self.locale_manager.get_text('game.transactions.success')
            self.ui_elements['bildirim'].color = color.green
        else:
            self.ui_elements['bildirim'].text = self.locale_manager.get_text('game.transactions.fail')
            self.ui_elements['bildirim'].color = color.red
            
        self.ui_guncelle()
        
    def ui_guncelle(self):
        self.ui_elements['bakiye'].text = f"{self.locale_manager.get_text('game.stats.balance')}: ${self.oyun.oyuncu_bakiyesi:,.2f}"
        self.ui_elements['puan'].text = f"{self.locale_manager.get_text('game.stats.score')}: {self.oyun.oyuncu_puani}"
        self.ui_elements['seviye'].text = f"{self.locale_manager.get_text('game.stats.level')}: {self.oyun.oyuncu_seviyesi}"
        self.ui_elements['alis_buton'].text = self.locale_manager.get_text('game.transactions.buy')
        self.ui_elements['satis_buton'].text = self.locale_manager.get_text('game.transactions.sell')
        self.ui_elements['menu_buton'].text = self.locale_manager.get_text('game.menu.settings')
        self.ui_elements['dil_buton'].text = f"Dil: {self.locale_manager.get_current_locale().upper()}"
        
    def toggle_menu(self):
        """Menüyü aç/kapat"""
        self.is_paused = not self.is_paused
        
        if self.is_paused:
            # Menü panelini göster
            self.ui_elements['menu_panel'] = Entity(
                parent=camera.ui,
                model='quad',
                scale=(0.4, 0.6),
                position=(0, 0),
                color=color.rgba(0, 0, 0, 0.9)
            )
            
            # Menü butonları
            Button(
                parent=self.ui_elements['menu_panel'],
                text=self.locale_manager.get_text('game.menu.continue'),
                color=color.green,
                position=(0, 0.2),
                scale=(0.3, 0.05),
                on_click=self.toggle_menu
            )
            
            Button(
                parent=self.ui_elements['menu_panel'],
                text='Kaydet',
                color=color.azure,
                position=(0, 0.1),
                scale=(0.3, 0.05),
                on_click=self.oyun.save_game
            )
            
            Button(
                parent=self.ui_elements['menu_panel'],
                text='Yükle',
                color=color.azure,
                position=(0, 0),
                scale=(0.3, 0.05),
                on_click=self.oyun.load_game
            )
            
            Button(
                parent=self.ui_elements['menu_panel'],
                text='Çıkış',
                color=color.red,
                position=(0, -0.2),
                scale=(0.3, 0.05),
                on_click=application.quit
            )
        else:
            # Menü panelini kaldır
            if 'menu_panel' in self.ui_elements:
                destroy(self.ui_elements['menu_panel'])
                del self.ui_elements['menu_panel']
        
    def update(self):
        # Performans kontrolü
        current_time = time.time()
        if current_time - self.last_update < self.update_interval:
            return
        self.last_update = current_time
        
        if self.is_paused:
            return
            
        # Oyun güncellemeleri
        if self.held_keys['left mouse']:
            self.alis_yap()
            
        if self.held_keys['right mouse']:
            self.satis_yap()
            
        # AR güncellemeleri
        if self.is_mobile:
            self.ar_manager.ar_nesne_guncelle()
            
        # Olay güncellemeleri
        self.olay_guncelle()
        
    def olay_guncelle(self):
        simdiki_zaman = time.time()
        for olay in self.olaylar:
            if simdiki_zaman - olay['baslangic'] > olay['sure']:
                # Olay süresi doldu, yeni olay oluştur
                olay['tip'] = random.choice([
                    'Borsa Yükselişi', 'Borsa Düşüşü',
                    'Enflasyon Artışı', 'Enflasyon Düşüşü',
                    'Faiz Artışı', 'Faiz Düşüşü',
                    'Döviz Dalgalanması', 'Altın Fiyatı Değişimi'
                ])
                olay['etki'] = random.uniform(-0.2, 0.2)
                olay['baslangic'] = simdiki_zaman
                
                # Olay bildirimi
                self.ui_elements['bildirim'].text = f"Yeni Olay: {olay['tip']}"
                self.ui_elements['bildirim'].color = color.yellow

def run_game(online_mode: bool = False):
    """Oyunu başlat"""
    app = Ursina()
    dunya = FinansalDunya(online_mode=online_mode)
    app.run()

def create_ui():
    """Ana UI'ı oluştur"""
    # Ana panel
    ui['main_panel'] = Entity(
        parent=camera.ui,
        model='quad',
        scale=(1.8, 1),
        position=(0, 0),
        color=color.rgba(0, 0, 0, 0.8)
    )
    
    # Üst bilgi paneli
    create_top_info_panel()
    
    # Portföy paneli
    create_portfolio_panel()
    
    # Market paneli
    create_market_panel()
    
    # İstatistik paneli
    create_stats_panel()
    
    # Menü butonu
    Button(
        parent=camera.ui,
        text='Menü',
        color=color.azure,
        position=(0.8, 0.45),
        scale=(0.2, 0.05),
        on_click=Func(toggle_menu)
    )

def create_top_info_panel():
    """Üst bilgi panelini oluştur"""
    # Para
    ui['text_elements']['money'] = Text(
        parent=camera.ui,
        text=f"${player['money']:,.2f}",
        position=(-0.8, 0.45),
        scale=2,
        color=color.green
    )
    
    # Portföy değeri
    ui['text_elements']['portfolio_value'] = Text(
        parent=camera.ui,
        text=f"Portföy: ${calculate_portfolio_value():,.2f}",
        position=(-0.4, 0.45),
        scale=2,
        color=color.white
    )
    
    # Risk skoru
    ui['text_elements']['risk_score'] = Text(
        parent=camera.ui,
        text=f"Risk: {calculate_risk_score():.2f}",
        position=(0, 0.45),
        scale=2,
        color=color.yellow
    )

def create_portfolio_panel():
    """Portföy panelini oluştur"""
    ui['portfolio_panel'] = Entity(
        parent=ui['main_panel'],
        model='quad',
        scale=(0.5, 0.8),
        position=(-0.6, -0.05),
        color=color.rgba(0, 0, 0, 0.5)
    )
    
    # Başlık
    Text(
        parent=ui['portfolio_panel'],
        text='Portföy',
        position=(0, 0.35),
        scale=2,
        color=color.white
    )
    
    # Hisse senetleri listesi
    y_pos = 0.25
    for symbol, data in player['portfolio'].items():
        if data['shares'] > 0:
            # Hisse adı ve miktar
            Text(
                parent=ui['portfolio_panel'],
                text=f"{symbol}: {data['shares']} adet",
                position=(-0.2, y_pos),
                scale=1.2,
                color=color.white
            )
            
            # Fiyat
            Text(
                parent=ui['portfolio_panel'],
                text=f"${data['price']:,.2f}",
                position=(0.15, y_pos),
                scale=1.2,
                color=color.green if data['price'] > 0 else color.red
            )
            
            y_pos -= 0.08

def create_market_panel():
    """Market panelini oluştur"""
    ui['market_panel'] = Entity(
        parent=ui['main_panel'],
        model='quad',
        scale=(0.5, 0.8),
        position=(0, -0.05),
        color=color.rgba(0, 0, 0, 0.5)
    )
    
    # Başlık
    Text(
        parent=ui['market_panel'],
        text='Market',
        position=(0, 0.35),
        scale=2,
        color=color.white
    )
    
    # Market trendi
    ui['text_elements']['market_trend'] = Text(
        parent=ui['market_panel'],
        text=f"Trend: {market_state['trend'].upper()}",
        position=(0, 0.25),
        scale=1.5,
        color=color.yellow
    )
    
    # Volatilite
    ui['text_elements']['volatility'] = Text(
        parent=ui['market_panel'],
        text=f"Volatilite: {market_state['volatility']:.2f}",
        position=(0, 0.2),
        scale=1.2,
        color=color.azure
    )
    
    # Hisse senetleri listesi
    y_pos = 0.1
    for symbol, data in player['portfolio'].items():
        # Hisse adı ve fiyat
        Text(
            parent=ui['market_panel'],
            text=f"{symbol}: ${data['price']:,.2f}",
            position=(-0.2, y_pos),
            scale=1.2,
            color=color.white
        )
        
        # Alım butonu
        Button(
            parent=ui['market_panel'],
            text='Al',
            color=color.green,
            position=(0.1, y_pos),
            scale=(0.1, 0.04),
            on_click=Func(lambda s=symbol: buy_stock(s))
        )
        
        # Satım butonu
        Button(
            parent=ui['market_panel'],
            text='Sat',
            color=color.red,
            position=(0.2, y_pos),
            scale=(0.1, 0.04),
            on_click=Func(lambda s=symbol: sell_stock(s))
        )
        
        y_pos -= 0.08

def create_stats_panel():
    """İstatistik panelini oluştur"""
    ui['stats_panel'] = Entity(
        parent=ui['main_panel'],
        model='quad',
        scale=(0.5, 0.8),
        position=(0.6, -0.05),
        color=color.rgba(0, 0, 0, 0.5)
    )
    
    # Başlık
    Text(
        parent=ui['stats_panel'],
        text='İstatistikler',
        position=(0, 0.35),
        scale=2,
        color=color.white
    )
    
    # İstatistikler
    stats = player['stats']
    y_pos = 0.25
    
    # Toplam işlem
    Text(
        parent=ui['stats_panel'],
        text=f"Toplam İşlem: {stats['total_trades']}",
        position=(0, y_pos),
        scale=1.2,
        color=color.white
    )
    y_pos -= 0.08
    
    # Başarılı işlemler
    Text(
        parent=ui['stats_panel'],
        text=f"Başarılı: {stats['successful_trades']}",
        position=(0, y_pos),
        scale=1.2,
        color=color.green
    )
    y_pos -= 0.08
    
    # Başarısız işlemler
    Text(
        parent=ui['stats_panel'],
        text=f"Başarısız: {stats['failed_trades']}",
        position=(0, y_pos),
        scale=1.2,
        color=color.red
    )
    y_pos -= 0.08
    
    # Toplam kâr
    Text(
        parent=ui['stats_panel'],
        text=f"Toplam Kâr: ${stats['total_profit']:,.2f}",
        position=(0, y_pos),
        scale=1.2,
        color=color.green
    )
    y_pos -= 0.08
    
    # Toplam zarar
    Text(
        parent=ui['stats_panel'],
        text=f"Toplam Zarar: ${stats['total_loss']:,.2f}",
        position=(0, y_pos),
        scale=1.2,
        color=color.red
    )

def toggle_menu():
    """Menüyü aç/kapat"""
    if not ui['menu_panel']:
        create_menu()
    else:
        destroy(ui['menu_panel'])
        ui['menu_panel'] = None

def create_menu():
    """Menü panelini oluştur"""
    ui['menu_panel'] = Entity(
        parent=camera.ui,
        model='quad',
        scale=(0.4, 0.6),
        position=(0, 0),
        color=color.rgba(0, 0, 0, 0.9)
    )
    
    # Başlık
    Text(
        parent=ui['menu_panel'],
        text='Menü',
        position=(0, 0.25),
        scale=2,
        color=color.white
    )
    
    # Kaydet butonu
    Button(
        parent=ui['menu_panel'],
        text='Kaydet',
        color=color.azure,
        position=(0, 0.1),
        scale=(0.3, 0.05),
        on_click=Func(save_game)
    )
    
    # Yükle butonu
    Button(
        parent=ui['menu_panel'],
        text='Yükle',
        color=color.azure,
        position=(0, 0),
        scale=(0.3, 0.05),
        on_click=Func(load_game)
    )
    
    # Ayarlar butonu
    Button(
        parent=ui['menu_panel'],
        text='Ayarlar',
        color=color.azure,
        position=(0, -0.1),
        scale=(0.3, 0.05),
        on_click=Func(show_settings)
    )
    
    # Çıkış butonu
    Button(
        parent=ui['menu_panel'],
        text='Çıkış',
        color=color.red,
        position=(0, -0.2),
        scale=(0.3, 0.05),
        on_click=Func(quit_game)
    )

def show_settings():
    """Ayarlar menüsünü göster"""
    # Mevcut menüyü kapat
    destroy(ui['menu_panel'])
    ui['menu_panel'] = None
    
    # Ayarlar paneli
    ui['settings_panel'] = Entity(
        parent=camera.ui,
        model='quad',
        scale=(0.4, 0.6),
        position=(0, 0),
        color=color.rgba(0, 0, 0, 0.9)
    )
    
    # Başlık
    Text(
        parent=ui['settings_panel'],
        text='Ayarlar',
        position=(0, 0.25),
        scale=2,
        color=color.white
    )
    
    # Ses ayarı
    Button(
        parent=ui['settings_panel'],
        text=f"Ses: {'Açık' if game_settings['sound_enabled'] else 'Kapalı'}",
        color=color.azure,
        position=(0, 0.1),
        scale=(0.3, 0.05),
        on_click=Func(toggle_sound)
    )
    
    # Müzik ayarı
    Button(
        parent=ui['settings_panel'],
        text=f"Müzik: {'Açık' if game_settings['music_enabled'] else 'Kapalı'}",
        color=color.azure,
        position=(0, 0),
        scale=(0.3, 0.05),
        on_click=Func(toggle_music)
    )
    
    # Tam ekran ayarı
    Button(
        parent=ui['settings_panel'],
        text=f"Tam Ekran: {'Açık' if game_settings['fullscreen'] else 'Kapalı'}",
        color=color.azure,
        position=(0, -0.1),
        scale=(0.3, 0.05),
        on_click=Func(toggle_fullscreen)
    )
    
    # Geri butonu
    Button(
        parent=ui['settings_panel'],
        text='Geri',
        color=color.red,
        position=(0, -0.2),
        scale=(0.3, 0.05),
        on_click=Func(lambda: (destroy(ui['settings_panel']), create_menu()))
    )

def toggle_sound():
    """Ses ayarını değiştir"""
    game_settings['sound_enabled'] = not game_settings['sound_enabled']
    show_settings()  # Ayarlar menüsünü yenile

def toggle_music():
    """Müzik ayarını değiştir"""
    game_settings['music_enabled'] = not game_settings['music_enabled']
    show_settings()  # Ayarlar menüsünü yenile

def toggle_fullscreen():
    """Tam ekran ayarını değiştir"""
    game_settings['fullscreen'] = not game_settings['fullscreen']
    window.fullscreen = game_settings['fullscreen']
    show_settings()  # Ayarlar menüsünü yenile

def start_tutorial():
    """Eğitim modunu başlat"""
    tutorial_steps = [
        {
            'title': 'Hoş Geldiniz!',
            'description': 'FinAsis finansal eğitim simülasyonuna hoş geldiniz. Size temel özellikleri tanıtacağım.',
            'position': (0, 0)
        },
        {
            'title': 'Portföy Paneli',
            'description': 'Bu panel sahip olduğunuz hisse senetlerini gösterir.',
            'position': (-0.65, 0)
        },
        {
            'title': 'Market Paneli',
            'description': 'Bu panel piyasadaki hisse senetlerini ve fiyatlarını gösterir.',
            'position': (0, 0)
        },
        {
            'title': 'İstatistik Paneli',
            'description': 'Bu panel trading performansınızı gösterir.',
            'position': (0.65, 0)
        }
    ]
    
    # Tutorial paneli
    tutorial_panel = Entity(
        parent=camera.ui,
        model='quad',
        scale=(0.4, 0.2),
        color=color.rgba(0, 0, 0, 0.9)
    )
    
    current_step = 0
    
    def show_step():
        nonlocal current_step
        step = tutorial_steps[current_step]
        
        # Panel pozisyonu
        tutorial_panel.position = step['position']
        
        # Başlık
        if hasattr(tutorial_panel, 'title'):
            destroy(tutorial_panel.title)
        tutorial_panel.title = Text(
            parent=tutorial_panel,
            text=step['title'],
            position=(0, 0.05),
            scale=1.5,
            color=color.yellow
        )
        
        # Açıklama
        if hasattr(tutorial_panel, 'description'):
            destroy(tutorial_panel.description)
        tutorial_panel.description = Text(
            parent=tutorial_panel,
            text=step['description'],
            position=(0, -0.02),
            scale=1,
            color=color.white
        )
        
        # İleri butonu
        if hasattr(tutorial_panel, 'next_button'):
            destroy(tutorial_panel.next_button)
        tutorial_panel.next_button = Button(
            parent=tutorial_panel,
            text='İleri' if current_step < len(tutorial_steps) - 1 else 'Bitir',
            position=(0.1, -0.07),
            scale=(0.2, 0.05),
            color=color.azure,
            on_click=next_step
        )
    
    def next_step():
        nonlocal current_step
        current_step += 1
        if current_step < len(tutorial_steps):
            show_step()
        else:
            # Tutorial'ı bitir
            destroy(tutorial_panel)
            player['tutorial_progress']['basic_trading'] = True
            save_game()
    
    # İlk adımı göster
    show_step()

def save_game():
    """Oyun durumunu kaydet"""
    try:
        # Kaydedilecek verileri hazırla
        save_data = {
            'player': player,
            'market_state': market_state,
            'quest_system': quest_system,
            'game_settings': game_settings,
            'save_time': datetime.now().isoformat()
        }
        
        # datetime nesnelerini ISO formatına dönüştür
        def convert_datetime(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            return obj
        
        # Verileri JSON formatında kaydet
        with open('save_game.json', 'w', encoding='utf-8') as f:
            json.dump(save_data, f, default=convert_datetime, ensure_ascii=False, indent=4)
            
        show_notification('Oyun kaydedildi!', color.green)
    except Exception as e:
        show_notification(f'Kayıt hatası: {str(e)}', color.red)

def load_game():
    """Kaydedilmiş oyun durumunu yükle"""
    try:
        # JSON dosyasını oku
        with open('save_game.json', 'r', encoding='utf-8') as f:
            save_data = json.load(f)
        
        # datetime string'lerini datetime nesnelerine dönüştür
        def parse_datetime(obj):
            for key, value in obj.items():
                if isinstance(value, str) and 'T' in value:
                    try:
                        obj[key] = datetime.fromisoformat(value)
                    except ValueError:
                        pass
                elif isinstance(value, dict):
                    parse_datetime(value)
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            parse_datetime(item)
            return obj
        
        # Verileri yükle
        global player, market_state, quest_system, game_settings
        player = parse_datetime(save_data['player'])
        market_state = parse_datetime(save_data['market_state'])
        quest_system = parse_datetime(save_data['quest_system'])
        game_settings = save_data['game_settings']
        
        show_notification('Oyun yüklendi!', color.green)
    except FileNotFoundError:
        show_notification('Kayıtlı oyun bulunamadı.', color.yellow)
    except Exception as e:
        show_notification(f'Yükleme hatası: {str(e)}', color.red)

def show_notification(message, color=color.white):
    """Bildirim göster"""
    notification = Text(
        text=message,
        position=(0, 0.4),
        scale=2,
        color=color
    )
    destroy(notification, delay=3)

def auto_save():
    """Otomatik kayıt"""
    current_time = datetime.now()
    if not hasattr(auto_save, 'last_save'):
        auto_save.last_save = current_time
    
    if (current_time - auto_save.last_save).seconds >= game_settings['save_interval']:
        save_game()
        auto_save.last_save = current_time

def quit_game():
    """Oyundan çık"""
    # Oyunu kaydet
    save_game()
    
    # Pencereyi kapat
    application.quit()

def initialize_quest_system():
    """Görev sistemini başlat"""
    # Günlük görevleri yükle
    daily_quests = ['daily_trade', 'daily_profit', 'daily_diversity']
    for quest_id in daily_quests:
        if quest_id in quest_definitions:
            quest_system['daily_quests'].append(quest_definitions[quest_id])
    
    # Haftalık görevleri yükle
    weekly_quests = ['weekly_growth', 'weekly_trades', 'weekly_risk']
    for quest_id in weekly_quests:
        if quest_id in quest_definitions:
            quest_system['weekly_quests'].append(quest_definitions[quest_id])
    
    # Başarı görevlerini yükle
    achievement_quests = ['achievement_portfolio', 'achievement_diversity', 'achievement_debt']
    for quest_id in achievement_quests:
        if quest_id in quest_definitions:
            quest_system['achievement_quests'].append(quest_definitions[quest_id])
    
    # Eğitim görevlerini yükle
    tutorial_quests = ['tutorial_buy', 'tutorial_sell', 'tutorial_diversity']
    for quest_id in tutorial_quests:
        if quest_id in quest_definitions:
            quest_system['tutorial_quests'].append(quest_definitions[quest_id])
    
    # Aktif görevleri belirle
    assign_daily_quests()
    assign_weekly_quests()
    
    # Eğitim görevlerini aktif görevlere ekle
    for quest in quest_system['tutorial_quests']:
        if quest['id'] not in player['completed_quests']:
            player['active_quests'].append(quest['id'])
            player['quest_progress'][quest['id']] = 0
    
    # Başarı görevlerini aktif görevlere ekle
    for quest in quest_system['achievement_quests']:
        if quest['id'] not in player['completed_quests']:
            player['active_quests'].append(quest['id'])
            player['quest_progress'][quest['id']] = 0
    
    # Görev UI'ını oluştur
    create_quest_ui()

def assign_daily_quests():
    """Günlük görevleri ata"""
    # Günlük görevleri sıfırla
    player['active_quests'] = [q for q in player['active_quests'] if q not in [d['id'] for d in quest_system['daily_quests']]]
    
    # Rastgele 2 günlük görev seç
    selected_quests = random.sample(quest_system['daily_quests'], min(2, len(quest_system['daily_quests'])))
    
    # Seçilen görevleri aktif görevlere ekle
    for quest in selected_quests:
        player['active_quests'].append(quest['id'])
        player['quest_progress'][quest['id']] = 0

def assign_weekly_quests():
    """Haftalık görevleri ata"""
    # Haftalık görevleri sıfırla
    player['active_quests'] = [q for q in player['active_quests'] if q not in [w['id'] for w in quest_system['weekly_quests']]]
    
    # Rastgele 2 haftalık görev seç
    selected_quests = random.sample(quest_system['weekly_quests'], min(2, len(quest_system['weekly_quests'])))
    
    # Seçilen görevleri aktif görevlere ekle
    for quest in selected_quests:
        player['active_quests'].append(quest['id'])
        player['quest_progress'][quest['id']] = 0

def check_quest_completion():
    """Görev tamamlanma durumunu kontrol et"""
    completed_quests = []
    
    for quest_id in player['active_quests']:
        if quest_id in quest_definitions:
            quest = quest_definitions[quest_id]
            
            # Görev tamamlandı mı kontrol et
            if quest['check_completion']():
                # Görevi tamamlandı olarak işaretle
                completed_quests.append(quest_id)
                
                # Ödülleri ver
                give_quest_rewards(quest)
                
                # Tamamlanan görevi göster
                show_quest_completion(quest)
    
    # Tamamlanan görevleri aktif görevlerden çıkar
    for quest_id in completed_quests:
        player['active_quests'].remove(quest_id)
        player['completed_quests'].append(quest_id)
    
    # Görev UI'ını güncelle
    update_quest_ui()

def give_quest_rewards(quest):
    """Görev ödüllerini ver"""
    reward = quest['reward']
    
    # Para ödülü
    if 'money' in reward:
        player['money'] += reward['money']
    
    # Deneyim ödülü
    if 'experience' in reward:
        player['experience']['current_xp'] += reward['experience']
        player['experience']['total_xp'] += reward['experience']
        
        # Seviye atlama kontrolü
        while player['experience']['current_xp'] >= player['experience']['next_level_xp']:
            player['experience']['current_xp'] -= player['experience']['next_level_xp']
            player['experience']['level'] += 1
            player['experience']['next_level_xp'] = calculate_next_level_xp(player['experience']['level'])
            show_level_up()
    
    # Başarı ödülü
    if 'achievement' in reward:
        if reward['achievement'] not in player['achievements']:
            player['achievements'].append(reward['achievement'])

def show_quest_completion(quest):
    """Görev tamamlanma bildirimini göster"""
    # Ana bildirim metni
    completion_text = Text(
        text=f"Görev Tamamlandı: {quest['title']}",
        position=(0, 0.6),
        scale=2,
        color=color.gold
    )
    
    # Ödül detayları
    reward_text = None
    if 'money' in quest['reward']:
        reward_text = Text(
            text=f"Ödül: +${quest['reward']['money']:,.2f}",
            position=(0, 0.5),
            scale=1.5,
            color=color.green
        )
    
    # Metinleri belirli süre sonra kaldır
    destroy(completion_text, delay=4)
    if reward_text:
        destroy(reward_text, delay=4)

def show_level_up():
    """Seviye atlama bildirimini göster"""
    level_text = Text(
        text=f"Seviye Atladınız! Yeni Seviye: {player['experience']['level']}",
        position=(0, 0.4),
        scale=2,
        color=color.yellow
    )
    destroy(level_text, delay=4)

def calculate_next_level_xp(current_level):
    """Sonraki seviye için gereken XP'yi hesapla"""
    return int(1000 * (1.5 ** (current_level - 1)))

def create_quest_ui():
    """Görev UI'ını oluştur"""
    # Görev paneli
    quest_ui['panel'] = Entity(
        parent=camera.ui,
        model='quad',
        scale=(0.8, 0.6),
        position=(0, 0),
        color=color.rgba(0, 0, 0, 0.7),
        visible=False
    )
    
    # Görev başlığı
    Text(
        parent=quest_ui['panel'],
        text='Görevler',
        position=(0, 0.25),
        scale=2,
        color=color.white
    )
    
    # Aktif görevler başlığı
    quest_ui['active_quests_text'] = Text(
        parent=quest_ui['panel'],
        text='Aktif Görevler:',
        position=(-0.35, 0.15),
        scale=1.5,
        color=color.white
    )
    
    # Tamamlanan görevler başlığı
    quest_ui['completed_quests_text'] = Text(
        parent=quest_ui['panel'],
        text='Tamamlanan Görevler:',
        position=(-0.35, -0.15),
        scale=1.5,
        color=color.white
    )
    
    # Görev kapatma butonu
    Button(
        parent=quest_ui['panel'],
        text='Kapat',
        color=color.red,
        position=(0, -0.25),
        scale=(0.2, 0.05),
        on_click=Func(lambda: setattr(quest_ui['panel'], 'visible', False))
    )
    
    # Görev butonu
    Button(
        parent=camera.ui,
        text='Görevler',
        color=color.azure,
        position=(0.7, 0.4),
        scale=(0.2, 0.05),
        on_click=Func(lambda: setattr(quest_ui['panel'], 'visible', True))
    )
    
    # Görev UI'ını güncelle
    update_quest_ui()

def update_quest_ui():
    """Görev UI'ını güncelle"""
    # Mevcut görev öğelerini temizle
    for item in quest_ui['quest_items']:
        destroy(item)
    quest_ui['quest_items'] = []
    
    # Aktif görevleri göster
    y_position = 0.1
    for quest_id in player['active_quests']:
        if quest_id in quest_definitions:
            quest = quest_definitions[quest_id]
            
            # Görev başlığı
            quest_ui['quest_items'].append(
                Text(
                    parent=quest_ui['panel'],
                    text=quest['title'],
                    position=(-0.3, y_position),
                    scale=1.2,
                    color=color.white
                )
            )
            
            # Görev açıklaması
            quest_ui['quest_items'].append(
                Text(
                    parent=quest_ui['panel'],
                    text=quest['description'],
                    position=(-0.3, y_position - 0.05),
                    scale=0.8,
                    color=color.light_gray
                )
            )
            
            # Görev ödülü
            reward_text = f"Ödül: ${quest['reward']['money']:,.2f}"
            quest_ui['quest_items'].append(
                Text(
                    parent=quest_ui['panel'],
                    text=reward_text,
                    position=(-0.3, y_position - 0.1),
                    scale=0.8,
                    color=color.gold
                )
            )
            
            y_position -= 0.15
    
    # Tamamlanan görevleri göster
    y_position = -0.2
    for quest_id in player['completed_quests'][-5:]:  # Son 5 tamamlanan görevi göster
        if quest_id in quest_definitions:
            quest = quest_definitions[quest_id]
            
            # Görev başlığı
            quest_ui['quest_items'].append(
                Text(
                    parent=quest_ui['panel'],
                    text=quest['title'],
                    position=(-0.3, y_position),
                    scale=1.2,
                    color=color.light_gray
                )
            )
            
            # Tamamlandı işareti
            quest_ui['quest_items'].append(
                Text(
                    parent=quest_ui['panel'],
                    text="✓ Tamamlandı",
                    position=(0.2, y_position),
                    scale=0.8,
                    color=color.green
                )
            )
            
            y_position -= 0.1

def calculate_daily_profit():
    """Günlük kârı hesapla"""
    today = datetime.now().date()
    today_trades = [t for t in player['trading_history'] if t['timestamp'].date() == today]
    
    profit = 0
    for trade in today_trades:
        if trade['type'] == 'sell':
            # Satış işleminden kâr hesapla
            buy_trades = [t for t in player['trading_history'] if t['stock'] == trade['stock'] and t['type'] == 'buy' and t['timestamp'].date() <= today]
            if buy_trades:
                # En eski alım fiyatını bul
                oldest_buy = min(buy_trades, key=lambda t: t['timestamp'])
                buy_price = oldest_buy['price']
                sell_price = trade['price']
                profit += (sell_price - buy_price) * trade['amount']
    
    return profit

def calculate_weekly_growth():
    """Haftalık büyümeyi hesapla"""
    # Başlangıç portföy değeri (1 hafta önce)
    week_ago = datetime.now() - timedelta(days=7)
    week_ago_trades = [t for t in player['trading_history'] if t['timestamp'] <= week_ago]
    
    # Şu anki portföy değeri
    current_value = calculate_portfolio_value()
    
    # Haftalık büyüme oranı
    if current_value > 0:
        return (current_value / 100000) - 1  # Başlangıç değerine göre büyüme
    return 0

def update_market_state():
    """Piyasa durumunu güncelle"""
    current_time = datetime.now()
    if (current_time - market_state['last_update']).seconds >= 30:  # Her 30 saniyede bir güncelle
        # Piyasa trendini güncelle
        trend_chance = random.random()
        if trend_chance < 0.4:
            market_state['trend'] = 'stable'
        elif trend_chance < 0.7:
            market_state['trend'] = 'bull'
        else:
            market_state['trend'] = 'bear'
        
        # Volatiliteyi güncelle
        market_state['volatility'] = random.uniform(0.3, 0.8)
        
        # Piyasa olayları oluştur
        if random.random() < 0.2:  # %20 şans
            event = generate_market_event()
            market_state['market_events'].append(event)
            show_market_event(event)
            apply_market_event(event)
        
        # Oyuncuya özel olaylar oluştur
        if random.random() < 0.15:  # %15 şans
            player_event = generate_player_event()
            if player_event:
                show_player_event(player_event)
                apply_player_event(player_event)
        
        # Görev tamamlanma durumunu kontrol et
        check_quest_completion()
        
        market_state['last_update'] = current_time

def update():
    """Ana oyun döngüsü"""
    # Piyasa güncellemesi
    update_market()
    
    # UI güncellemesi
    update_ui()
    
    # Görev kontrolü
    check_quests()
    
    # Otomatik kayıt
    if game_settings['auto_save']:
        auto_save()

def update_market():
    """Piyasa durumunu güncelle"""
    current_time = datetime.now()
    
    # Piyasa güncellemesi
    if (current_time - market_state['last_update']).seconds >= game_settings['market_update_interval']:
        # Trend güncelleme
        update_market_trend()
        
        # Fiyat güncelleme
        update_stock_prices()
        
        # Olay kontrolü
        check_market_events()
        
        market_state['last_update'] = current_time

def update_market_trend():
    """Piyasa trendini güncelle"""
    trend_chance = random.random()
    
    # Zorluk seviyesine göre trend olasılıkları
    if game_settings['difficulty'] == 'easy':
        if trend_chance < 0.5:  # %50 şans
            market_state['trend'] = 'bull'
        elif trend_chance < 0.8:  # %30 şans
            market_state['trend'] = 'stable'
        else:  # %20 şans
            market_state['trend'] = 'bear'
    elif game_settings['difficulty'] == 'normal':
        if trend_chance < 0.4:  # %40 şans
            market_state['trend'] = 'bull'
        elif trend_chance < 0.7:  # %30 şans
            market_state['trend'] = 'stable'
        else:  # %30 şans
            market_state['trend'] = 'bear'
    else:  # hard
        if trend_chance < 0.3:  # %30 şans
            market_state['trend'] = 'bull'
        elif trend_chance < 0.5:  # %20 şans
            market_state['trend'] = 'stable'
        else:  # %50 şans
            market_state['trend'] = 'bear'
    
    # Volatilite güncelleme
    market_state['volatility'] = random.uniform(
        0.2 if game_settings['difficulty'] == 'easy' else 0.3 if game_settings['difficulty'] == 'normal' else 0.4,
        0.5 if game_settings['difficulty'] == 'easy' else 0.7 if game_settings['difficulty'] == 'normal' else 0.9
    )

def update_stock_prices():
    """Hisse senedi fiyatlarını güncelle"""
    for symbol, data in player['portfolio'].items():
        base_price = data['price']
        
        # Trend etkisi
        trend_effect = {
            'bull': random.uniform(0.001, 0.01),
            'stable': random.uniform(-0.003, 0.003),
            'bear': random.uniform(-0.01, -0.001)
        }[market_state['trend']]
        
        # Sektör etkisi
        sector_effect = calculate_sector_effect(data['sector'])
        
        # Volatilite etkisi
        volatility_effect = random.uniform(-market_state['volatility'], market_state['volatility'])
        
        # Toplam değişim
        total_change = trend_effect + sector_effect + volatility_effect
        
        # Zorluk seviyesine göre değişim sınırlaması
        if game_settings['difficulty'] == 'easy':
            total_change = max(-0.05, min(0.05, total_change))
        elif game_settings['difficulty'] == 'normal':
            total_change = max(-0.1, min(0.1, total_change))
        else:  # hard
            total_change = max(-0.15, min(0.15, total_change))
        
        # Yeni fiyat
        new_price = base_price * (1 + total_change)
        player['portfolio'][symbol]['price'] = max(0.01, new_price)

def calculate_sector_effect(sector):
    """Sektör bazlı fiyat etkisini hesapla"""
    sector_trends = {
        'tech': random.uniform(-0.005, 0.008),
        'auto': random.uniform(-0.004, 0.006),
        'retail': random.uniform(-0.003, 0.005),
        'media': random.uniform(-0.004, 0.007),
        'finance': random.uniform(-0.003, 0.004)
    }
    return sector_trends.get(sector, 0)

def check_market_events():
    """Piyasa olaylarını kontrol et"""
    if random.random() < game_settings['event_chance']:
        event = generate_market_event()
        if event:
            market_state['market_events'].append(event)
            apply_market_event(event)
            show_market_event(event)

def generate_market_event():
    """Piyasa olayı oluştur"""
    event_types = {
        'global': [
            {
                'title': 'Küresel Ekonomik Büyüme',
                'description': 'Küresel ekonomik büyüme beklentileri yükseldi!',
                'effect': {'market_trend': 'bull', 'volatility': -0.1},
                'duration': 300,
                'probability': 0.2
            },
            {
                'title': 'Ekonomik Kriz',
                'description': 'Küresel ekonomik kriz endişeleri artıyor!',
                'effect': {'market_trend': 'bear', 'volatility': 0.2},
                'duration': 300,
                'probability': 0.1
            }
        ],
        'sector': [
            {
                'title': 'Teknoloji Atılımı',
                'description': 'Yeni teknolojik gelişmeler sektörü hareketlendirdi!',
                'effect': {'sector': 'tech', 'change': 0.05},
                'duration': 180,
                'probability': 0.15
            },
            {
                'title': 'Otomotiv Krizi',
                'description': 'Tedarik zinciri sorunları otomotiv sektörünü vuruyor!',
                'effect': {'sector': 'auto', 'change': -0.05},
                'duration': 180,
                'probability': 0.15
            }
        ],
        'company': [
            {
                'title': 'Ürün Lansmanı',
                'description': 'AAPL yeni ürünlerini tanıttı!',
                'effect': {'symbol': 'AAPL', 'change': 0.08},
                'duration': 120,
                'probability': 0.2
            },
            {
                'title': 'CEO İstifası',
                'description': 'TSLA CEO\'su istifa etti!',
                'effect': {'symbol': 'TSLA', 'change': -0.08},
                'duration': 120,
                'probability': 0.1
            }
        ]
    }
    
    # Olay türü seç
    event_type = random.choice(list(event_types.keys()))
    events = event_types[event_type]
    
    # Olasılık kontrolü
    for event in events:
        if random.random() < event['probability']:
            return event
    
    return None

def apply_market_event(event):
    """Piyasa olayını uygula"""
    effect = event['effect']
    
    # Piyasa trendi etkisi
    if 'market_trend' in effect:
        market_state['trend'] = effect['market_trend']
    
    # Volatilite etkisi
    if 'volatility' in effect:
        market_state['volatility'] = max(0.1, min(1.0, market_state['volatility'] + effect['volatility']))
    
    # Sektör etkisi
    if 'sector' in effect:
        for symbol, data in player['portfolio'].items():
            if data['sector'] == effect['sector']:
                data['price'] *= (1 + effect['change'])
    
    # Şirket etkisi
    if 'symbol' in effect:
        if effect['symbol'] in player['portfolio']:
            player['portfolio'][effect['symbol']]['price'] *= (1 + effect['change'])

def show_market_event(event):
    """Piyasa olayını göster"""
    # Bildirim paneli
    notification = Entity(
        parent=camera.ui,
        model='quad',
        scale=(0.6, 0.2),
        position=(0, 0.3),
        color=color.rgba(0, 0, 0, 0.9)
    )
    
    # Başlık
    title_text = Text(
        parent=notification,
        text=event['title'],
        position=(0, 0.05),
        scale=1.5,
        color=color.yellow
    )
    
    # Açıklama
    desc_text = Text(
        parent=notification,
        text=event['description'],
        position=(0, -0.02),
        scale=1.2,
        color=color.white
    )
    
    # Efekt açıklaması
    effect = event['effect']
    effect_text = ""
    
    if 'market_trend' in effect:
        effect_text = "Piyasa trendi değişti!"
    elif 'sector' in effect:
        effect_text = f"{effect['sector'].upper()} sektörü etkilendi!"
    elif 'symbol' in effect:
        effect_text = f"{effect['symbol']} hissesi etkilendi!"
    
    Text(
        parent=notification,
        text=effect_text,
        position=(0, -0.08),
        scale=1,
        color=color.azure
    )
    
    # Bildirimi kaydet
    ui['notifications'].append({
        'entity': notification,
        'created_at': datetime.now(),
        'duration': 5  # 5 saniye sonra kaybolacak
    })

def calculate_portfolio_value():
    """Portföy değerini hesapla"""
    total_value = player['money']
    for symbol, data in player['portfolio'].items():
        total_value += data['shares'] * data['price']
    return total_value

def calculate_risk_score():
    """Risk skorunu hesapla"""
    # Portföy çeşitliliği (0-1 arası)
    portfolio_diversity = calculate_portfolio_diversity()
    
    # Borç/gelir oranı (0-1 arası)
    debt_to_income = calculate_debt_to_income_ratio()
    
    # Toplam risk skoru (0-1 arası)
    risk_score = (1 - portfolio_diversity) * 0.6 + debt_to_income * 0.4
    return min(max(risk_score, 0), 1)

def calculate_portfolio_diversity():
    """Portföy çeşitliliğini hesapla"""
    total_value = calculate_portfolio_value()
    if total_value == 0:
        return 0
    
    # Her sektördeki yatırım oranını hesapla
    sector_weights = {}
    for symbol, data in player['portfolio'].items():
        sector = data['sector']
        value = data['shares'] * data['price']
        sector_weights[sector] = sector_weights.get(sector, 0) + value / total_value
    
    # Herfindahl-Hirschman Index'ini hesapla (ters çevrilmiş)
    hhi = sum(weight * weight for weight in sector_weights.values())
    diversity = 1 - hhi
    return min(max(diversity, 0), 1)

def calculate_debt_to_income_ratio():
    """Borç/gelir oranını hesapla"""
    total_income = sum(t['amount'] for t in player.get('trading_history', []) 
                      if t['type'] == 'profit' and (datetime.now() - t['timestamp']).days <= 30)
    total_debt = sum(t['amount'] for t in player.get('trading_history', [])
                    if t['type'] == 'loss' and (datetime.now() - t['timestamp']).days <= 30)
    
    if total_income == 0:
        return 1 if total_debt > 0 else 0
    
    ratio = total_debt / total_income
    return min(max(ratio, 0), 1)

def update_ui():
    """UI'ı güncelle"""
    # Para ve portföy değerini güncelle
    ui['text_elements']['money'].text = f"Para: ${player['money']:,.2f}"
    ui['text_elements']['portfolio_value'].text = f"Portföy: ${calculate_portfolio_value():,.2f}"
    ui['text_elements']['risk_score'].text = f"Risk: {calculate_risk_score():.2f}"
    
    # Hisse senedi fiyatlarını güncelle
    for symbol, data in player['portfolio'].items():
        if symbol in ui['text_elements']:
            ui['text_elements'][symbol].text = f"{symbol}: ${data['price']:,.2f}"
    
    # Hisse senedi butonlarını güncelle
    update_stock_buttons()
    
    # Görevleri güncelle
    update_quest_ui()
    
    # Bildirimleri güncelle
    update_notifications()

def update_stock_buttons():
    """Hisse senedi butonlarını güncelle"""
    for symbol, data in player['portfolio'].items():
        # Alım butonu
        if symbol + '_buy' in ui['buttons']:
            ui['buttons'][symbol + '_buy'].enabled = player['money'] >= data['price']
        
        # Satım butonu
        if symbol + '_sell' in ui['buttons']:
            ui['buttons'][symbol + '_sell'].enabled = data['shares'] > 0

def update_notifications():
    """Bildirimleri güncelle"""
    current_time = datetime.now()
    
    # Süresi dolmuş bildirimleri kaldır
    ui['notifications'] = [n for n in ui['notifications'] 
                         if (current_time - n['timestamp']).seconds < 5]
    
    # Bildirimleri göster
    for i, notification in enumerate(ui['notifications']):
        if 'text' in notification:
            notification['text'].y = -0.3 - i * 0.1

def buy_stock(symbol):
    """Hisse senedi satın al"""
    stock = player['portfolio'][symbol]
    price = stock['price']
    
    # Yeterli para var mı kontrol et
    if player['money'] < price:
        show_notification('Yeterli paranız yok!', color.red)
        return
    
    # İşlemi gerçekleştir
    player['money'] -= price
    stock['shares'] += 1
    
    # İşlem kaydını tut
    trade = {
        'type': 'buy',
        'symbol': symbol,
        'price': price,
        'shares': 1,
        'total': price,
        'timestamp': datetime.now()
    }
    player['trading_history'].append(trade)
    
    # İstatistikleri güncelle
    player['stats']['total_trades'] += 1
    
    # Bildirimi göster
    show_notification(f'{symbol} hissesinden 1 adet satın alındı.', color.green)
    
    # UI'ı güncelle
    update_ui()

def sell_stock(symbol):
    """Hisse senedi sat"""
    stock = player['portfolio'][symbol]
    price = stock['price']
    
    # Yeterli hisse var mı kontrol et
    if stock['shares'] <= 0:
        show_notification('Yeterli hisseniz yok!', color.red)
        return
    
    # İşlemi gerçekleştir
    player['money'] += price
    stock['shares'] -= 1
    
    # İşlem kaydını tut
    trade = {
        'type': 'sell',
        'symbol': symbol,
        'price': price,
        'shares': 1,
        'total': price,
        'timestamp': datetime.now()
    }
    player['trading_history'].append(trade)
    
    # İstatistikleri güncelle
    player['stats']['total_trades'] += 1
    
    # Bildirimi göster
    show_notification(f'{symbol} hissesinden 1 adet satıldı.', color.green)
    
    # UI'ı güncelle
    update_ui()

def check_quests():
    """Görevleri kontrol et"""
    # Günlük görevleri kontrol et
    for quest in quest_system['daily_quests']:
        if not quest.get('completed', False) and quest_definitions[quest['id']]['check_completion']():
            quest['completed'] = True
            give_quest_rewards(quest)
            show_quest_completion(quest)
    
    # Haftalık görevleri kontrol et
    for quest in quest_system['weekly_quests']:
        if not quest.get('completed', False) and quest_definitions[quest['id']]['check_completion']():
            quest['completed'] = True
            give_quest_rewards(quest)
            show_quest_completion(quest)
    
    # Başarı görevlerini kontrol et
    for quest in quest_system['achievement_quests']:
        if not quest.get('completed', False) and quest_definitions[quest['id']]['check_completion']():
            quest['completed'] = True
            give_quest_rewards(quest)
            show_quest_completion(quest)
            
    # Öğretici görevleri kontrol et
    for quest in quest_system['tutorial_quests']:
        if not quest.get('completed', False) and quest_definitions[quest['id']]['check_completion']():
            quest['completed'] = True
            give_quest_rewards(quest)
            show_quest_completion(quest)
            
    # Seviye atlamayı kontrol et
    check_level_up()

def check_level_up():
    """Seviye atlamayı kontrol et"""
    while player['experience']['current_xp'] >= player['experience']['next_level_xp']:
        # Seviye atla
        player['experience']['level'] += 1
        player['experience']['current_xp'] -= player['experience']['next_level_xp']
        player['experience']['next_level_xp'] = calculate_next_level_xp(player['experience']['level'])
        
        # Seviye atlama ödüllerini ver
        rewards = {
            'money': 1000 * player['experience']['level'],
            'experience': 0
        }
        give_quest_rewards({'reward': rewards})
        
        # Seviye atlama bildirimini göster
        show_level_up()

class CharacterSelection:
    def __init__(self):
        self.characters = self.load_characters()
        self.selected_character = None
        self.ui_elements = {}
        
    def load_characters(self):
        with open('characters.json', 'r', encoding='utf-8') as f:
            return json.load(f)['characters']
            
    def create_ui(self):
        # Karakter seçim paneli
        self.ui_elements['panel'] = Entity(
            model='quad',
            scale=(1, 1),
            color=color.black90,
            position=(0, 0, -1)
        )
        
        # Karakter kartları
        for i, char in enumerate(self.characters):
            card = Entity(
                model='quad',
                scale=(0.3, 0.4),
                color=color.white,
                position=(-0.5 + i * 0.3, 0, -0.9),
                parent=self.ui_elements['panel']
            )
            
            # Karakter bilgileri
            Text(
                text=char['name'],
                position=(-0.5 + i * 0.3, 0.1, -0.8),
                scale=2,
                parent=self.ui_elements['panel']
            )
            
            Text(
                text=char['description'],
                position=(-0.5 + i * 0.3, 0, -0.8),
                scale=1,
                parent=self.ui_elements['panel']
            )
            
            # Seçim butonu
            Button(
                text='Seç',
                position=(-0.5 + i * 0.3, -0.1, -0.8),
                scale=(0.1, 0.05),
                on_click=Func(self.select_character, char),
                parent=self.ui_elements['panel']
            )
            
    def select_character(self, character):
        self.selected_character = character
        # Oyuncu verilerini güncelle
        player['money'] = character['starting_money']
        player['stats']['risk_tolerance'] = character['advantages']['risk_tolerance']
        # Karakter seçim ekranını kapat
        destroy(self.ui_elements['panel'])
        # Oyunu başlat
        start_game()

class MissionSystem:
    def __init__(self):
        self.levels = self.load_missions()
        self.current_level = 1
        self.current_mission = None
        self.ui_elements = {}
        
    def load_missions(self):
        with open('missions.json', 'r', encoding='utf-8') as f:
            return json.load(f)['levels']
            
    def create_mission_ui(self):
        # Görev paneli
        self.ui_elements['panel'] = Entity(
            model='quad',
            scale=(0.4, 0.3),
            color=color.black90,
            position=(0.7, 0.6, -1)
        )
        
        # Görev başlığı
        self.ui_elements['title'] = Text(
            text='Görevler',
            position=(0.7, 0.7, -0.9),
            scale=2,
            parent=self.ui_elements['panel']
        )
        
        # Görev listesi
        self.ui_elements['list'] = Entity(
            model='quad',
            scale=(0.35, 0.2),
            color=color.black,
            position=(0.7, 0.5, -0.9),
            parent=self.ui_elements['panel']
        )
        
    def update_mission_ui(self):
        if self.current_mission:
            level = self.levels[self.current_level - 1]
            mission = level['missions'][0]  # İlk görevi göster
            
            # Görev bilgilerini güncelle
            Text(
                text=f"Seviye: {level['name']}",
                position=(0.7, 0.6, -0.8),
                scale=1.5,
                parent=self.ui_elements['panel']
            )
            
            Text(
                text=f"Görev: {mission['title']}",
                position=(0.7, 0.5, -0.8),
                scale=1.2,
                parent=self.ui_elements['panel']
            )
            
            Text(
                text=mission['description'],
                position=(0.7, 0.4, -0.8),
                scale=0.8,
                parent=self.ui_elements['panel']
            )
            
    def check_mission_completion(self):
        if self.current_mission:
            requirements = self.current_mission['requirements']
            completed = True
            
            for req, value in requirements.items():
                if req == 'company_created':
                    completed &= player['company'] is not None
                elif req == 'initial_capital':
                    completed &= player['money'] >= value
                # Diğer gereksinimler için kontroller...
                
            if completed:
                self.complete_mission()
                
    def complete_mission(self):
        if self.current_mission is None:
            return
            
        if isinstance(self.current_mission, dict) and 'rewards' in self.current_mission:
            rewards = self.current_mission['rewards']
            player['money'] += rewards.get('money', 0)
            player['experience']['current_xp'] += rewards.get('experience', 0)
        
        # Görev tamamlandı bildirimi
        show_notification('📈 Görev Başarıyla Tamamlandı!', color.green)
        
        # Yeni görev atama
        self.assign_next_mission()
        
    def assign_next_mission(self):
        level = self.levels[self.current_level - 1]
        if len(level['missions']) > 1:
            self.current_mission = level['missions'][1]
        else:
            # Seviye tamamlandı
            self.level_up()
            
    def level_up(self):
        self.current_level += 1
        if self.current_level <= len(self.levels):
            # Yeni seviye arka planını yükle
            self.load_level_background()
            # İlk görevi ata
            self.current_mission = self.levels[self.current_level - 1]['missions'][0]
            show_notification(f'🎉 Seviye {self.current_level} Açıldı!', color.yellow)
            
    def load_level_background(self):
        level = self.levels[self.current_level - 1]
        background = level['background']
        # Arka plan değiştirme işlemi
        # ...

class BattleRoyaleMode:
    def __init__(self):
        self.players = []
        self.events = []
        self.loot_cards = []
        self.active_cards = []
        self.current_event = None
        self.match_start_time = 0
        self.match_duration = 900  # 15 dakika
        self.event_interval = 180  # 3 dakika
        self.card_spawn_interval = 60  # 1 dakika
        self.held_keys = {'w': False, 'a': False, 's': False, 'd': False, 'left mouse': False, 'right mouse': False}
        self.invoke = application.base.sequence
        self.player = None
        
        # Yeni öznitelikler
        self.last_update = time.time()
        self.update_interval = 0.016  # ~60 FPS
        self.is_paused = False
        self.is_mobile = platform.system().lower() in ['android', 'ios']
        self.ar_manager = None  # AR yöneticisi mobil platformlarda başlatılacak
        
        # Olayları ve kartları yükle
        self.load_game_data()

    def load_game_data(self):
        """Oyun verilerini yükle"""
        self.events = self.load_events()
        self.loot_cards = self.load_loot_cards()

    def load_events(self):
        """Olay verilerini yükle"""
        try:
            with open('games/ursina_game/arena_events.json', 'r', encoding='utf-8') as f:
                return json.load(f)['events']
        except (FileNotFoundError, KeyError, json.JSONDecodeError):
            return []

    def load_loot_cards(self):
        """Kart verilerini yükle"""
        try:
            with open('games/ursina_game/loot_cards.json', 'r', encoding='utf-8') as f:
                return json.load(f)['cards']
        except (FileNotFoundError, KeyError, json.JSONDecodeError):
            return []

    def alis_yap(self):
        """Alış işlemi yap"""
        if self.player and hasattr(self.player, 'money') and self.player.money >= 1000:
            self.player.money -= 1000
            return True
        return False

    def satis_yap(self):
        """Satış işlemi yap"""
        if self.player and hasattr(self.player, 'shares') and self.player.shares > 0:
            self.player.money += 1000
            self.player.shares -= 1
            return True
        return False

    def olay_guncelle(self):
        """Olayları güncelle"""
        current_time = time.time()
        for event in self.events:
            if 'start_time' in event and current_time - event['start_time'] > event.get('duration', 0):
                self.generate_new_event()

    def generate_new_event(self):
        """Yeni olay oluştur"""
        event_types = ['market_change', 'resource_discovery', 'crisis']
        new_event = {
            'type': random.choice(event_types),
            'start_time': time.time(),
            'duration': random.randint(30, 180)
        }
        self.events.append(new_event)

    def update(self):
        """Oyun durumunu güncelle"""
        current_time = time.time()
        if current_time - self.last_update < self.update_interval:
            return
        self.last_update = current_time
        
        if self.is_paused:
            return
            
        # Oyun güncellemeleri
        if self.held_keys['left mouse']:
            self.alis_yap()
            
        if self.held_keys['right mouse']:
            self.satis_yap()
            
        # AR güncellemeleri
        if self.is_mobile and self.ar_manager:
            self.ar_manager.ar_nesne_guncelle()
            
        # Olay güncellemeleri
        self.olay_guncelle()

class FastFinanceTournament:
    def __init__(self):
        self.scenarios = self.load_scenarios()
        self.current_scenario = None
        self.player_score = 0
        self.scenario_start_time = 0
        self.scenario_duration = 300  # 5 dakika
        
    def load_scenarios(self):
        with open('short_matches.json', 'r', encoding='utf-8') as f:
            return json.load(f)['scenarios']
            
    def start_scenario(self, scenario_id):
        self.current_scenario = next(s for s in self.scenarios if s['id'] == scenario_id)
        self.scenario_start_time = time.time()
        
    def submit_answer(self, option_id):
        if self.current_scenario is None:
            return False
            
        if isinstance(self.current_scenario, dict) and 'correct_answer' in self.current_scenario:
            if self.current_scenario['correct_answer'] == option_id:
                self.player_score += 100
                return True
        return False
        
    def check_time_up(self):
        elapsed = time.time() - self.scenario_start_time
        return elapsed >= self.scenario_duration

def start_game():
    app = Ursina()
    
    # Oyun modları
    battle_royale = BattleRoyaleMode()
    tournament = FastFinanceTournament()
    
    # Ana menü
    menu = Entity(parent=camera.ui)
    Button(text='Battle Royale Modu', scale=(0.3, 0.1), position=(0, 0.2), parent=menu)
    Button(text='Hızlı Finans Turnuvası', scale=(0.3, 0.1), position=(0, -0.2), parent=menu)
    
    app.run()

def generate_player_event(player=None):
    if player is None:
        return None
        
    events = [
        {
            'type': 'market_opportunity',
            'description': 'Yeni bir yatırım fırsatı!',
            'effect': lambda p: setattr(p, 'market_multiplier', p.market_multiplier * 1.2)
        },
        {
            'type': 'resource_discovery',
            'description': 'Yeni kaynaklar keşfedildi!',
            'effect': lambda p: setattr(p, 'resource_efficiency', p.resource_efficiency * 1.15)
        }
    ]
    return random.choice(events)

def show_player_event(event=None):
    if event is None or not isinstance(event, dict):
        return None
        
    popup = WindowPanel(
        title='Yeni Olay!',
        content=event.get('description', ''),
        scale=(0.5, 0.3),
        position=(0, 0)
    )
    return popup

def apply_player_event(player=None, event=None):
    if player is None or event is None or not isinstance(event, dict):
        return
        
    effect = event.get('effect')
    if effect and callable(effect):
        effect(player)

class FinAsisGame(Ursina):
    def __init__(self, player_id):
        super().__init__()
        self.player_id = player_id
        self.game_integration = GameIntegration(player_id)
        
        # Oyun ayarları
        window.title = "FinAsis - Ticaretin İzinde"
        window.borderless = False
        window.fullscreen = False
        window.exit_button.visible = False
        
        # Oyun durumu
        self.game_state = {
            'is_paused': False,
            'current_time': time.time(),
            'game_speed': 1.0,  # Oyun hızı çarpanı
            'difficulty': 'normal',  # easy, normal, hard
            'save_interval': 60,  # Otomatik kayıt aralığı
            'last_save_time': time.time()
        }
        
        # Oyuncu verileri
        self.player_data = {
            'name': self.game_integration.player_data['name'],
            'balance': self.game_integration.player_data['balance'],
            'score': self.game_integration.player_data['score'],
            'experience': 0,
            'level': 1,
            'skills': {
                'management': 1,
                'marketing': 1,
                'finance': 1,
                'production': 1
            },
            'achievements': [],
            'inventory': {},
            'buildings': [],
            'employees': []
        }
        
        # Ekonomik sistem
        self.economy = {
            'market_demand': {},
            'prices': {},
            'inflation_rate': 0.02,
            'interest_rate': 0.1,
            'tax_rate': 0.2,
            'last_update': time.time()
        }
        
        # Görev sistemi
        self.quest_system = {
            'active_quests': [],
            'completed_quests': [],
            'daily_quests': [],
            'achievements': [],
            'rewards': {}
        }
        
        # Pazar araştırması
        self.market_research = {
            'last_research_time': time.time(),
            'research_interval': 300,  # 5 dakika
            'market_data': {},
            'trends': [],
            'opportunities': [],
            'customer_feedback': [],
            'market_share': {},
            'competitor_analysis': {},
            'demand_forecast': {}
        }
        
        # Rekabet analizi
        self.competition_analysis = {
            'competitors': [],
            'market_share': {},
            'strengths': [],
            'weaknesses': [],
            'last_analysis_time': time.time(),
            'competitive_advantage': {},
            'threat_level': 0.5,
            'market_position': 'neutral'
        }
        
        # Finansal raporlama
        self.financial_reports = {
            'balance_sheet': {},
            'income_statement': {},
            'cash_flow': {},
            'last_report_time': time.time(),
            'report_interval': 3600,
            'financial_ratios': {},
            'budget_planning': {},
            'investment_analysis': {}
        }
        
        # Stratejik planlama
        self.strategic_planning = {
            'objectives': [],
            'strategies': [],
            'action_plans': [],
            'performance_metrics': {},
            'last_review_time': time.time(),
            'vision': '',
            'mission': '',
            'core_values': [],
            'swot_analysis': {}
        }
        
        # Üretim sistemi
        self.production_system = {
            'factories': [],
            'production_lines': [],
            'inventory': {},
            'supply_chain': {},
            'quality_control': {},
            'efficiency': 1.0
        }
        
        # İnsan kaynakları
        self.hr_system = {
            'personnel': {
                'employees': [],
                'departments': [],
                'last_update': time.time(),
                'update_interval': 3600  # 1 saat
            },
            'training': {
                'programs': [],
                'certifications': [],
                'last_review': time.time(),
                'review_interval': 7200  # 2 saat
            },
            'performance': {
                'evaluations': [],
                'rewards': [],
                'last_assessment': time.time(),
                'assessment_interval': 14400  # 4 saat
            },
            'career': {
                'paths': [],
                'promotions': [],
                'last_check': time.time(),
                'check_interval': 10800  # 3 saat
            }
        }
        
        # Pazarlama sistemi
        self.marketing_system = {
            'campaigns': [],
            'brand_value': 0,
            'customer_base': {},
            'advertising_budget': 0,
            'social_media': {},
            'market_research': {}
        }
        
        # AR-GE sistemi
        self.rnd_system = {
            'projects': [],
            'technologies': [],
            'innovations': [],
            'research_budget': 0,
            'patents': [],
            'development_time': {}
        }
        
        # UI elementleri
        self.create_ui()
        
        # Ses sistemi
        self.sound_system = {
            'music_volume': 0.5,
            'sfx_volume': 0.7,
            'current_track': None,
            'playlist': []
        }
        
        # Grafik ayarları
        self.graphics_settings = {
            'quality': 'high',
            'shadows': True,
            'particles': True,
            'effects': True
        }
        
        # Çoklu oyuncu desteği
        self.multiplayer = {
            'is_online': False,
            'players': [],
            'trades': [],
            'alliances': [],
            'competitions': []
        }
        
        # Başlangıç durumu
        self.initialize_game()
        
        # Eğitim sistemi
        self.training_system = {
            'employee_trainings': [],
            'management_programs': [],
            'online_courses': [],
            'certifications': [],
            'training_budget': 0,
            'training_efficiency': 1.0,
            'last_training_update': time.time(),
            'training_interval': 3600,  # 1 saat
            'available_courses': {
                'basic': [
                    {'name': 'Temel Finans', 'duration': 2, 'cost': 1000, 'skill': 'finance'},
                    {'name': 'Temel Pazarlama', 'duration': 2, 'cost': 1000, 'skill': 'marketing'},
                    {'name': 'Temel Üretim', 'duration': 2, 'cost': 1000, 'skill': 'production'}
                ],
                'advanced': [
                    {'name': 'İleri Finans', 'duration': 4, 'cost': 2000, 'skill': 'finance'},
                    {'name': 'İleri Pazarlama', 'duration': 4, 'cost': 2000, 'skill': 'marketing'},
                    {'name': 'İleri Üretim', 'duration': 4, 'cost': 2000, 'skill': 'production'}
                ],
                'management': [
                    {'name': 'Liderlik Eğitimi', 'duration': 6, 'cost': 3000, 'skill': 'management'},
                    {'name': 'Stratejik Yönetim', 'duration': 6, 'cost': 3000, 'skill': 'management'},
                    {'name': 'Proje Yönetimi', 'duration': 6, 'cost': 3000, 'skill': 'management'}
                ]
            }
        }
        
        # Eğitim paneli
        self.training_panel = Entity(
            model='quad',
            texture='white_cube',
            scale=(0.3, 0.4),
            position=(0.7, 0.2),
            color=color.rgba(0, 0, 0, 0.7)
        )
        
        # Kalite yönetim sistemi
        self.quality_system = {
            'iso_standards': {
                'iso9001': False,
                'iso14001': False,
                'iso45001': False
            },
            'quality_control': {
                'processes': [],
                'checkpoints': [],
                'defect_rate': 0.05,
                'last_audit': time.time(),
                'audit_interval': 86400  # 24 saat
            },
            'customer_satisfaction': {
                'score': 0.8,
                'feedback': [],
                'last_survey': time.time(),
                'survey_interval': 43200  # 12 saat
            },
            'continuous_improvement': {
                'projects': [],
                'metrics': {},
                'last_review': time.time(),
                'review_interval': 21600  # 6 saat
            }
        }
        
        # Kalite paneli
        self.quality_panel = Entity(
            model='quad',
            texture='white_cube',
            scale=(0.3, 0.4),
            position=(0.7, -0.3),
            color=color.rgba(0, 0, 0, 0.7)
        )
        
        # Sürdürülebilirlik sistemi
        self.sustainability_system = {
            'environmental_impact': {
                'carbon_footprint': 1000,  # kg CO2
                'energy_consumption': 5000,  # kWh
                'water_usage': 2000,  # m3
                'waste_generated': 500,  # kg
                'last_measurement': time.time(),
                'measurement_interval': 43200  # 12 saat
            },
            'social_responsibility': {
                'community_projects': [],
                'employee_wellbeing': 0.8,
                'diversity_score': 0.7,
                'last_assessment': time.time(),
                'assessment_interval': 86400  # 24 saat
            },
            'energy_efficiency': {
                'renewable_energy_ratio': 0.2,
                'energy_savings': 0,
                'efficiency_projects': [],
                'last_audit': time.time(),
                'audit_interval': 21600  # 6 saat
            },
            'waste_management': {
                'recycling_rate': 0.3,
                'waste_reduction': 0,
                'waste_projects': [],
                'last_review': time.time(),
                'review_interval': 43200  # 12 saat
            }
        }
        
        # Sürdürülebilirlik paneli
        self.sustainability_panel = Entity(
            model='quad',
            texture='white_cube',
            scale=(0.3, 0.4),
            position=(0.7, -0.3),
            color=color.rgba(0, 0, 0, 0.7)
        )
        
        # Kriz yönetim sistemi
        self.crisis_system = {
            'risk_assessment': {
                'financial_risks': [],
                'operational_risks': [],
                'market_risks': [],
                'last_assessment': time.time(),
                'assessment_interval': 21600  # 6 saat
            },
            'emergency_plans': {
                'financial_crisis': {
                    'status': 'ready',
                    'last_update': time.time(),
                    'update_interval': 43200  # 12 saat
                },
                'market_crisis': {
                    'status': 'ready',
                    'last_update': time.time(),
                    'update_interval': 43200
                },
                'operational_crisis': {
                    'status': 'ready',
                    'last_update': time.time(),
                    'update_interval': 43200
                }
            },
            'business_continuity': {
                'backup_systems': [],
                'recovery_plans': [],
                'last_test': time.time(),
                'test_interval': 86400  # 24 saat
            },
            'crisis_communication': {
                'stakeholders': [],
                'communication_plans': [],
                'last_review': time.time(),
                'review_interval': 43200  # 12 saat
            }
        }
        
        # Kriz yönetim paneli
        self.crisis_panel = Entity(
            model='quad',
            texture='white_cube',
            scale=(0.3, 0.4),
            position=(0.7, -0.3),
            color=color.rgba(0, 0, 0, 0.7)
        )
        
        # Uluslararası ticaret sistemi
        self.international_trade = {
            'exchange_rates': {
                'USD': 1.0,
                'EUR': 0.92,
                'GBP': 0.79,
                'JPY': 151.0,
                'CNY': 7.24,
                'last_update': time.time(),
                'update_interval': 3600  # 1 saat
            },
            'customs_processes': {
                'documents': [],
                'regulations': [],
                'last_check': time.time(),
                'check_interval': 21600  # 6 saat
            },
            'cultural_adaptation': {
                'markets': [],
                'localization': [],
                'last_review': time.time(),
                'review_interval': 43200  # 12 saat
            },
            'supply_chain': {
                'suppliers': [],
                'logistics': [],
                'last_audit': time.time(),
                'audit_interval': 86400  # 24 saat
            }
        }
        
        # Uluslararası ticaret paneli
        self.international_trade_panel = Entity(
            model='quad',
            texture='white_cube',
            scale=(0.3, 0.4),
            position=(0.7, -0.3),
            color=color.rgba(0, 0, 0, 0.7)
        )
        
        # Dijital dönüşüm sistemi
        self.digital_transformation = {
            'artificial_intelligence': {
                'models': [],
                'applications': [],
                'last_update': time.time(),
                'update_interval': 21600  # 6 saat
            },
            'automation': {
                'processes': [],
                'robots': [],
                'last_audit': time.time(),
                'audit_interval': 43200  # 12 saat
            },
            'data_analytics': {
                'dashboards': [],
                'reports': [],
                'last_analysis': time.time(),
                'analysis_interval': 3600  # 1 saat
            },
            'cyber_security': {
                'threats': [],
                'defenses': [],
                'last_check': time.time(),
                'check_interval': 1800  # 30 dakika
            }
        }
        
        # Dijital dönüşüm paneli
        self.digital_panel = Entity(
            model='quad',
            texture='white_cube',
            scale=(0.3, 0.4),
            position=(0.7, -0.3),
            color=color.rgba(0, 0, 0, 0.7)
        )
        
        # İnovasyon yönetim sistemi
        self.innovation_system = {
            'idea_management': {
                'ideas': [],
                'evaluations': [],
                'last_review': time.time(),
                'review_interval': 21600  # 6 saat
            },
            'patent_management': {
                'patents': [],
                'applications': [],
                'last_check': time.time(),
                'check_interval': 43200  # 12 saat
            },
            'rnd_projects': {
                'active_projects': [],
                'completed_projects': [],
                'last_update': time.time(),
                'update_interval': 3600  # 1 saat
            },
            'technology_transfer': {
                'partnerships': [],
                'licenses': [],
                'last_audit': time.time(),
                'audit_interval': 86400  # 24 saat
            }
        }
        
        # İnovasyon yönetim paneli
        self.innovation_panel = Entity(
            model='quad',
            texture='white_cube',
            scale=(0.3, 0.4),
            position=(0.7, -0.3),
            color=color.rgba(0, 0, 0, 0.7)
        )
        
        # CRM sistemi
        self.crm_system = {
            'customer_data': {
                'customers': [],
                'segments': [],
                'last_update': time.time(),
                'update_interval': 3600  # 1 saat
            },
            'sales_history': {
                'transactions': [],
                'loyalty_programs': [],
                'last_check': time.time(),
                'check_interval': 1800  # 30 dakika
            },
            'customer_satisfaction': {
                'surveys': [],
                'feedback': [],
                'last_survey': time.time(),
                'survey_interval': 7200  # 2 saat
            },
            'marketing_campaigns': {
                'active_campaigns': [],
                'completed_campaigns': [],
                'last_review': time.time(),
                'review_interval': 14400  # 4 saat
            }
        }
        
        # CRM paneli
        self.crm_panel = Entity(
            model='quad',
            texture='white_cube',
            scale=(0.3, 0.4),
            position=(0.7, -0.3),
            color=color.rgba(0, 0, 0, 0.7)
        )
        
        # Tedarik zinciri yönetim sistemi
        self.scm_system = {
            'suppliers': {
                'active_suppliers': [],
                'evaluations': [],
                'last_check': time.time(),
                'check_interval': 7200  # 2 saat
            },
            'inventory': {
                'stock_levels': [],
                'orders': [],
                'last_audit': time.time(),
                'audit_interval': 3600  # 1 saat
            },
            'logistics': {
                'shipments': [],
                'routes': [],
                'last_update': time.time(),
                'update_interval': 1800  # 30 dakika
            },
            'risk_management': {
                'risks': [],
                'mitigations': [],
                'last_assessment': time.time(),
                'assessment_interval': 14400  # 4 saat
            }
        }
        
        # SCM paneli
        self.scm_panel = Entity(
            model='quad',
            texture='white_cube',
            scale=(0.3, 0.4),
            position=(0.7, -0.3),
            color=color.rgba(0, 0, 0, 0.7)
        )
        
        # Proje yönetim sistemi
        self.pm_system = {
            'projects': {
                'active_projects': [],
                'completed_projects': [],
                'last_review': time.time(),
                'review_interval': 3600  # 1 saat
            },
            'resources': {
                'teams': [],
                'equipment': [],
                'last_check': time.time(),
                'check_interval': 1800  # 30 dakika
            },
            'scheduling': {
                'tasks': [],
                'milestones': [],
                'last_update': time.time(),
                'update_interval': 900  # 15 dakika
            },
            'performance': {
                'metrics': [],
                'reports': [],
                'last_assessment': time.time(),
                'assessment_interval': 7200  # 2 saat
            }
        }
        
        # PM paneli
        self.pm_panel = Entity(
            model='quad',
            texture='white_cube',
            scale=(0.3, 0.4),
            position=(0.7, -0.3),
            color=color.rgba(0, 0, 0, 0.7)
        )
        
        # HR paneli
        self.hr_panel = Entity(
            model='quad',
            texture='white_cube',
            scale=(0.3, 0.4),
            position=(0.7, -0.3),
            color=color.rgba(0, 0, 0, 0.7)
        )
        
        # Finansal raporlama sistemi
        self.fr_system = {
            'balance_sheet': {
                'assets': [],
                'liabilities': [],
                'equity': [],
                'last_update': time.time(),
                'update_interval': 3600  # 1 saat
            },
            'income_statement': {
                'revenues': [],
                'expenses': [],
                'profits': [],
                'last_check': time.time(),
                'check_interval': 1800  # 30 dakika
            },
            'cash_flow': {
                'operations': [],
                'investments': [],
                'financing': [],
                'last_audit': time.time(),
                'audit_interval': 7200  # 2 saat
            },
            'ratios': {
                'liquidity': [],
                'profitability': [],
                'leverage': [],
                'last_calculation': time.time(),
                'calculation_interval': 14400  # 4 saat
            }
        }
        
        # FR paneli
        self.fr_panel = Entity(
            model='quad',
            texture='white_cube',
            scale=(0.3, 0.4),
            position=(0.7, -0.3),
            color=color.rgba(0, 0, 0, 0.7)
        )
        
        # Sağlık yönetim sistemi
        self.health_system = {
            'player_age': 18,  # Varsayılan yaş
            'play_time': 0,    # Toplam oyun süresi (saniye)
            'break_time': 0,   # Toplam mola süresi (saniye)
            'last_break': time.time(),
            'health_tips': [],
            'recommended_play_time': 7200,  # 2 saat
            'recommended_break_interval': 1800,  # 30 dakika
            'break_duration': 300  # 5 dakika
        }
        
        # Sağlık paneli
        self.health_panel = Entity(
            model='quad',
            texture='white_cube',
            scale=(0.3, 0.4),
            position=(0.7, -0.3),
            color=color.rgba(0, 0, 0, 0.7)
        )
        
        # Egzersiz sistemi
        self.exercise_system = {
            'last_exercise': time.time(),
            'exercise_interval': 3600,  # 1 saat
            'exercise_duration': 300,   # 5 dakika
            'current_exercises': [],
            'exercise_history': [],
            'exercise_types': {
                'stretching': [
                    "Boyun esnetme",
                    "Omuz çevirme",
                    "Kol esnetme",
                    "Bel döndürme",
                    "Bacak esnetme"
                ],
                'strength': [
                    "Şınav",
                    "Mekik",
                    "Squat",
                    "Plank",
                    "Lunge"
                ],
                'cardio': [
                    "Yerinde koşu",
                    "Zıplama",
                    "Merdiven çıkma",
                    "Dans etme",
                    "İp atlama"
                ]
            }
        }
        
        # Egzersiz paneli
        self.exercise_panel = Entity(
            model='quad',
            texture='white_cube',
            scale=(0.3, 0.4),
            position=(0.7, -0.3),
            color=color.rgba(0, 0, 0, 0.7)
        )
        
    def initialize_game(self):
        """Oyunu başlatır ve başlangıç durumunu ayarlar"""
        # Başlangıç görevlerini yükle
        self.load_initial_quests()
        
        # Başlangıç binalarını oluştur
        self.create_initial_buildings()
        
        # Başlangıç çalışanlarını işe al
        self.hire_initial_employees()
        
        # Pazar verilerini başlat
        self.initialize_market_data()
        
        # Finansal durumu başlat
        self.initialize_financial_state()
        
        # Stratejik planı oluştur
        self.create_initial_strategic_plan()
        
    def create_ui(self):
        """UI elementlerini oluşturur"""
        # Ana menü
        self.main_menu = Entity(
            model='quad',
            texture='white_cube',
            scale=(1, 1),
            position=(0, 0),
            color=color.rgba(0, 0, 0, 0.8)
        )
        
        # Pazar araştırması paneli
        self.market_research_panel = Entity(
            model='quad',
            texture='white_cube',
            scale=(0.3, 0.4),
            position=(-0.7, 0.2),
            color=color.rgba(0, 0, 0, 0.7)
        )
        
        # Rekabet analizi paneli
        self.competition_panel = Entity(
            model='quad',
            texture='white_cube',
            scale=(0.3, 0.4),
            position=(-0.7, -0.3),
            color=color.rgba(0, 0, 0, 0.7)
        )
        
        # Finansal raporlama paneli
        self.financial_panel = Entity(
            model='quad',
            texture='white_cube',
            scale=(0.3, 0.4),
            position=(0, 0.2),
            color=color.rgba(0, 0, 0, 0.7)
        )
        
        # Stratejik planlama paneli
        self.strategic_panel = Entity(
            model='quad',
            texture='white_cube',
            scale=(0.3, 0.4),
            position=(0, -0.3),
            color=color.rgba(0, 0, 0, 0.7)
        )
        
        # Üretim paneli
        self.production_panel = Entity(
            model='quad',
            texture='white_cube',
            scale=(0.3, 0.4),
            position=(0.7, 0.2),
            color=color.rgba(0, 0, 0, 0.7)
        )
        
        # İK paneli
        self.hr_panel = Entity(
            model='quad',
            texture='white_cube',
            scale=(0.3, 0.4),
            position=(0.7, -0.3),
            color=color.rgba(0, 0, 0, 0.7)
        )
        
        # Pazarlama paneli
        self.marketing_panel = Entity(
            model='quad',
            texture='white_cube',
            scale=(0.3, 0.4),
            position=(0.35, 0.2),
            color=color.rgba(0, 0, 0, 0.7)
        )
        
        # AR-GE paneli
        self.rnd_panel = Entity(
            model='quad',
            texture='white_cube',
            scale=(0.3, 0.4),
            position=(0.35, -0.3),
            color=color.rgba(0, 0, 0, 0.7)
        )
        
        # Bildirim sistemi
        self.notification_system = {
            'panel': Entity(
                model='quad',
                texture='white_cube',
                scale=(0.4, 0.2),
                position=(0, 0.4),
                color=color.rgba(0, 0, 0, 0.7)
            ),
            'messages': [],
            'last_notification': time.time()
        }
        
        # Mini harita
        self.minimap = Entity(
            model='quad',
            texture='white_cube',
            scale=(0.2, 0.2),
            position=(0.8, 0.4),
            color=color.rgba(0, 0, 0, 0.7)
        )
        
        # Kontrol paneli
        self.control_panel = Entity(
            model='quad',
            texture='white_cube',
            scale=(0.4, 0.1),
            position=(0, -0.45),
            color=color.rgba(0, 0, 0, 0.7)
        )
        
    def update(self):
        """Her frame'de çalışacak güncelleme fonksiyonu"""
        current_time = time.time()
        
        # Oyun hızı kontrolü
        if not self.game_state['is_paused']:
            time_delta = (current_time - self.game_state['current_time']) * self.game_state['game_speed']
            self.game_state['current_time'] = current_time
            
            # Sistem güncellemeleri
            self.update_market_research()
            self.update_competition_analysis()
            self.update_financial_reports()
            self.update_strategic_planning()
            self.update_production_system()
            self.update_hr_system()
            self.update_marketing_system()
            self.update_rnd_system()
            self.update_economy()
            self.update_quest_system()
            
            # Otomatik kayıt
            if current_time - self.game_state['last_save_time'] >= self.game_state['save_interval']:
                self.save_game()
                self.game_state['last_save_time'] = current_time
            
            # UI güncelleme
            self.update_ui()
            
            # Bildirim kontrolü
            self.check_notifications()
            
            # Çoklu oyuncu güncelleme
            if self.multiplayer['is_online']:
                self.update_multiplayer()
                
            # Eğitim sistemi güncellemesi
            self.update_training_system()
            
            # Kalite sistemi güncellemesi
            self.update_quality_system()
            
            # Sürdürülebilirlik sistemi güncellemesi
            self.update_sustainability_system()
            
            # Kriz yönetim sistemi güncellemesi
            self.update_crisis_system()
            
            # Uluslararası ticaret sistemi güncellemesi
            self.update_international_trade()
            
            # Dijital dönüşüm sistemi güncellemesi
            self.update_digital_transformation()
            
            # İnovasyon yönetim sistemi güncellemesi
            self.update_innovation_system()
            
            # CRM sistemi güncellemesi
            self.update_crm_system()
            
            # Tedarik zinciri yönetim sistemi güncellemesi
            self.update_scm_system()
            
            # PM sistemi güncellemesi
            self.update_pm_system()
            
            # FR sistemi güncellemesi
            self.update_fr_system()
            
            # Sağlık sistemi güncellemesi
            self.update_health_system()
            
            # Egzersiz sistemi güncellemesi
            self.update_exercise_system()
            
    def input(self, key):
        """Klavye girişlerini işler"""
        # Oyun kontrolleri
        if key == 'escape':
            self.toggle_pause()
        elif key == 'space':
            self.toggle_game_speed()
            
        # Sistem kontrolleri
        if key == 'r':
            self.update_market_research()
        elif key == 'c':
            self.update_competition_analysis()
        elif key == 'f':
            self.update_financial_reports()
        elif key == 's':
            self.update_strategic_planning()
        elif key == 'p':
            self.show_production_panel()
        elif key == 'h':
            self.show_hr_panel()
        elif key == 'm':
            self.show_marketing_panel()
        elif key == 'd':
            self.show_rnd_panel()
            
        # Çoklu oyuncu kontrolleri
        if key == 't':
            self.initiate_trade()
        elif key == 'a':
            self.propose_alliance()
            
        # Eğitim sistemi kontrolleri
        if key == 'e':
            self.show_training_panel()
            
        # Kalite yönetimi kontrolleri
        if key == 'q':
            self.show_quality_panel()
            
        # Sürdürülebilirlik kontrolleri
        if key == 's':
            self.show_sustainability_panel()
            
        # Kriz yönetimi kontrolleri
        if key == 'k':
            self.show_crisis_panel()
            
        # Uluslararası ticaret kontrolleri
        if key == 'u':
            self.show_international_trade_panel()
            
        # Dijital dönüşüm kontrolleri
        if key == 'd':
            self.show_digital_panel()
            
        # İnovasyon yönetimi kontrolleri
        if key == 'i':
            self.show_innovation_panel()
            
        # CRM kontrolleri
        if key == 'm':
            self.show_crm_panel()
            
        # SCM kontrolleri
        if key == 't':
            self.show_scm_panel()
            
        # PM kontrolleri
        if key == 'p':
            self.show_pm_panel()
            
        # FR kontrolleri
        if key == 'f':
            self.show_fr_panel()
            
        # Sağlık kontrolleri
        if key == 'h':
            self.show_health_panel()
            
        # Egzersiz kontrolleri
        if key == 'e':
            self.show_exercise_panel()
            
    def toggle_pause(self):
        """Oyunu duraklatır/devam ettirir"""
        self.game_state['is_paused'] = not self.game_state['is_paused']
        self.show_notification("Oyun " + ("duraklatıldı" if self.game_state['is_paused'] else "devam ediyor"))
        
    def toggle_game_speed(self):
        """Oyun hızını değiştirir"""
        speeds = [0.5, 1.0, 2.0, 4.0]
        current_index = speeds.index(self.game_state['game_speed'])
        next_index = (current_index + 1) % len(speeds)
        self.game_state['game_speed'] = speeds[next_index]
        self.show_notification(f"Oyun hızı: {self.game_state['game_speed']}x")
        
    def show_notification(self, message, duration=3):
        """Bildirim gösterir"""
        self.notification_system['messages'].append({
            'text': message,
            'time': time.time(),
            'duration': duration
        })
        
    def check_notifications(self):
        """Bildirimleri kontrol eder"""
        current_time = time.time()
        for msg in self.notification_system['messages'][:]:
            if current_time - msg['time'] >= msg['duration']:
                self.notification_system['messages'].remove(msg)
                
    def save_game(self):
        """Oyun durumunu kaydeder"""
        save_data = {
            'player_data': self.player_data,
            'game_state': self.game_state,
            'economy': self.economy,
            'quest_system': self.quest_system,
            'market_research': self.market_research,
            'competition_analysis': self.competition_analysis,
            'financial_reports': self.financial_reports,
            'strategic_planning': self.strategic_planning,
            'production_system': self.production_system,
            'hr_system': self.hr_system,
            'marketing_system': self.marketing_system,
            'rnd_system': self.rnd_system,
            'rnd_system': self.rnd_system
        }
        
        try:
            with open(f'save_{self.player_id}.json', 'w') as f:
                json.dump(save_data, f)
            self.show_notification("Oyun kaydedildi")
        except Exception as e:
            self.show_notification(f"Kayıt hatası: {str(e)}", color.red)
            
    def load_game(self):
        """Kaydedilmiş oyunu yükler"""
        try:
            with open(f'save_{self.player_id}.json', 'r') as f:
                save_data = json.load(f)
                
            # Verileri yükle
            self.player_data = save_data['player_data']
            self.game_state = save_data['game_state']
            self.economy = save_data['economy']
            self.quest_system = save_data['quest_system']
            self.market_research = save_data['market_research']
            self.competition_analysis = save_data['competition_analysis']
            self.financial_reports = save_data['financial_reports']
            self.strategic_planning = save_data['strategic_planning']
            self.production_system = save_data['production_system']
            self.hr_system = save_data['hr_system']
            self.marketing_system = save_data['marketing_system']
            self.rnd_system = save_data['rnd_system']
            
            self.show_notification("Oyun yüklendi")
        except Exception as e:
            self.show_notification(f"Yükleme hatası: {str(e)}", color.red)
            
    def update_training_system(self):
        """Eğitim sistemini günceller"""
        current_time = time.time()
        if current_time - self.training_system['last_training_update'] >= self.training_system['training_interval']:
            # Eğitimleri kontrol et
            self.check_training_completion()
            
            # Yeni eğitim fırsatları oluştur
            self.generate_training_opportunities()
            
            # Eğitim bütçesini güncelle
            self.update_training_budget()
            
            self.training_system['last_training_update'] = current_time
            
    def check_training_completion(self):
        """Tamamlanan eğitimleri kontrol eder"""
        for training in self.training_system['employee_trainings'][:]:
            if current_time - training['start_time'] >= training['duration'] * 3600:
                # Eğitimi tamamla
                self.complete_training(training)
                self.training_system['employee_trainings'].remove(training)
                
    def complete_training(self, training):
        """Eğitimi tamamlar ve ödülleri verir"""
        employee = training['employee']
        course = training['course']
        
        # Beceri artışı
        skill_increase = random.uniform(0.1, 0.3)
        employee['skills'][course['skill']] = min(10, employee['skills'][course['skill']] + skill_increase)
        
        # Sertifika kontrolü
        if course['level'] == 'advanced' and random.random() < 0.7:
            self.training_system['certifications'].append({
                'employee': employee['id'],
                'course': course['name'],
                'date': time.time()
            })
            
        # Bildirim göster
        self.show_notification(f"{employee['name']} {course['name']} eğitimini tamamladı!")
        
    def generate_training_opportunities(self):
        """Yeni eğitim fırsatları oluşturur"""
        # Çalışanlar için eğitim fırsatları
        for employee in self.hr_system['personnel']['employees']:
            if random.random() < 0.3:  # %30 şans
                available_courses = self.get_available_courses(employee)
                if available_courses:
                    course = random.choice(available_courses)
                    self.training_system['employee_trainings'].append({
                        'employee': employee,
                        'course': course,
                        'start_time': time.time(),
                        'duration': course['duration']
                    })
                    
    def get_available_courses(self, employee):
        """Çalışan için uygun kursları döndürür"""
        available = []
        for level, courses in self.training_system['available_courses'].items():
            for course in courses:
                if employee['skills'][course['skill']] < 8:  # Beceri 8'den düşükse
                    available.append(course)
        return available
        
    def update_training_budget(self):
        """Eğitim bütçesini günceller"""
        # Bütçenin %5'i eğitim için ayrılır
        self.training_system['training_budget'] = self.player_data['balance'] * 0.05
        
    def show_training_panel(self):
        """Eğitim panelini gösterir"""
        self.training_panel.visible = True
        
        # Panel başlığı
        Text(
            parent=self.training_panel,
            text='Eğitim Sistemi',
            position=(0, 0.15),
            scale=2,
            color=color.white
        )
        
        # Eğitim bütçesi
        Text(
            parent=self.training_panel,
            text=f"Eğitim Bütçesi: ${self.training_system['training_budget']:,.2f}",
            position=(0, 0.05),
            scale=1.2,
            color=color.green
        )
        
        # Devam eden eğitimler
        y_pos = -0.05
        for training in self.training_system['employee_trainings']:
            progress = (time.time() - training['start_time']) / (training['duration'] * 3600)
            Text(
                parent=self.training_panel,
                text=f"{training['employee']['name']}: {training['course']['name']} (%{progress*100:.0f})",
                position=(0, y_pos),
                scale=1,
                color=color.white
            )
            y_pos -= 0.05

    def update_quality_system(self):
        """Kalite sistemini günceller"""
        current_time = time.time()
        
        # Denetim kontrolü
        if current_time - self.quality_system['quality_control']['last_audit'] >= self.quality_system['quality_control']['audit_interval']:
            self.perform_quality_audit()
            self.quality_system['quality_control']['last_audit'] = current_time
            
        # Müşteri memnuniyeti anketi
        if current_time - self.quality_system['customer_satisfaction']['last_survey'] >= self.quality_system['customer_satisfaction']['survey_interval']:
            self.perform_customer_survey()
            self.quality_system['customer_satisfaction']['last_survey'] = current_time
            
        # Sürekli iyileştirme gözden geçirmesi
        if current_time - self.quality_system['continuous_improvement']['last_review'] >= self.quality_system['continuous_improvement']['review_interval']:
            self.review_improvement_projects()
            self.quality_system['continuous_improvement']['last_review'] = current_time
            
    def perform_quality_audit(self):
        """Kalite denetimi yapar"""
        # Hata oranını kontrol et
        defect_rate = self.quality_system['quality_control']['defect_rate']
        
        # ISO standartlarına uygunluk kontrolü
        for standard in self.quality_system['iso_standards']:
            if not self.quality_system['iso_standards'][standard]:
                if random.random() < 0.3:  # %30 şans
                    self.quality_system['iso_standards'][standard] = True
                    self.show_notification(f"{standard} sertifikası alındı!")
                    
        # Kalite metriklerini güncelle
        self.update_quality_metrics()
        
    def perform_customer_survey(self):
        """Müşteri memnuniyeti anketi yapar"""
        # Yeni geri bildirimler topla
        new_feedback = {
            'product_quality': random.uniform(0.7, 1.0),
            'service_quality': random.uniform(0.7, 1.0),
            'delivery_time': random.uniform(0.7, 1.0),
            'price_value': random.uniform(0.7, 1.0)
        }
        
        self.quality_system['customer_satisfaction']['feedback'].append(new_feedback)
        
        # Memnuniyet skorunu güncelle
        total_score = sum(f['product_quality'] + f['service_quality'] + f['delivery_time'] + f['price_value'] 
                         for f in self.quality_system['customer_satisfaction']['feedback'])
        feedback_count = len(self.quality_system['customer_satisfaction']['feedback'])
        self.quality_system['customer_satisfaction']['score'] = total_score / (feedback_count * 4)
        
    def review_improvement_projects(self):
        """İyileştirme projelerini gözden geçirir"""
        # Tamamlanan projeleri kontrol et
        for project in self.quality_system['continuous_improvement']['projects'][:]:
            if project['status'] == 'in_progress' and random.random() < 0.2:  # %20 şans
                project['status'] = 'completed'
                self.apply_improvement_results(project)
                
        # Yeni projeler oluştur
        if random.random() < 0.3:  # %30 şans
            self.create_new_improvement_project()
            
    def apply_improvement_results(self, project):
        """İyileştirme sonuçlarını uygular"""
        if project['type'] == 'process':
            # Süreç verimliliğini artır
            self.production_system['efficiency'] *= 1.1
        elif project['type'] == 'quality':
            # Hata oranını düşür
            self.quality_system['quality_control']['defect_rate'] *= 0.9
        elif project['type'] == 'customer':
            # Müşteri memnuniyetini artır
            self.quality_system['customer_satisfaction']['score'] = min(1.0, 
                self.quality_system['customer_satisfaction']['score'] * 1.05)
                
        self.show_notification(f"{project['name']} iyileştirme projesi tamamlandı!")
        
    def create_new_improvement_project(self):
        """Yeni iyileştirme projesi oluşturur"""
        project_types = ['process', 'quality', 'customer']
        project_type = random.choice(project_types)
        
        new_project = {
            'name': f"{project_type.capitalize()} İyileştirme Projesi",
            'type': project_type,
            'status': 'in_progress',
            'start_time': time.time(),
            'duration': random.randint(3600, 7200)  # 1-2 saat
        }
        
        self.quality_system['continuous_improvement']['projects'].append(new_project)
        
    def show_quality_panel(self):
        """Kalite panelini gösterir"""
        self.quality_panel.visible = True
        
        # Panel başlığı
        Text(
            parent=self.quality_panel,
            text='Kalite Yönetimi',
            position=(0, 0.15),
            scale=2,
            color=color.white
        )
        
        # ISO standartları
        y_pos = 0.05
        for standard, certified in self.quality_system['iso_standards'].items():
            Text(
                parent=self.quality_panel,
                text=f"{standard}: {'✓' if certified else '✗'}",
                position=(0, y_pos),
                scale=1.2,
                color=color.green if certified else color.red
            )
            y_pos -= 0.05
            
        # Müşteri memnuniyeti
        Text(
            parent=self.quality_panel,
            text=f"Müşteri Memnuniyeti: %{self.quality_system['customer_satisfaction']['score']*100:.0f}",
            position=(0, y_pos),
            scale=1.2,
            color=color.yellow
        )
        y_pos -= 0.05
        
        # Hata oranı
        Text(
            parent=self.quality_panel,
            text=f"Hata Oranı: %{self.quality_system['quality_control']['defect_rate']*100:.1f}",
            position=(0, y_pos),
            scale=1.2,
            color=color.red
        )
        
    def update_sustainability_system(self):
        """Sürdürülebilirlik sistemini günceller"""
        current_time = time.time()
        
        # Çevresel etki ölçümü
        if current_time - self.sustainability_system['environmental_impact']['last_measurement'] >= self.sustainability_system['environmental_impact']['measurement_interval']:
            self.measure_environmental_impact()
            self.sustainability_system['environmental_impact']['last_measurement'] = current_time
            
        # Sosyal sorumluluk değerlendirmesi
        if current_time - self.sustainability_system['social_responsibility']['last_assessment'] >= self.sustainability_system['social_responsibility']['assessment_interval']:
            self.assess_social_responsibility()
            self.sustainability_system['social_responsibility']['last_assessment'] = current_time
            
        # Enerji verimliliği denetimi
        if current_time - self.sustainability_system['energy_efficiency']['last_audit'] >= self.sustainability_system['energy_efficiency']['audit_interval']:
            self.audit_energy_efficiency()
            self.sustainability_system['energy_efficiency']['last_audit'] = current_time
            
        # Atık yönetimi gözden geçirmesi
        if current_time - self.sustainability_system['waste_management']['last_review'] >= self.sustainability_system['waste_management']['review_interval']:
            self.review_waste_management()
            self.sustainability_system['waste_management']['last_review'] = current_time
            
    def measure_environmental_impact(self):
        """Çevresel etkiyi ölçer"""
        # Karbon ayak izi
        self.sustainability_system['environmental_impact']['carbon_footprint'] *= random.uniform(0.95, 1.05)
        
        # Enerji tüketimi
        self.sustainability_system['environmental_impact']['energy_consumption'] *= random.uniform(0.95, 1.05)
        
        # Su kullanımı
        self.sustainability_system['environmental_impact']['water_usage'] *= random.uniform(0.95, 1.05)
        
        # Atık üretimi
        self.sustainability_system['environmental_impact']['waste_generated'] *= random.uniform(0.95, 1.05)
        
    def assess_social_responsibility(self):
        """Sosyal sorumluluğu değerlendirir"""
        # Topluluk projeleri
        if random.random() < 0.2:  # %20 şans
            new_project = {
                'name': f"Topluluk Projesi {len(self.sustainability_system['social_responsibility']['community_projects']) + 1}",
                'impact': random.uniform(0.1, 0.3),
                'completion_time': random.randint(3600, 7200)  # 1-2 saat
            }
            self.sustainability_system['social_responsibility']['community_projects'].append(new_project)
            
        # Çalışan refahı
        self.sustainability_system['social_responsibility']['employee_wellbeing'] = min(1.0,
            self.sustainability_system['social_responsibility']['employee_wellbeing'] * random.uniform(1.0, 1.05))
            
        # Çeşitlilik skoru
        self.sustainability_system['social_responsibility']['diversity_score'] = min(1.0,
            self.sustainability_system['social_responsibility']['diversity_score'] * random.uniform(1.0, 1.05))
            
    def audit_energy_efficiency(self):
        """Enerji verimliliğini denetler"""
        # Yenilenebilir enerji oranı
        if random.random() < 0.3:  # %30 şans
            self.sustainability_system['energy_efficiency']['renewable_energy_ratio'] = min(1.0,
                self.sustainability_system['energy_efficiency']['renewable_energy_ratio'] * 1.1)
                
        # Enerji tasarrufu
        self.sustainability_system['energy_efficiency']['energy_savings'] += random.uniform(0.1, 0.5)
        
        # Verimlilik projeleri
        if random.random() < 0.2:  # %20 şans
            new_project = {
                'name': f"Enerji Verimliliği Projesi {len(self.sustainability_system['energy_efficiency']['efficiency_projects']) + 1}",
                'savings': random.uniform(0.1, 0.3),
                'completion_time': random.randint(3600, 7200)  # 1-2 saat
            }
            self.sustainability_system['energy_efficiency']['efficiency_projects'].append(new_project)
            
    def review_waste_management(self):
        """Atık yönetimini gözden geçirir"""
        # Geri dönüşüm oranı
        if random.random() < 0.3:  # %30 şans
            self.sustainability_system['waste_management']['recycling_rate'] = min(1.0,
                self.sustainability_system['waste_management']['recycling_rate'] * 1.1)
                
        # Atık azaltma
        self.sustainability_system['waste_management']['waste_reduction'] += random.uniform(0.1, 0.5)
        
        # Atık projeleri
        if random.random() < 0.2:  # %20 şans
            new_project = {
                'name': f"Atık Yönetimi Projesi {len(self.sustainability_system['waste_management']['waste_projects']) + 1}",
                'reduction': random.uniform(0.1, 0.3),
                'completion_time': random.randint(3600, 7200)  # 1-2 saat
            }
            self.sustainability_system['waste_management']['waste_projects'].append(new_project)
            
    def show_sustainability_panel(self):
        """Sürdürülebilirlik panelini gösterir"""
        self.sustainability_panel.visible = True
        
        # Panel başlığı
        Text(
            parent=self.sustainability_panel,
            text='Sürdürülebilirlik',
            position=(0, 0.15),
            scale=2,
            color=color.white
        )
        
        # Çevresel etki
        y_pos = 0.05
        Text(
            parent=self.sustainability_panel,
            text=f"Karbon Ayak İzi: {self.sustainability_system['environmental_impact']['carbon_footprint']:.0f} kg CO2",
            position=(0, y_pos),
            scale=1.2,
            color=color.red
        )
        y_pos -= 0.05
        
        Text(
            parent=self.sustainability_panel,
            text=f"Enerji Tüketimi: {self.sustainability_system['environmental_impact']['energy_consumption']:.0f} kWh",
            position=(0, y_pos),
            scale=1.2,
            color=color.yellow
        )
        y_pos -= 0.05
        
        # Sosyal sorumluluk
        Text(
            parent=self.sustainability_panel,
            text=f"Çalışan Refahı: %{self.sustainability_system['social_responsibility']['employee_wellbeing']*100:.0f}",
            position=(0, y_pos),
            scale=1.2,
            color=color.green
        )
        y_pos -= 0.05
        
        # Enerji verimliliği
        Text(
            parent=self.sustainability_panel,
            text=f"Yenilenebilir Enerji: %{self.sustainability_system['energy_efficiency']['renewable_energy_ratio']*100:.0f}",
            position=(0, y_pos),
            scale=1.2,
            color=color.blue
        )
        y_pos -= 0.05
        
        # Atık yönetimi
        Text(
            parent=self.sustainability_panel,
            text=f"Geri Dönüşüm Oranı: %{self.sustainability_system['waste_management']['recycling_rate']*100:.0f}",
            position=(0, y_pos),
            scale=1.2,
            color=color.orange
        )
        
    def update_crisis_system(self):
        """Kriz yönetim sistemini günceller"""
        current_time = time.time()
        
        # Risk değerlendirmesi
        if current_time - self.crisis_system['risk_assessment']['last_assessment'] >= self.crisis_system['risk_assessment']['assessment_interval']:
            self.assess_risks()
            self.crisis_system['risk_assessment']['last_assessment'] = current_time
            
        # Acil durum planları güncellemesi
        for plan_type in self.crisis_system['emergency_plans']:
            if current_time - self.crisis_system['emergency_plans'][plan_type]['last_update'] >= self.crisis_system['emergency_plans'][plan_type]['update_interval']:
                self.update_emergency_plan(plan_type)
                self.crisis_system['emergency_plans'][plan_type]['last_update'] = current_time
                
        # İş sürekliliği testi
        if current_time - self.crisis_system['business_continuity']['last_test'] >= self.crisis_system['business_continuity']['test_interval']:
            self.test_business_continuity()
            self.crisis_system['business_continuity']['last_test'] = current_time
            
        # Kriz iletişimi gözden geçirmesi
        if current_time - self.crisis_system['crisis_communication']['last_review'] >= self.crisis_system['crisis_communication']['review_interval']:
            self.review_crisis_communication()
            self.crisis_system['crisis_communication']['last_review'] = current_time
            
    def assess_risks(self):
        """Riskleri değerlendirir"""
        # Finansal riskler
        if random.random() < 0.2:  # %20 şans
            new_risk = {
                'type': 'financial',
                'severity': random.uniform(0.1, 0.5),
                'probability': random.uniform(0.1, 0.3),
                'mitigation_plan': f"Finansal Risk {len(self.crisis_system['risk_assessment']['financial_risks']) + 1}"
            }
            self.crisis_system['risk_assessment']['financial_risks'].append(new_risk)
            
        # Operasyonel riskler
        if random.random() < 0.2:  # %20 şans
            new_risk = {
                'type': 'operational',
                'severity': random.uniform(0.1, 0.5),
                'probability': random.uniform(0.1, 0.3),
                'mitigation_plan': f"Operasyonel Risk {len(self.crisis_system['risk_assessment']['operational_risks']) + 1}"
            }
            self.crisis_system['risk_assessment']['operational_risks'].append(new_risk)
            
        # Pazar riskleri
        if random.random() < 0.2:  # %20 şans
            new_risk = {
                'type': 'market',
                'severity': random.uniform(0.1, 0.5),
                'probability': random.uniform(0.1, 0.3),
                'mitigation_plan': f"Pazar Risk {len(self.crisis_system['risk_assessment']['market_risks']) + 1}"
            }
            self.crisis_system['risk_assessment']['market_risks'].append(new_risk)
            
    def update_emergency_plan(self, plan_type):
        """Acil durum planını günceller"""
        if random.random() < 0.3:  # %30 şans
            self.crisis_system['emergency_plans'][plan_type]['status'] = 'updated'
            self.show_notification(f"{plan_type.replace('_', ' ').title()} acil durum planı güncellendi!")
            
    def test_business_continuity(self):
        """İş sürekliliğini test eder"""
        # Yedek sistemler
        if random.random() < 0.2:  # %20 şans
            new_system = {
                'name': f"Yedek Sistem {len(self.crisis_system['business_continuity']['backup_systems']) + 1}",
                'type': random.choice(['financial', 'operational', 'technical']),
                'recovery_time': random.randint(3600, 7200)  # 1-2 saat
            }
            self.crisis_system['business_continuity']['backup_systems'].append(new_system)
            
        # Kurtarma planları
        if random.random() < 0.2:  # %20 şans
            new_plan = {
                'name': f"Kurtarma Planı {len(self.crisis_system['business_continuity']['recovery_plans']) + 1}",
                'scenario': random.choice(['financial_crisis', 'market_crisis', 'operational_crisis']),
                'recovery_steps': random.randint(3, 7)
            }
            self.crisis_system['business_continuity']['recovery_plans'].append(new_plan)
            
    def review_crisis_communication(self):
        """Kriz iletişimini gözden geçirir"""
        # Paydaşlar
        if random.random() < 0.2:  # %20 şans
            new_stakeholder = {
                'name': f"Paydaş {len(self.crisis_system['crisis_communication']['stakeholders']) + 1}",
                'type': random.choice(['investor', 'customer', 'supplier', 'employee']),
                'communication_channel': random.choice(['email', 'phone', 'meeting'])
            }
            self.crisis_system['crisis_communication']['stakeholders'].append(new_stakeholder)
            
        # İletişim planları
        if random.random() < 0.2:  # %20 şans
            new_plan = {
                'name': f"İletişim Planı {len(self.crisis_system['crisis_communication']['communication_plans']) + 1}",
                'crisis_type': random.choice(['financial', 'market', 'operational']),
                'channels': random.randint(2, 4)
            }
            self.crisis_system['crisis_communication']['communication_plans'].append(new_plan)
            
    def show_crisis_panel(self):
        """Kriz yönetim panelini gösterir"""
        self.crisis_panel.visible = True
        
        # Panel başlığı
        Text(
            parent=self.crisis_panel,
            text='Kriz Yönetimi',
            position=(0, 0.15),
            scale=2,
            color=color.white
        )
        
        # Risk değerlendirmesi
        y_pos = 0.05
        Text(
            parent=self.crisis_panel,
            text=f"Finansal Riskler: {len(self.crisis_system['risk_assessment']['financial_risks'])}",
            position=(0, y_pos),
            scale=1.2,
            color=color.red
        )
        y_pos -= 0.05
        
        Text(
            parent=self.crisis_panel,
            text=f"Operasyonel Riskler: {len(self.crisis_system['risk_assessment']['operational_risks'])}",
            position=(0, y_pos),
            scale=1.2,
            color=color.yellow
        )
        y_pos -= 0.05
        
        # Acil durum planları
        Text(
            parent=self.crisis_panel,
            text=f"Finansal Kriz Planı: {self.crisis_system['emergency_plans']['financial_crisis']['status']}",
            position=(0, y_pos),
            scale=1.2,
            color=color.green
        )
        y_pos -= 0.05
        
        # İş sürekliliği
        Text(
            parent=self.crisis_panel,
            text=f"Yedek Sistemler: {len(self.crisis_system['business_continuity']['backup_systems'])}",
            position=(0, y_pos),
            scale=1.2,
            color=color.blue
        )
        y_pos -= 0.05
        
        # Kriz iletişimi
        Text(
            parent=self.crisis_panel,
            text=f"İletişim Planları: {len(self.crisis_system['crisis_communication']['communication_plans'])}",
            position=(0, y_pos),
            scale=1.2,
            color=color.orange
        )
        
    def update_international_trade(self):
        """Uluslararası ticaret sistemini günceller"""
        current_time = time.time()
        
        # Döviz kurları güncellemesi
        if current_time - self.international_trade['exchange_rates']['last_update'] >= self.international_trade['exchange_rates']['update_interval']:
            self.update_exchange_rates()
            self.international_trade['exchange_rates']['last_update'] = current_time
            
        # Gümrük süreçleri kontrolü
        if current_time - self.international_trade['customs_processes']['last_check'] >= self.international_trade['customs_processes']['check_interval']:
            self.check_customs_processes()
            self.international_trade['customs_processes']['last_check'] = current_time
            
        # Kültürel uyum gözden geçirmesi
        if current_time - self.international_trade['cultural_adaptation']['last_review'] >= self.international_trade['cultural_adaptation']['review_interval']:
            self.review_cultural_adaptation()
            self.international_trade['cultural_adaptation']['last_review'] = current_time
            
        # Tedarik zinciri denetimi
        if current_time - self.international_trade['supply_chain']['last_audit'] >= self.international_trade['supply_chain']['audit_interval']:
            self.audit_supply_chain()
            self.international_trade['supply_chain']['last_audit'] = current_time
            
    def update_exchange_rates(self):
        """Döviz kurlarını günceller"""
        for currency in self.international_trade['exchange_rates']:
            if currency != 'last_update' and currency != 'update_interval':
                # Kurlarda %1'e kadar dalgalanma
                change = random.uniform(-0.01, 0.01)
                self.international_trade['exchange_rates'][currency] *= (1 + change)
                
    def check_customs_processes(self):
        """Gümrük süreçlerini kontrol eder"""
        # Gümrük belgeleri
        if random.random() < 0.2:  # %20 şans
            new_document = {
                'name': f"Gümrük Belgesi {len(self.international_trade['customs_processes']['documents']) + 1}",
                'type': random.choice(['import', 'export']),
                'validity': random.randint(30, 90)  # 30-90 gün
            }
            self.international_trade['customs_processes']['documents'].append(new_document)
            
        # Düzenlemeler
        if random.random() < 0.2:  # %20 şans
            new_regulation = {
                'name': f"Gümrük Düzenlemesi {len(self.international_trade['customs_processes']['regulations']) + 1}",
                'country': random.choice(['ABD', 'AB', 'Çin', 'Japonya', 'İngiltere']),
                'impact': random.uniform(0.1, 0.3)
            }
            self.international_trade['customs_processes']['regulations'].append(new_regulation)
            
    def review_cultural_adaptation(self):
        """Kültürel uyumu gözden geçirir"""
        # Pazar araştırması
        if random.random() < 0.2:  # %20 şans
            new_market = {
                'name': f"Pazar {len(self.international_trade['cultural_adaptation']['markets']) + 1}",
                'country': random.choice(['ABD', 'AB', 'Çin', 'Japonya', 'İngiltere']),
                'potential': random.uniform(0.5, 1.0)
            }
            self.international_trade['cultural_adaptation']['markets'].append(new_market)
            
        # Yerelleştirme
        if random.random() < 0.2:  # %20 şans
            new_localization = {
                'name': f"Yerelleştirme {len(self.international_trade['cultural_adaptation']['localization']) + 1}",
                'type': random.choice(['language', 'design', 'marketing']),
                'progress': random.uniform(0.1, 0.5)
            }
            self.international_trade['cultural_adaptation']['localization'].append(new_localization)
            
    def audit_supply_chain(self):
        """Tedarik zincirini denetler"""
        # Tedarikçiler
        if random.random() < 0.2:  # %20 şans
            new_supplier = {
                'name': f"Tedarikçi {len(self.international_trade['supply_chain']['suppliers']) + 1}",
                'country': random.choice(['ABD', 'AB', 'Çin', 'Japonya', 'İngiltere']),
                'reliability': random.uniform(0.7, 1.0)
            }
            self.international_trade['supply_chain']['suppliers'].append(new_supplier)
            
        # Lojistik
        if random.random() < 0.2:  # %20 şans
            new_logistics = {
                'name': f"Lojistik {len(self.international_trade['supply_chain']['logistics']) + 1}",
                'type': random.choice(['air', 'sea', 'land']),
                'efficiency': random.uniform(0.7, 1.0)
            }
            self.international_trade['supply_chain']['logistics'].append(new_logistics)
            
    def show_international_trade_panel(self):
        """Uluslararası ticaret panelini gösterir"""
        self.international_trade_panel.visible = True
        
        # Panel başlığı
        Text(
            parent=self.international_trade_panel,
            text='Uluslararası Ticaret',
            position=(0, 0.15),
            scale=2,
            color=color.white
        )
        
        # Döviz kurları
        y_pos = 0.05
        Text(
            parent=self.international_trade_panel,
            text=f"USD/TRY: {self.international_trade['exchange_rates']['USD']:.2f}",
            position=(0, y_pos),
            scale=1.2,
            color=color.green
        )
        y_pos -= 0.05
        
        Text(
            parent=self.international_trade_panel,
            text=f"EUR/TRY: {self.international_trade['exchange_rates']['EUR']:.2f}",
            position=(0, y_pos),
            scale=1.2,
            color=color.blue
        )
        y_pos -= 0.05
        
        # Gümrük süreçleri
        Text(
            parent=self.international_trade_panel,
            text=f"Gümrük Belgeleri: {len(self.international_trade['customs_processes']['documents'])}",
            position=(0, y_pos),
            scale=1.2,
            color=color.yellow
        )
        y_pos -= 0.05
        
        # Kültürel uyum
        Text(
            parent=self.international_trade_panel,
            text=f"Aktif Pazarlar: {len(self.international_trade['cultural_adaptation']['markets'])}",
            position=(0, y_pos),
            scale=1.2,
            color=color.orange
        )
        y_pos -= 0.05
        
        # Tedarik zinciri
        Text(
            parent=self.international_trade_panel,
            text=f"Tedarikçiler: {len(self.international_trade['supply_chain']['suppliers'])}",
            position=(0, y_pos),
            scale=1.2,
            color=color.red
        )
        
    def update_digital_transformation(self):
        """Dijital dönüşüm sistemini günceller"""
        current_time = time.time()
        
        # Yapay zeka güncellemesi
        if current_time - self.digital_transformation['artificial_intelligence']['last_update'] >= self.digital_transformation['artificial_intelligence']['update_interval']:
            self.update_ai_systems()
            self.digital_transformation['artificial_intelligence']['last_update'] = current_time
            
        # Otomasyon denetimi
        if current_time - self.digital_transformation['automation']['last_audit'] >= self.digital_transformation['automation']['audit_interval']:
            self.audit_automation()
            self.digital_transformation['automation']['last_audit'] = current_time
            
        # Veri analizi
        if current_time - self.digital_transformation['data_analytics']['last_analysis'] >= self.digital_transformation['data_analytics']['analysis_interval']:
            self.analyze_data()
            self.digital_transformation['data_analytics']['last_analysis'] = current_time
            
        # Siber güvenlik kontrolü
        if current_time - self.digital_transformation['cyber_security']['last_check'] >= self.digital_transformation['cyber_security']['check_interval']:
            self.check_security()
            self.digital_transformation['cyber_security']['last_check'] = current_time
            
    def update_ai_systems(self):
        """Yapay zeka sistemlerini günceller"""
        # AI modelleri
        if random.random() < 0.2:  # %20 şans
            new_model = {
                'name': f"AI Modeli {len(self.digital_transformation['artificial_intelligence']['models']) + 1}",
                'type': random.choice(['classification', 'regression', 'clustering']),
                'accuracy': random.uniform(0.8, 0.95)
            }
            self.digital_transformation['artificial_intelligence']['models'].append(new_model)
            
        # AI uygulamaları
        if random.random() < 0.2:  # %20 şans
            new_application = {
                'name': f"AI Uygulaması {len(self.digital_transformation['artificial_intelligence']['applications']) + 1}",
                'department': random.choice(['finans', 'pazarlama', 'üretim', 'insan_kaynaklari']),
                'efficiency': random.uniform(0.1, 0.3)
            }
            self.digital_transformation['artificial_intelligence']['applications'].append(new_application)
            
    def audit_automation(self):
        """Otomasyon sistemlerini denetler"""
        # Otomatik süreçler
        if random.random() < 0.2:  # %20 şans
            new_process = {
                'name': f"Otomatik Süreç {len(self.digital_transformation['automation']['processes']) + 1}",
                'type': random.choice(['iş akışı', 'raporlama', 'kontrol']),
                'savings': random.uniform(0.1, 0.5)
            }
            self.digital_transformation['automation']['processes'].append(new_process)
            
        # Robotlar
        if random.random() < 0.2:  # %20 şans
            new_robot = {
                'name': f"Robot {len(self.digital_transformation['automation']['robots']) + 1}",
                'task': random.choice(['veri girişi', 'kontrol', 'analiz']),
                'reliability': random.uniform(0.9, 1.0)
            }
            self.digital_transformation['automation']['robots'].append(new_robot)
            
    def analyze_data(self):
        """Veri analizi yapar"""
        # Gösterge panelleri
        if random.random() < 0.2:  # %20 şans
            new_dashboard = {
                'name': f"Gösterge Paneli {len(self.digital_transformation['data_analytics']['dashboards']) + 1}",
                'metrics': random.randint(5, 15),
                'update_frequency': random.choice(['gerçek zamanlı', 'saatlik', 'günlük'])
            }
            self.digital_transformation['data_analytics']['dashboards'].append(new_dashboard)
            
        # Raporlar
        if random.random() < 0.2:  # %20 şans
            new_report = {
                'name': f"Rapor {len(self.digital_transformation['data_analytics']['reports']) + 1}",
                'type': random.choice(['performans', 'trend', 'tahmin']),
                'insight_value': random.uniform(0.1, 0.5)
            }
            self.digital_transformation['data_analytics']['reports'].append(new_report)
            
    def check_security(self):
        """Siber güvenliği kontrol eder"""
        # Tehditler
        if random.random() < 0.2:  # %20 şans
            new_threat = {
                'name': f"Tehdit {len(self.digital_transformation['cyber_security']['threats']) + 1}",
                'type': random.choice(['phishing', 'malware', 'ddos']),
                'severity': random.uniform(0.1, 0.5)
            }
            self.digital_transformation['cyber_security']['threats'].append(new_threat)
            
        # Savunmalar
        if random.random() < 0.2:  # %20 şans
            new_defense = {
                'name': f"Savunma {len(self.digital_transformation['cyber_security']['defenses']) + 1}",
                'type': random.choice(['firewall', 'antivirus', 'encryption']),
                'effectiveness': random.uniform(0.7, 1.0)
            }
            self.digital_transformation['cyber_security']['defenses'].append(new_defense)
            
    def show_digital_panel(self):
        """Dijital dönüşüm panelini gösterir"""
        self.digital_panel.visible = True
        
        # Panel başlığı
        Text(
            parent=self.digital_panel,
            text='Dijital Dönüşüm',
            position=(0, 0.15),
            scale=2,
            color=color.white
        )
        
        # Yapay zeka
        y_pos = 0.05
        Text(
            parent=self.digital_panel,
            text=f"AI Modelleri: {len(self.digital_transformation['artificial_intelligence']['models'])}",
            position=(0, y_pos),
            scale=1.2,
            color=color.blue
        )
        y_pos -= 0.05
        
        # Otomasyon
        Text(
            parent=self.digital_panel,
            text=f"Otomatik Süreçler: {len(self.digital_transformation['automation']['processes'])}",
            position=(0, y_pos),
            scale=1.2,
            color=color.green
        )
        y_pos -= 0.05
        
        # Veri analizi
        Text(
            parent=self.digital_panel,
            text=f"Gösterge Panelleri: {len(self.digital_transformation['data_analytics']['dashboards'])}",
            position=(0, y_pos),
            scale=1.2,
            color=color.yellow
        )
        y_pos -= 0.05
        
        # Siber güvenlik
        Text(
            parent=self.digital_panel,
            text=f"Aktif Savunmalar: {len(self.digital_transformation['cyber_security']['defenses'])}",
            position=(0, y_pos),
            scale=1.2,
            color=color.red
        )
        y_pos -= 0.05
        
        # Tehdit seviyesi
        threat_level = len(self.digital_transformation['cyber_security']['threats']) / max(1, len(self.digital_transformation['cyber_security']['defenses']))
        Text(
            parent=self.digital_panel,
            text=f"Tehdit Seviyesi: %{threat_level*100:.0f}",
            position=(0, y_pos),
            scale=1.2,
            color=color.orange
        )
        
    def update_innovation_system(self):
        """İnovasyon yönetim sistemini günceller"""
        current_time = time.time()
        
        # Fikir yönetimi gözden geçirmesi
        if current_time - self.innovation_system['idea_management']['last_review'] >= self.innovation_system['idea_management']['review_interval']:
            self.review_ideas()
            self.innovation_system['idea_management']['last_review'] = current_time
            
        # Patent yönetimi kontrolü
        if current_time - self.innovation_system['patent_management']['last_check'] >= self.innovation_system['patent_management']['check_interval']:
            self.check_patents()
            self.innovation_system['patent_management']['last_check'] = current_time
            
        # Ar-Ge projeleri güncellemesi
        if current_time - self.innovation_system['rnd_projects']['last_update'] >= self.innovation_system['rnd_projects']['update_interval']:
            self.update_rnd_projects()
            self.innovation_system['rnd_projects']['last_update'] = current_time
            
        # Teknoloji transferi denetimi
        if current_time - self.innovation_system['technology_transfer']['last_audit'] >= self.innovation_system['technology_transfer']['audit_interval']:
            self.audit_technology_transfer()
            self.innovation_system['technology_transfer']['last_audit'] = current_time
            
    def review_ideas(self):
        """Fikirleri gözden geçirir"""
        # Yeni fikirler
        if random.random() < 0.2:  # %20 şans
            new_idea = {
                'name': f"Fikir {len(self.innovation_system['idea_management']['ideas']) + 1}",
                'category': random.choice(['ürün', 'süreç', 'hizmet', 'iş modeli']),
                'potential': random.uniform(0.1, 0.5)
            }
            self.innovation_system['idea_management']['ideas'].append(new_idea)
            
        # Fikir değerlendirmeleri
        if random.random() < 0.2:  # %20 şans
            new_evaluation = {
                'idea_id': random.randint(0, len(self.innovation_system['idea_management']['ideas'])),
                'score': random.uniform(0.1, 1.0),
                'feedback': random.choice(['geliştir', 'reddet', 'beklet'])
            }
            self.innovation_system['idea_management']['evaluations'].append(new_evaluation)
            
    def check_patents(self):
        """Patentleri kontrol eder"""
        # Yeni patentler
        if random.random() < 0.2:  # %20 şans
            new_patent = {
                'name': f"Patent {len(self.innovation_system['patent_management']['patents']) + 1}",
                'type': random.choice(['icat', 'tasarım', 'faydalı model']),
                'value': random.uniform(0.1, 0.5)
            }
            self.innovation_system['patent_management']['patents'].append(new_patent)
            
        # Patent başvuruları
        if random.random() < 0.2:  # %20 şans
            new_application = {
                'name': f"Başvuru {len(self.innovation_system['patent_management']['applications']) + 1}",
                'status': random.choice(['beklemede', 'değerlendirmede', 'onaylandı']),
                'priority': random.uniform(0.1, 1.0)
            }
            self.innovation_system['patent_management']['applications'].append(new_application)
            
    def update_rnd_projects(self):
        """Ar-Ge projelerini günceller"""
        # Aktif projeler
        if random.random() < 0.2:  # %20 şans
            new_project = {
                'name': f"Ar-Ge Projesi {len(self.innovation_system['rnd_projects']['active_projects']) + 1}",
                'budget': random.uniform(10000, 100000),
                'progress': random.uniform(0.1, 0.5)
            }
            self.innovation_system['rnd_projects']['active_projects'].append(new_project)
            
        # Tamamlanan projeler
        for project in self.innovation_system['rnd_projects']['active_projects'][:]:
            if project['progress'] >= 1.0:
                self.innovation_system['rnd_projects']['completed_projects'].append(project)
                self.innovation_system['rnd_projects']['active_projects'].remove(project)
                
    def audit_technology_transfer(self):
        """Teknoloji transferini denetler"""
        # Ortaklıklar
        if random.random() < 0.2:  # %20 şans
            new_partnership = {
                'name': f"Ortaklık {len(self.innovation_system['technology_transfer']['partnerships']) + 1}",
                'type': random.choice(['üniversite', 'araştırma merkezi', 'şirket']),
                'value': random.uniform(0.1, 0.5)
            }
            self.innovation_system['technology_transfer']['partnerships'].append(new_partnership)
            
        # Lisanslar
        if random.random() < 0.2:  # %20 şans
            new_license = {
                'name': f"Lisans {len(self.innovation_system['technology_transfer']['licenses']) + 1}",
                'type': random.choice(['in', 'out']),
                'revenue': random.uniform(1000, 10000)
            }
            self.innovation_system['technology_transfer']['licenses'].append(new_license)
            
    def show_innovation_panel(self):
        """İnovasyon yönetim panelini gösterir"""
        self.innovation_panel.visible = True
        
        # Panel başlığı
        Text(
            parent=self.innovation_panel,
            text='İnovasyon Yönetimi',
            position=(0, 0.15),
            scale=2,
            color=color.white
        )
        
        # Fikir yönetimi
        y_pos = 0.05
        Text(
            parent=self.innovation_panel,
            text=f"Aktif Fikirler: {len(self.innovation_system['idea_management']['ideas'])}",
            position=(0, y_pos),
            scale=1.2,
            color=color.blue
        )
        y_pos -= 0.05
        
        # Patent yönetimi
        Text(
            parent=self.innovation_panel,
            text=f"Patentler: {len(self.innovation_system['patent_management']['patents'])}",
            position=(0, y_pos),
            scale=1.2,
            color=color.green
        )
        y_pos -= 0.05
        
        # Ar-Ge projeleri
        Text(
            parent=self.innovation_panel,
            text=f"Aktif Projeler: {len(self.innovation_system['rnd_projects']['active_projects'])}",
            position=(0, y_pos),
            scale=1.2,
            color=color.yellow
        )
        y_pos -= 0.05
        
        # Teknoloji transferi
        Text(
            parent=self.innovation_panel,
            text=f"Ortaklıklar: {len(self.innovation_system['technology_transfer']['partnerships'])}",
            position=(0, y_pos),
            scale=1.2,
            color=color.orange
        )
        y_pos -= 0.05
        
        # İnovasyon skoru
        innovation_score = (
            len(self.innovation_system['idea_management']['ideas']) * 0.2 +
            len(self.innovation_system['patent_management']['patents']) * 0.3 +
            len(self.innovation_system['rnd_projects']['active_projects']) * 0.3 +
            len(self.innovation_system['technology_transfer']['partnerships']) * 0.2
        )
        Text(
            parent=self.innovation_panel,
            text=f"İnovasyon Skoru: {innovation_score:.1f}",
            position=(0, y_pos),
            scale=1.2,
            color=color.red
        )
        
    def update_crm_system(self):
        """CRM sistemini günceller"""
        current_time = time.time()
        
        # Müşteri verileri güncellemesi
        if current_time - self.crm_system['customer_data']['last_update'] >= self.crm_system['customer_data']['update_interval']:
            self.update_customer_data()
            self.crm_system['customer_data']['last_update'] = current_time
            
        # Satış geçmişi kontrolü
        if current_time - self.crm_system['sales_history']['last_check'] >= self.crm_system['sales_history']['check_interval']:
            self.check_sales_history()
            self.crm_system['sales_history']['last_check'] = current_time
            
        # Müşteri memnuniyeti anketi
        if current_time - self.crm_system['customer_satisfaction']['last_survey'] >= self.crm_system['customer_satisfaction']['survey_interval']:
            self.conduct_customer_survey()
            self.crm_system['customer_satisfaction']['last_survey'] = current_time
            
        # Pazarlama kampanyaları gözden geçirmesi
        if current_time - self.crm_system['marketing_campaigns']['last_review'] >= self.crm_system['marketing_campaigns']['review_interval']:
            self.review_marketing_campaigns()
            self.crm_system['marketing_campaigns']['last_review'] = current_time
            
    def update_customer_data(self):
        """Müşteri verilerini günceller"""
        # Yeni müşteriler
        if random.random() < 0.2:  # %20 şans
            new_customer = {
                'id': len(self.crm_system['customer_data']['customers']) + 1,
                'name': f"Müşteri {len(self.crm_system['customer_data']['customers']) + 1}",
                'segment': random.choice(['kurumsal', 'bireysel', 'VIP']),
                'value': random.uniform(1000, 10000)
            }
            self.crm_system['customer_data']['customers'].append(new_customer)
            
        # Müşteri segmentleri
        if random.random() < 0.2:  # %20 şans
            new_segment = {
                'name': f"Segment {len(self.crm_system['customer_data']['segments']) + 1}",
                'size': random.randint(10, 100),
                'value': random.uniform(0.1, 0.5)
            }
            self.crm_system['customer_data']['segments'].append(new_segment)
            
    def check_sales_history(self):
        """Satış geçmişini kontrol eder"""
        # Yeni işlemler
        if random.random() < 0.2:  # %20 şans
            new_transaction = {
                'customer_id': random.randint(1, len(self.crm_system['customer_data']['customers'])),
                'amount': random.uniform(100, 1000),
                'product': random.choice(['ürün', 'hizmet', 'abonelik']),
                'date': time.time()
            }
        
    def update_scm_system(self):
        """Tedarik zinciri yönetim sistemini günceller"""
        current_time = time.time()
        
        # Tedarikçi kontrolü
        if current_time - self.scm_system['suppliers']['last_check'] >= self.scm_system['suppliers']['check_interval']:
            self.check_suppliers()
            self.scm_system['suppliers']['last_check'] = current_time
            
        # Envanter denetimi
        if current_time - self.scm_system['inventory']['last_audit'] >= self.scm_system['inventory']['audit_interval']:
            self.audit_inventory()
            self.scm_system['inventory']['last_audit'] = current_time
            
        # Lojistik güncellemesi
        if current_time - self.scm_system['logistics']['last_update'] >= self.scm_system['logistics']['update_interval']:
            self.update_logistics()
            self.scm_system['logistics']['last_update'] = current_time
            
        # Risk değerlendirmesi
        if current_time - self.scm_system['risk_management']['last_assessment'] >= self.scm_system['risk_management']['assessment_interval']:
            self.assess_risks()
            self.scm_system['risk_management']['last_assessment'] = current_time
            
    def check_suppliers(self):
        """Tedarikçileri kontrol eder"""
        # Yeni tedarikçiler
        if random.random() < 0.2:  # %20 şans
            new_supplier = {
                'id': len(self.scm_system['suppliers']['active_suppliers']) + 1,
                'name': f"Tedarikçi {len(self.scm_system['suppliers']['active_suppliers']) + 1}",
                'category': random.choice(['hammadde', 'yarı mamul', 'tam mamul']),
                'reliability': random.uniform(0.1, 1.0)
            }
            self.scm_system['suppliers']['active_suppliers'].append(new_supplier)
            
        # Tedarikçi değerlendirmeleri
        if random.random() < 0.2:  # %20 şans
            new_evaluation = {
                'supplier_id': random.randint(1, len(self.scm_system['suppliers']['active_suppliers'])),
                'score': random.uniform(0.1, 1.0),
                'criteria': random.choice(['kalite', 'teslimat', 'fiyat', 'hizmet'])
            }
            self.scm_system['suppliers']['evaluations'].append(new_evaluation)
            
    def audit_inventory(self):
        """Envanteri denetler"""
        # Stok seviyeleri
        if random.random() < 0.2:  # %20 şans
            new_stock = {
                'product_id': len(self.scm_system['inventory']['stock_levels']) + 1,
                'quantity': random.randint(100, 1000),
                'location': random.choice(['depo1', 'depo2', 'depo3']),
                'value': random.uniform(1000, 10000)
            }
            self.scm_system['inventory']['stock_levels'].append(new_stock)
            
        # Siparişler
        if random.random() < 0.2:  # %20 şans
            new_order = {
                'order_id': len(self.scm_system['inventory']['orders']) + 1,
                'supplier_id': random.randint(1, len(self.scm_system['suppliers']['active_suppliers'])),
                'quantity': random.randint(10, 100),
                'status': random.choice(['beklemede', 'yolda', 'teslim edildi'])
            }
            self.scm_system['inventory']['orders'].append(new_order)
            
    def update_logistics(self):
        """Lojistik durumunu günceller"""
        # Sevkiyatlar
        if random.random() < 0.2:  # %20 şans
            new_shipment = {
                'shipment_id': len(self.scm_system['logistics']['shipments']) + 1,
                'from_location': random.choice(['depo1', 'depo2', 'depo3']),
                'to_location': random.choice(['müşteri1', 'müşteri2', 'müşteri3']),
                'status': random.choice(['yüklendi', 'yolda', 'teslim edildi'])
            }
            self.scm_system['logistics']['shipments'].append(new_shipment)
            
        # Rotalar
        if random.random() < 0.2:  # %20 şans
            new_route = {
                'route_id': len(self.scm_system['logistics']['routes']) + 1,
                'distance': random.uniform(10, 100),
                'duration': random.uniform(1, 5),
                'cost': random.uniform(100, 1000)
            }
            self.scm_system['logistics']['routes'].append(new_route)
            
    def assess_risks(self):
        """Riskleri değerlendirir"""
        # Riskler
        if random.random() < 0.2:  # %20 şans
            new_risk = {
                'risk_id': len(self.scm_system['risk_management']['risks']) + 1,
                'type': random.choice(['tedarik', 'lojistik', 'envanter', 'maliyet']),
                'probability': random.uniform(0.1, 0.5),
                'impact': random.uniform(0.1, 0.5)
            }
            self.scm_system['risk_management']['risks'].append(new_risk)
            
        # Risk azaltma önlemleri
        if random.random() < 0.2:  # %20 şans
            new_mitigation = {
                'risk_id': random.randint(1, len(self.scm_system['risk_management']['risks'])),
                'action': random.choice(['yedek tedarikçi', 'stok artırımı', 'alternatif rota']),
                'effectiveness': random.uniform(0.1, 1.0)
            }
            self.scm_system['risk_management']['mitigations'].append(new_mitigation)
            
    def show_scm_panel(self):
        """SCM panelini gösterir"""
        self.scm_panel.visible = True
        
        # Panel başlığı
        Text(
            parent=self.scm_panel,
            text='Tedarik Zinciri',
            position=(0, 0.15),
            scale=2,
            color=color.white
        )
        
        # Tedarikçiler
        y_pos = 0.05
        Text(
            parent=self.scm_panel,
            text=f"Aktif Tedarikçiler: {len(self.scm_system['suppliers']['active_suppliers'])}",
            position=(0, y_pos),
            scale=1.2,
            color=color.blue
        )
        y_pos -= 0.05
        
        # Envanter
        Text(
            parent=self.scm_panel,
            text=f"Stok Seviyeleri: {len(self.scm_system['inventory']['stock_levels'])}",
            position=(0, y_pos),
            scale=1.2,
            color=color.green
        )
        y_pos -= 0.05
        
        # Lojistik
        Text(
            parent=self.scm_panel,
            text=f"Aktif Sevkiyatlar: {len(self.scm_system['logistics']['shipments'])}",
            position=(0, y_pos),
            scale=1.2,
            color=color.yellow
        )
        y_pos -= 0.05
        
        # Risk yönetimi
        Text(
            parent=self.scm_panel,
            text=f"Aktif Riskler: {len(self.scm_system['risk_management']['risks'])}",
            position=(0, y_pos),
            scale=1.2,
            color=color.orange
        )
        y_pos -= 0.05
        
        # Tedarik zinciri performans skoru
        performance_score = (
            sum(s['reliability'] for s in self.scm_system['suppliers']['active_suppliers']) / max(1, len(self.scm_system['suppliers']['active_suppliers'])) * 0.4 +
            len(self.scm_system['inventory']['stock_levels']) / 100 * 0.3 +
            len(self.scm_system['logistics']['shipments']) / 50 * 0.2 +
            (1 - len(self.scm_system['risk_management']['risks']) / 10) * 0.1
        )
        Text(
            parent=self.scm_panel,
            text=f"Performans Skoru: {performance_score:.1f}/10",
            position=(0, y_pos),
            scale=1.2,
            color=color.red
        )
        
    def input(self, key):
        """Klavye girişlerini işler"""
        # ... existing code ...
        
        # SCM kontrolleri
        if key == 't':
            self.show_scm_panel()
            
    def update(self):
        """Her frame'de çalışacak güncelleme fonksiyonu"""
        # ... existing code ...
        
        # SCM sistemi güncellemesi
        self.update_scm_system()
        
        # PM sistemi güncellemesi
        self.update_pm_system()

    def update_pm_system(self):
        """Proje yönetim sistemini günceller"""
        current_time = time.time()
        
        # Proje gözden geçirmesi
        if current_time - self.pm_system['projects']['last_review'] >= self.pm_system['projects']['review_interval']:
            self.review_projects()
            self.pm_system['projects']['last_review'] = current_time
            
        # Kaynak kontrolü
        if current_time - self.pm_system['resources']['last_check'] >= self.pm_system['resources']['check_interval']:
            self.check_resources()
            self.pm_system['resources']['last_check'] = current_time
            
        # Zamanlama güncellemesi
        if current_time - self.pm_system['scheduling']['last_update'] >= self.pm_system['scheduling']['update_interval']:
            self.update_schedule()
            self.pm_system['scheduling']['last_update'] = current_time
            
        # Performans değerlendirmesi
        if current_time - self.pm_system['performance']['last_assessment'] >= self.pm_system['performance']['assessment_interval']:
            self.assess_performance()
            self.pm_system['performance']['last_assessment'] = current_time
            
    def review_projects(self):
        """Projeleri gözden geçirir"""
        # Yeni projeler
        if random.random() < 0.2:  # %20 şans
            new_project = {
                'id': len(self.pm_system['projects']['active_projects']) + 1,
                'name': f"Proje {len(self.pm_system['projects']['active_projects']) + 1}",
                'type': random.choice(['ürün', 'hizmet', 'altyapı', 'araştırma']),
                'budget': random.uniform(10000, 100000),
                'progress': random.uniform(0.1, 0.5)
            }
            self.pm_system['projects']['active_projects'].append(new_project)
            
        # Tamamlanan projeler
        for project in self.pm_system['projects']['active_projects'][:]:
            if project['progress'] >= 1.0:
                self.pm_system['projects']['completed_projects'].append(project)
                self.pm_system['projects']['active_projects'].remove(project)
                
    def check_resources(self):
        """Kaynakları kontrol eder"""
        # Ekipler
        if random.random() < 0.2:  # %20 şans
            new_team = {
                'id': len(self.pm_system['resources']['teams']) + 1,
                'name': f"Ekip {len(self.pm_system['resources']['teams']) + 1}",
                'size': random.randint(3, 10),
                'skills': random.sample(['planlama', 'geliştirme', 'test', 'dokümantasyon'], 2)
            }
            self.pm_system['resources']['teams'].append(new_team)
            
        # Ekipman
        if random.random() < 0.2:  # %20 şans
            new_equipment = {
                'id': len(self.pm_system['resources']['equipment']) + 1,
                'name': f"Ekipman {len(self.pm_system['resources']['equipment']) + 1}",
                'type': random.choice(['yazılım', 'donanım', 'laboratuvar', 'ofis']),
                'status': random.choice(['kullanımda', 'bakımda', 'yedek'])
            }
            self.pm_system['resources']['equipment'].append(new_equipment)
            
    def update_schedule(self):
        """Zamanlamayı günceller"""
        # Görevler
        if random.random() < 0.2:  # %20 şans
            new_task = {
                'id': len(self.pm_system['scheduling']['tasks']) + 1,
                'project_id': random.randint(1, len(self.pm_system['projects']['active_projects'])),
                'name': f"Görev {len(self.pm_system['scheduling']['tasks']) + 1}",
                'duration': random.uniform(1, 5),
                'status': random.choice(['beklemede', 'devam ediyor', 'tamamlandı'])
            }
            self.pm_system['scheduling']['tasks'].append(new_task)
            
        # Kilometre taşları
        if random.random() < 0.2:  # %20 şans
            new_milestone = {
                'id': len(self.pm_system['scheduling']['milestones']) + 1,
                'project_id': random.randint(1, len(self.pm_system['projects']['active_projects'])),
                'name': f"Kilometre Taşı {len(self.pm_system['scheduling']['milestones']) + 1}",
                'date': time.time() + random.uniform(86400, 604800),  # 1-7 gün
                'status': random.choice(['gelecek', 'yaklaşıyor', 'tamamlandı'])
            }
            self.pm_system['scheduling']['milestones'].append(new_milestone)
            
    def assess_performance(self):
        """Performansı değerlendirir"""
        # Metrikler
        if random.random() < 0.2:  # %20 şans
            new_metric = {
                'id': len(self.pm_system['performance']['metrics']) + 1,
                'project_id': random.randint(1, len(self.pm_system['projects']['active_projects'])),
                'type': random.choice(['zaman', 'maliyet', 'kalite', 'kapsam']),
                'value': random.uniform(0.1, 1.0)
            }
            self.pm_system['performance']['metrics'].append(new_metric)
            
        # Raporlar
        if random.random() < 0.2:  # %20 şans
            new_report = {
                'id': len(self.pm_system['performance']['reports']) + 1,
                'project_id': random.randint(1, len(self.pm_system['projects']['active_projects'])),
                'period': random.choice(['günlük', 'haftalık', 'aylık']),
                'status': random.choice(['iyi', 'orta', 'kötü'])
            }
            self.pm_system['performance']['reports'].append(new_report)
            
    def show_pm_panel(self):
        """PM panelini gösterir"""
        self.pm_panel.visible = True
        
        # Panel başlığı
        Text(
            parent=self.pm_panel,
            text='Proje Yönetimi',
            position=(0, 0.15),
            scale=2,
            color=color.white
        )
        
        # Projeler
        y_pos = 0.05
        Text(
            parent=self.pm_panel,
            text=f"Aktif Projeler: {len(self.pm_system['projects']['active_projects'])}",
            position=(0, y_pos),
            scale=1.2,
            color=color.blue
        )
        y_pos -= 0.05
        
        # Kaynaklar
        Text(
            parent=self.pm_panel,
            text=f"Ekipler: {len(self.pm_system['resources']['teams'])}",
            position=(0, y_pos),
            scale=1.2,
            color=color.green
        )
        y_pos -= 0.05
        
        # Zamanlama
        Text(
            parent=self.pm_panel,
            text=f"Aktif Görevler: {len(self.pm_system['scheduling']['tasks'])}",
            position=(0, y_pos),
            scale=1.2,
            color=color.yellow
        )
        y_pos -= 0.05
        
        # Performans
        Text(
            parent=self.pm_panel,
            text=f"Metrikler: {len(self.pm_system['performance']['metrics'])}",
            position=(0, y_pos),
            scale=1.2,
            color=color.orange
        )
        y_pos -= 0.05
        
        # Proje performans skoru
        performance_score = (
            sum(p['progress'] for p in self.pm_system['projects']['active_projects']) / max(1, len(self.pm_system['projects']['active_projects'])) * 0.4 +
            len(self.pm_system['resources']['teams']) / 10 * 0.2 +
            sum(1 for t in self.pm_system['scheduling']['tasks'] if t['status'] == 'tamamlandı') / max(1, len(self.pm_system['scheduling']['tasks'])) * 0.2 +
            sum(m['value'] for m in self.pm_system['performance']['metrics']) / max(1, len(self.pm_system['performance']['metrics'])) * 0.2
        ) * 10
        Text(
            parent=self.pm_panel,
            text=f"Performans Skoru: {performance_score:.1f}/10",
            position=(0, y_pos),
            scale=1.2,
            color=color.red
        )
        
    def input(self, key):
        """Klavye girişlerini işler"""
        # ... existing code ...
        
        # PM kontrolleri
        if key == 'p':
            self.show_pm_panel()
            
    def update(self):
        """Her frame'de çalışacak güncelleme fonksiyonu"""
        # ... existing code ...
        
        # PM sistemi güncellemesi
        self.update_pm_system()

    def update_hr_system(self):
        """İnsan kaynakları sistemini günceller"""
        current_time = time.time()
        
        # Personel güncellemesi
        if current_time - self.hr_system['personnel']['last_update'] >= self.hr_system['personnel']['update_interval']:
            self.update_personnel()
            self.hr_system['personnel']['last_update'] = current_time
            
        # Eğitim gözden geçirmesi
        if current_time - self.hr_system['training']['last_review'] >= self.hr_system['training']['review_interval']:
            self.review_training()
            self.hr_system['training']['last_review'] = current_time
            
        # Performans değerlendirmesi
        if current_time - self.hr_system['performance']['last_assessment'] >= self.hr_system['performance']['assessment_interval']:
            self.assess_performance()
            self.hr_system['performance']['last_assessment'] = current_time
            
        # Kariyer kontrolü
        if current_time - self.hr_system['career']['last_check'] >= self.hr_system['career']['check_interval']:
            self.check_career()
            self.hr_system['career']['last_check'] = current_time
            
    def update_personnel(self):
        """Personel verilerini günceller"""
        # Yeni çalışanlar
        if random.random() < 0.2:  # %20 şans
            new_employee = {
                'id': len(self.hr_system['personnel']['employees']) + 1,
                'name': f"Çalışan {len(self.hr_system['personnel']['employees']) + 1}",
                'department': random.choice(['üretim', 'pazarlama', 'satış', 'ar-ge']),
                'position': random.choice(['uzman', 'yönetici', 'müdür', 'direktör']),
                'salary': random.uniform(5000, 20000)
            }
            self.hr_system['personnel']['employees'].append(new_employee)
            
        # Departmanlar
        if random.random() < 0.2:  # %20 şans
            new_department = {
                'id': len(self.hr_system['personnel']['departments']) + 1,
                'name': f"Departman {len(self.hr_system['personnel']['departments']) + 1}",
                'size': random.randint(5, 20),
                'budget': random.uniform(100000, 500000)
            }
            self.hr_system['personnel']['departments'].append(new_department)
            
    def review_training(self):
        """Eğitim programlarını gözden geçirir"""
        # Eğitim programları
        if random.random() < 0.2:  # %20 şans
            new_program = {
                'id': len(self.hr_system['training']['programs']) + 1,
                'name': f"Eğitim {len(self.hr_system['training']['programs']) + 1}",
                'type': random.choice(['teknik', 'yönetim', 'kişisel gelişim']),
                'duration': random.uniform(1, 5),
                'cost': random.uniform(1000, 5000)
            }
            self.hr_system['training']['programs'].append(new_program)
            
        # Sertifikalar
        if random.random() < 0.2:  # %20 şans
            new_certification = {
                'id': len(self.hr_system['training']['certifications']) + 1,
                'employee_id': random.randint(1, len(self.hr_system['personnel']['employees'])),
                'name': f"Sertifika {len(self.hr_system['training']['certifications']) + 1}",
                'level': random.choice(['temel', 'orta', 'ileri'])
            }
            self.hr_system['training']['certifications'].append(new_certification)
            
    def assess_performance(self):
        """Performans değerlendirmesi yapar"""
        # Değerlendirmeler
        if random.random() < 0.2:  # %20 şans
            new_evaluation = {
                'id': len(self.hr_system['performance']['evaluations']) + 1,
                'employee_id': random.randint(1, len(self.hr_system['personnel']['employees'])),
                'score': random.uniform(1, 5),
                'criteria': random.choice(['iş kalitesi', 'verimlilik', 'takım çalışması', 'liderlik'])
            }
            self.hr_system['performance']['evaluations'].append(new_evaluation)
            
        # Ödüller
        if random.random() < 0.2:  # %20 şans
            new_reward = {
                'id': len(self.hr_system['performance']['rewards']) + 1,
                'employee_id': random.randint(1, len(self.hr_system['personnel']['employees'])),
                'type': random.choice(['prim', 'terfi', 'plaket', 'izin']),
                'value': random.uniform(1000, 10000)
            }
            self.hr_system['performance']['rewards'].append(new_reward)
            
    def check_career(self):
        """Kariyer gelişimini kontrol eder"""
        # Kariyer yolları
        if random.random() < 0.2:  # %20 şans
            new_path = {
                'id': len(self.hr_system['career']['paths']) + 1,
                'employee_id': random.randint(1, len(self.hr_system['personnel']['employees'])),
                'current_level': random.choice(['junior', 'mid', 'senior']),
                'next_level': random.choice(['mid', 'senior', 'lead']),
                'progress': random.uniform(0.1, 0.9)
            }
            self.hr_system['career']['paths'].append(new_path)
            
        # Terfiler
        if random.random() < 0.2:  # %20 şans
            new_promotion = {
                'id': len(self.hr_system['career']['promotions']) + 1,
                'employee_id': random.randint(1, len(self.hr_system['personnel']['employees'])),
                'from_position': random.choice(['uzman', 'yönetici', 'müdür']),
                'to_position': random.choice(['yönetici', 'müdür', 'direktör']),
                'date': time.time()
            }
            self.hr_system['career']['promotions'].append(new_promotion)
            
    def show_hr_panel(self):
        """HR panelini gösterir"""
        self.hr_panel.visible = True
        
        # Panel başlığı
        Text(
            parent=self.hr_panel,
            text='İnsan Kaynakları',
            position=(0, 0.15),
            scale=2,
            color=color.white
        )
        
        # Personel
        y_pos = 0.05
        Text(
            parent=self.hr_panel,
            text=f"Toplam Çalışan: {len(self.hr_system['personnel']['employees'])}",
            position=(0, y_pos),
            scale=1.2,
            color=color.blue
        )
        y_pos -= 0.05
        
        # Eğitim
        Text(
            parent=self.hr_panel,
            text=f"Aktif Eğitimler: {len(self.hr_system['training']['programs'])}",
            position=(0, y_pos),
            scale=1.2,
            color=color.green
        )
        y_pos -= 0.05
        
        # Performans
        Text(
            parent=self.hr_panel,
            text=f"Değerlendirmeler: {len(self.hr_system['performance']['evaluations'])}",
            position=(0, y_pos),
            scale=1.2,
            color=color.yellow
        )
        y_pos -= 0.05
        
        # Kariyer
        Text(
            parent=self.hr_panel,
            text=f"Terfiler: {len(self.hr_system['career']['promotions'])}",
            position=(0, y_pos),
            scale=1.2,
            color=color.orange
        )
        y_pos -= 0.05
        
        # İK performans skoru
        hr_score = (
            len(self.hr_system['personnel']['employees']) / 100 * 0.3 +
            sum(p['score'] for p in self.hr_system['performance']['evaluations']) / max(1, len(self.hr_system['performance']['evaluations'])) * 0.3 +
            sum(p['progress'] for p in self.hr_system['career']['paths']) / max(1, len(self.hr_system['career']['paths'])) * 0.2 +
            len(self.hr_system['training']['certifications']) / 50 * 0.2
        ) * 10
        Text(
            parent=self.hr_panel,
            text=f"İK Skoru: {hr_score:.1f}/10",
            position=(0, y_pos),
            scale=1.2,
            color=color.red
        )
        
    def input(self, key):
        """Klavye girişlerini işler"""
        # ... existing code ...
        
        # HR kontrolleri
        if key == 'h':
            self.show_hr_panel()
            
    def update(self):
        """Her frame'de çalışacak güncelleme fonksiyonu"""
        # ... existing code ...
        
        # HR sistemi güncellemesi
        self.update_hr_system()

    def set_player_age(self, age):
        """Oyuncunun yaşını ayarlar ve önerilen süreleri günceller"""
        self.health_system['player_age'] = age
        
        # Yaşa göre önerilen süreleri ayarla
        if age < 12:
            self.health_system['recommended_play_time'] = 3600  # 1 saat
            self.health_system['recommended_break_interval'] = 900  # 15 dakika
            self.health_system['break_duration'] = 300  # 5 dakika
        elif age < 18:
            self.health_system['recommended_play_time'] = 7200  # 2 saat
            self.health_system['recommended_break_interval'] = 1800  # 30 dakika
            self.health_system['break_duration'] = 300  # 5 dakika
        else:
            self.health_system['recommended_play_time'] = 10800  # 3 saat
            self.health_system['recommended_break_interval'] = 2700  # 45 dakika
            self.health_system['break_duration'] = 300  # 5 dakika
            
    def update_health_system(self):
        """Sağlık sistemini günceller"""
        current_time = time.time()
        
        # Oyun süresini güncelle
        self.health_system['play_time'] = current_time - self.start_time
        
        # Mola kontrolü
        if current_time - self.health_system['last_break'] >= self.health_system['recommended_break_interval']:
            self.show_break_notification()
            self.health_system['last_break'] = current_time
            self.health_system['break_time'] += self.health_system['break_duration']
            
        # Sağlık tavsiyeleri güncelle
        if len(self.health_system['health_tips']) < 5:
            self.generate_health_tips()
            
    def show_break_notification(self):
        """Mola bildirimi gösterir"""
        self.show_notification(
            "Mola zamanı! Lütfen 5 dakika ara verin ve şunları yapın:\n"
            "1. Gözlerinizi dinlendirin\n"
            "2. Esneme hareketleri yapın\n"
            "3. Su için\n"
            "4. Kısa bir yürüyüş yapın",
            duration=10
        )
        
    def generate_health_tips(self):
        """Sağlıklı yaşam tavsiyeleri oluşturur"""
        tips = [
            "Düzenli egzersiz yapın - günde en az 30 dakika",
            "Sağlıklı beslenin - meyve ve sebze tüketin",
            "Yeterli uyku alın - günde 7-9 saat",
            "Su tüketimine dikkat edin - günde 2-3 litre",
            "Göz sağlığınız için ekranla aranıza mesafe bırakın",
            "Duruşunuza dikkat edin - düz oturun",
            "Stres yönetimi için meditasyon yapın",
            "Sosyal ilişkilerinizi güçlendirin",
            "Zihinsel aktiviteler yapın - kitap okuyun",
            "Düzenli sağlık kontrolleri yaptırın"
        ]
        
        # Rastgele 5 tavsiye seç
        selected_tips = random.sample(tips, 5)
        self.health_system['health_tips'] = selected_tips
        
    def show_health_panel(self):
        """Sağlık panelini gösterir"""
        self.health_panel.visible = True
        
        # Panel başlığı
        Text(
            parent=self.health_panel,
            text='Sağlık Yönetimi',
            position=(0, 0.15),
            scale=2,
            color=color.white
        )
        
        # Yaş bilgisi
        y_pos = 0.05
        Text(
            parent=self.health_panel,
            text=f"Yaş: {self.health_system['player_age']}",
            position=(0, y_pos),
            scale=1.2,
            color=color.blue
        )
        y_pos -= 0.05
        
        # Oyun süresi
        play_time_minutes = self.health_system['play_time'] / 60
        Text(
            parent=self.health_panel,
            text=f"Oyun Süresi: {play_time_minutes:.0f} dakika",
            position=(0, y_pos),
            scale=1.2,
            color=color.green
        )
        y_pos -= 0.05
        
        # Mola süresi
        break_time_minutes = self.health_system['break_time'] / 60
        Text(
            parent=self.health_panel,
            text=f"Mola Süresi: {break_time_minutes:.0f} dakika",
            position=(0, y_pos),
            scale=1.2,
            color=color.yellow
        )
        y_pos -= 0.05
        
        # Sağlık tavsiyeleri
        Text(
            parent=self.health_panel,
            text="Sağlık Tavsiyeleri:",
            position=(0, y_pos),
            scale=1.2,
            color=color.orange
        )
        y_pos -= 0.05
        
        for tip in self.health_system['health_tips']:
            Text(
                parent=self.health_panel,
                text=f"- {tip}",
                position=(0, y_pos),
                scale=0.8,
                color=color.white
            )
            y_pos -= 0.03
            
    def input(self, key):
        """Klavye girişlerini işler"""
        # ... existing code ...
        
        # Sağlık kontrolleri
        if key == 'h':
            self.show_health_panel()
            
    def update(self):
        """Her frame'de çalışacak güncelleme fonksiyonu"""
        # ... existing code ...
        
        # Sağlık sistemi güncellemesi
        self.update_health_system()

    def update_exercise_system(self):
        """Egzersiz sistemini günceller"""
        current_time = time.time()
        
        # Egzersiz hatırlatması
        if current_time - self.exercise_system['last_exercise'] >= self.exercise_system['exercise_interval']:
            self.show_exercise_notification()
            self.exercise_system['last_exercise'] = current_time
            
        # Mevcut egzersizleri güncelle
        if len(self.exercise_system['current_exercises']) < 3:
            self.generate_exercises()
            
    def show_exercise_notification(self):
        """Egzersiz bildirimi gösterir"""
        exercises = self.generate_exercises()
        exercise_text = "Egzersiz zamanı! Şu hareketleri yapın:\n"
        for i, exercise in enumerate(exercises, 1):
            exercise_text += f"{i}. {exercise}\n"
            
        self.show_notification(
            exercise_text + "\nHer hareketi 30 saniye yapın ve 10 saniye dinlenin.",
            duration=15
        )
        
    def generate_exercises(self):
        """Yeni egzersizler oluşturur"""
        exercises = []
        # Her kategoriden bir egzersiz seç
        for category in ['stretching', 'strength', 'cardio']:
            exercise = random.choice(self.exercise_system['exercise_types'][category])
            exercises.append(exercise)
            
        self.exercise_system['current_exercises'] = exercises
        return exercises
        
    def show_exercise_panel(self):
        """Egzersiz panelini gösterir"""
        self.exercise_panel.visible = True
        
        # Panel başlığı
        Text(
            parent=self.exercise_panel,
            text='Egzersiz Programı',
            position=(0, 0.15),
            scale=2,
            color=color.white
        )
        
        # Son egzersiz zamanı
        y_pos = 0.05
        last_exercise_minutes = (time.time() - self.exercise_system['last_exercise']) / 60
        Text(
            parent=self.exercise_panel,
            text=f"Son Egzersiz: {last_exercise_minutes:.0f} dakika önce",
            position=(0, y_pos),
            scale=1.2,
            color=color.blue
        )
        y_pos -= 0.05
        
        # Günlük egzersiz hedefi
        Text(
            parent=self.exercise_panel,
            text="Günlük Hedef: 30 dakika",
            position=(0, y_pos),
            scale=1.2,
            color=color.green
        )
        y_pos -= 0.05
        
        # Mevcut egzersizler
        Text(
            parent=self.exercise_panel,
            text="Güncel Egzersizler:",
            position=(0, y_pos),
            scale=1.2,
            color=color.yellow
        )
        y_pos -= 0.05
        
        for exercise in self.exercise_system['current_exercises']:
            Text(
                parent=self.exercise_panel,
                text=f"- {exercise}",
                position=(0, y_pos),
                scale=0.8,
                color=color.white
            )
            y_pos -= 0.03
            
        # Egzersiz önerileri
        Text(
            parent=self.exercise_panel,
            text="Öneriler:",
            position=(0, y_pos),
            scale=1.2,
            color=color.orange
        )
        y_pos -= 0.05
        
        tips = [
            "Her saat başı 5 dakika egzersiz yapın",
            "Egzersiz öncesi ısınma hareketleri yapın",
            "Egzersiz sonrası esneme hareketleri yapın",
            "Düzenli su tüketin",
            "Doğru nefes almayı unutmayın"
        ]
        
        for tip in tips:
            Text(
                parent=self.exercise_panel,
                text=f"- {tip}",
                position=(0, y_pos),
                scale=0.8,
                color=color.white
            )
            y_pos -= 0.03
            
    def input(self, key):
        """Klavye girişlerini işler"""
        # ... existing code ...
        
        # Egzersiz kontrolleri
        if key == 'e':
            self.show_exercise_panel()
            
    def update(self):
        """Her frame'de çalışacak güncelleme fonksiyonu"""
        # ... existing code ...
        
        # Egzersiz sistemi güncellemesi
        self.update_exercise_system()

if __name__ == '__main__':
    app = FinAsisGame(1)
    app.run() 