# -*- coding: utf-8 -*-
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

# Django ayarlarÄ±nÄ± yÃ¼kle
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
# django.setup() satÄ±rÄ± kaldÄ±rÄ±ldÄ± - circular import sorununa yol aÃ§Ä±yor

# Oyun iÃ§indeki ÅŸirket modelleri yerine sÄ±nÄ±flar kullan
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

# Oyun ayarlarÄ±
game_settings = {
    'difficulty': 'normal',  # easy, normal, hard
    'market_update_interval': 5,  # saniye
    'event_chance': 0.2,  # 0-1 arasÄ±
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
    'volatility': 0.5,  # 0-1 arasÄ±
    'last_update': datetime.now(),
    'market_events': []
}

# UI bileÅŸenleri
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
        'debt_to_income': 0.0,  # BorÃ§/gelir oranÄ±
        'portfolio_diversity': 0.0,  # PortfÃ¶y Ã§eÅŸitliliÄŸi
        'total_debt': 0,  # Toplam borÃ§
        'total_income': 0,  # Toplam gelir
        'monthly_income': 0,  # AylÄ±k gelir
        'monthly_expenses': 0  # AylÄ±k giderler
    },
    'skills': {
        'analysis': 1,  # 1-10 arasÄ±
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

# GÃ¶rev sistemi
quest_system = {
    'daily_quests': [],
    'weekly_quests': [],
    'achievement_quests': [],
    'tutorial_quests': []
}

# GÃ¶rev tanÄ±mlamalarÄ±
quest_definitions = {
    # GÃ¼nlÃ¼k gÃ¶revler
    'daily_trade': {
        'id': 'daily_trade',
        'title': 'GÃ¼nlÃ¼k Ä°ÅŸlem',
        'description': 'BugÃ¼n en az 1 hisse senedi alÄ±m veya satÄ±m iÅŸlemi yapÄ±n.',
        'reward': {'money': 500, 'experience': 100},
        'type': 'daily',
        'check_completion': lambda: len([t for t in player['trading_history'] if (datetime.now() - t['timestamp']).days < 1]) > 0
    },
    'daily_profit': {
        'id': 'daily_profit',
        'title': 'GÃ¼nlÃ¼k KÃ¢r',
        'description': 'BugÃ¼n portfÃ¶yÃ¼nÃ¼zden 1000$ kÃ¢r elde edin.',
        'reward': {'money': 1000, 'experience': 200},
        'type': 'daily',
        'check_completion': lambda: calculate_daily_profit() >= 1000
    },
    'daily_diversity': {
        'id': 'daily_diversity',
        'title': 'Ã‡eÅŸitlilik UstasÄ±',
        'description': 'PortfÃ¶y Ã§eÅŸitliliÄŸinizi 0.7\'nin Ã¼zerine Ã§Ä±karÄ±n.',
        'reward': {'money': 800, 'experience': 150},
        'type': 'daily',
        'check_completion': lambda: player['stats']['portfolio_diversity'] > 0.7
    },
    
    # HaftalÄ±k gÃ¶revler
    'weekly_growth': {
        'id': 'weekly_growth',
        'title': 'HaftalÄ±k BÃ¼yÃ¼me',
        'description': 'PortfÃ¶yÃ¼nÃ¼zÃ¼ bu hafta %10 bÃ¼yÃ¼tÃ¼n.',
        'reward': {'money': 5000, 'experience': 500},
        'type': 'weekly',
        'check_completion': lambda: calculate_weekly_growth() >= 0.1
    },
    'weekly_trades': {
        'id': 'weekly_trades',
        'title': 'Aktif Trader',
        'description': 'Bu hafta en az 10 iÅŸlem yapÄ±n.',
        'reward': {'money': 3000, 'experience': 400},
        'type': 'weekly',
        'check_completion': lambda: len([t for t in player['trading_history'] if (datetime.now() - t['timestamp']).days < 7]) >= 10
    },
    'weekly_risk': {
        'id': 'weekly_risk',
        'title': 'Risk YÃ¶neticisi',
        'description': 'Risk skorunuzu 0.5\'in altÄ±na dÃ¼ÅŸÃ¼rÃ¼n.',
        'reward': {'money': 4000, 'experience': 450},
        'type': 'weekly',
        'check_completion': lambda: calculate_risk_score() < 0.5
    },
    
    # BaÅŸarÄ± gÃ¶revleri
    'achievement_portfolio': {
        'id': 'achievement_portfolio',
        'title': 'PortfÃ¶y UstasÄ±',
        'description': 'PortfÃ¶yÃ¼nÃ¼zÃ¼ 200.000$ deÄŸerine ulaÅŸtÄ±rÄ±n.',
        'reward': {'money': 10000, 'experience': 1000, 'achievement': 'portfolio_master'},
        'type': 'achievement',
        'check_completion': lambda: calculate_portfolio_value() >= 200000
    },
    'achievement_diversity': {
        'id': 'achievement_diversity',
        'title': 'Ã‡eÅŸitlilik KralÄ±',
        'description': 'PortfÃ¶y Ã§eÅŸitliliÄŸinizi 0.9\'un Ã¼zerine Ã§Ä±karÄ±n.',
        'reward': {'money': 8000, 'experience': 800, 'achievement': 'diversity_king'},
        'type': 'achievement',
        'check_completion': lambda: player['stats']['portfolio_diversity'] > 0.9
    },
    'achievement_debt': {
        'id': 'achievement_debt',
        'title': 'BorÃ§suz YaÅŸam',
        'description': 'BorÃ§/gelir oranÄ±nÄ±zÄ± 0.1\'in altÄ±na dÃ¼ÅŸÃ¼rÃ¼n.',
        'reward': {'money': 6000, 'experience': 600, 'achievement': 'debt_free'},
        'type': 'achievement',
        'check_completion': lambda: player['stats']['debt_to_income'] < 0.1
    },
    
    # EÄŸitim gÃ¶revleri
    'tutorial_buy': {
        'id': 'tutorial_buy',
        'title': 'Ä°lk AlÄ±m',
        'description': 'Ä°lk hisse senedi alÄ±m iÅŸleminizi yapÄ±n.',
        'reward': {'money': 1000, 'experience': 200},
        'type': 'tutorial',
        'check_completion': lambda: len([t for t in player['trading_history'] if t['type'] == 'buy']) > 0
    },
    'tutorial_sell': {
        'id': 'tutorial_sell',
        'title': 'Ä°lk SatÄ±m',
        'description': 'Ä°lk hisse senedi satÄ±m iÅŸleminizi yapÄ±n.',
        'reward': {'money': 1000, 'experience': 200},
        'type': 'tutorial',
        'check_completion': lambda: len([t for t in player['trading_history'] if t['type'] == 'sell']) > 0
    },
    'tutorial_diversity': {
        'id': 'tutorial_diversity',
        'title': 'Ã‡eÅŸitlendirme',
        'description': 'En az 3 farklÄ± hisse senedine yatÄ±rÄ±m yapÄ±n.',
        'reward': {'money': 2000, 'experience': 300},
        'type': 'tutorial',
        'check_completion': lambda: len([s for s in player['portfolio'].values() if s['shares'] > 0]) >= 3
    }
}

# GÃ¶rev UI elementleri
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
        
        # Dil yÃ¶neticisi
        self.locale_manager = LocaleManager()
        
        # Platform kontrolÃ¼
        self.platform = self.oyun.platform
        self.is_mobile = self.platform in ['android', 'ios']
        
        # AR yÃ¶neticisini baÅŸlat (mobil platformlarda)
        if self.is_mobile:
            self.ar_manager = ARManager(use_aruco=True, show_camera=True)
            self.ar_manager.start()
            
        # DÃ¼nya oluÅŸturma
        self.dunya = Entity(
            model='plane',
            texture='white_cube',
            scale=(100, 1, 100),
            color=color.gray
        )
        
        # Binalar ve iÅŸ yerleri
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
        
        # TuÅŸ durumlarÄ±
        self.held_keys = {'w': False, 'a': False, 's': False, 'd': False, 'left mouse': False, 'right mouse': False}
        
        # Ä°nitialize
        self.bina_olustur()
        self.is_yeri_olustur()
        self.olay_olustur()
        self.ui_olustur()
        
        # Otomatik kayÄ±t
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
        
        # Bakiye gÃ¶stergesi
        self.ui_elements['bakiye'] = Text(
            parent=self.ui_elements['ana_panel'],
            text=f"{self.locale_manager.get_text('game.stats.balance')}: ${self.oyun.oyuncu_bakiyesi:,.2f}",
            position=(-0.4, 0.4),
            scale=2,
            color=color.green
        )
        
        # Puan gÃ¶stergesi
        self.ui_elements['puan'] = Text(
            parent=self.ui_elements['ana_panel'],
            text=f"{self.locale_manager.get_text('game.stats.score')}: {self.oyun.oyuncu_puani}",
            position=(0.4, 0.4),
            scale=2,
            color=color.yellow
        )
        
        # Seviye gÃ¶stergesi
        self.ui_elements['seviye'] = Text(
            parent=self.ui_elements['ana_panel'],
            text=f"{self.locale_manager.get_text('game.stats.level')}: {self.oyun.oyuncu_seviyesi}",
            position=(0, 0.4),
            scale=2,
            color=color.azure
        )
        
        # Ä°ÅŸlem butonlarÄ±
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
        
        # MenÃ¼ butonu
        self.ui_elements['menu_buton'] = Button(
            parent=camera.ui,
            text=self.locale_manager.get_text('game.menu.settings'),
            color=color.azure,
            position=(0.8, 0.45),
            scale=(0.2, 0.05),
            on_click=self.toggle_menu
        )
        
        # Dil seÃ§imi butonu
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
        """Dil seÃ§imini deÄŸiÅŸtir"""
        available_locales = self.locale_manager.get_available_locales()
        current_index = available_locales.index(self.locale_manager.get_current_locale())
        next_index = (current_index + 1) % len(available_locales)
        self.locale_manager.set_locale(available_locales[next_index])
        
        # UI'Ä± gÃ¼ncelle
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
        """MenÃ¼yÃ¼ aÃ§/kapat"""
        self.is_paused = not self.is_paused
        
        if self.is_paused:
            # MenÃ¼ panelini gÃ¶ster
            self.ui_elements['menu_panel'] = Entity(
                parent=camera.ui,
                model='quad',
                scale=(0.4, 0.6),
                position=(0, 0),
                color=color.rgba(0, 0, 0, 0.9)
            )
            
            # MenÃ¼ butonlarÄ±
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
                text='YÃ¼kle',
                color=color.azure,
                position=(0, 0),
                scale=(0.3, 0.05),
                on_click=self.oyun.load_game
            )
            
            Button(
                parent=self.ui_elements['menu_panel'],
                text='Ã‡Ä±kÄ±ÅŸ',
                color=color.red,
                position=(0, -0.2),
                scale=(0.3, 0.05),
                on_click=application.quit
            )
        else:
            # MenÃ¼ panelini kaldÄ±r
            if 'menu_panel' in self.ui_elements:
                destroy(self.ui_elements['menu_panel'])
                del self.ui_elements['menu_panel']
        
    def update(self):
        # Performans kontrolÃ¼
        current_time = time.time()
        if current_time - self.last_update < self.update_interval:
            return
        self.last_update = current_time
        
        if self.is_paused:
            return
            
        # Oyun gÃ¼ncellemeleri
        if self.held_keys['left mouse']:
            self.alis_yap()
            
        if self.held_keys['right mouse']:
            self.satis_yap()
            
        # AR gÃ¼ncellemeleri
        if self.is_mobile:
            self.ar_manager.ar_nesne_guncelle()
            
        # Olay gÃ¼ncellemeleri
        self.olay_guncelle()
        
    def olay_guncelle(self):
        simdiki_zaman = time.time()
        for olay in self.olaylar:
            if simdiki_zaman - olay['baslangic'] > olay['sure']:
                # Olay sÃ¼resi doldu, yeni olay oluÅŸtur
                olay['tip'] = random.choice([
                    'Borsa YÃ¼kseliÅŸi', 'Borsa DÃ¼ÅŸÃ¼ÅŸÃ¼',
                    'Enflasyon ArtÄ±ÅŸÄ±', 'Enflasyon DÃ¼ÅŸÃ¼ÅŸÃ¼',
                    'Faiz ArtÄ±ÅŸÄ±', 'Faiz DÃ¼ÅŸÃ¼ÅŸÃ¼',
                    'DÃ¶viz DalgalanmasÄ±', 'AltÄ±n FiyatÄ± DeÄŸiÅŸimi'
                ])
                olay['etki'] = random.uniform(-0.2, 0.2)
                olay['baslangic'] = simdiki_zaman
                
                # Olay bildirimi
                self.ui_elements['bildirim'].text = f"Yeni Olay: {olay['tip']}"
                self.ui_elements['bildirim'].color = color.yellow

def run_game(online_mode: bool = False):
    """Oyunu baÅŸlat"""
    app = Ursina()
    dunya = FinansalDunya(online_mode=online_mode)
    app.run()

def create_ui():
    """Ana UI'Ä± oluÅŸtur"""
    # Ana panel
    ui['main_panel'] = Entity(
        parent=camera.ui,
        model='quad',
        scale=(1.8, 1),
        position=(0, 0),
        color=color.rgba(0, 0, 0, 0.8)
    )
    
    # Ãœst bilgi paneli
    create_top_info_panel()
    
    # PortfÃ¶y paneli
    create_portfolio_panel()
    
    # Market paneli
    create_market_panel()
    
    # Ä°statistik paneli
    create_stats_panel()
    
    # MenÃ¼ butonu
    Button(
        parent=camera.ui,
        text='MenÃ¼',
        color=color.azure,
        position=(0.8, 0.45),
        scale=(0.2, 0.05),
        on_click=Func(toggle_menu)
    )

def create_top_info_panel():
    """Ãœst bilgi panelini oluÅŸtur"""
    # Para
    ui['text_elements']['money'] = Text(
        parent=camera.ui,
        text=f"${player['money']:,.2f}",
        position=(-0.8, 0.45),
        scale=2,
        color=color.green
    )
    
    # PortfÃ¶y deÄŸeri
    ui['text_elements']['portfolio_value'] = Text(
        parent=camera.ui,
        text=f"PortfÃ¶y: ${calculate_portfolio_value():,.2f}",
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
    """PortfÃ¶y panelini oluÅŸtur"""
    ui['portfolio_panel'] = Entity(
        parent=ui['main_panel'],
        model='quad',
        scale=(0.5, 0.8),
        position=(-0.6, -0.05),
        color=color.rgba(0, 0, 0, 0.5)
    )
    
    # BaÅŸlÄ±k
    Text(
        parent=ui['portfolio_panel'],
        text='PortfÃ¶y',
        position=(0, 0.35),
        scale=2,
        color=color.white
    )
    
    # Hisse senetleri listesi
    y_pos = 0.25
    for symbol, data in player['portfolio'].items():
        if data['shares'] > 0:
            # Hisse adÄ± ve miktar
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
    """Market panelini oluÅŸtur"""
    ui['market_panel'] = Entity(
        parent=ui['main_panel'],
        model='quad',
        scale=(0.5, 0.8),
        position=(0, -0.05),
        color=color.rgba(0, 0, 0, 0.5)
    )
    
    # BaÅŸlÄ±k
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
        # Hisse adÄ± ve fiyat
        Text(
            parent=ui['market_panel'],
            text=f"{symbol}: ${data['price']:,.2f}",
            position=(-0.2, y_pos),
            scale=1.2,
            color=color.white
        )
        
        # AlÄ±m butonu
        Button(
            parent=ui['market_panel'],
            text='Al',
            color=color.green,
            position=(0.1, y_pos),
            scale=(0.1, 0.04),
            on_click=Func(lambda s=symbol: buy_stock(s))
        )
        
        # SatÄ±m butonu
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
    """Ä°statistik panelini oluÅŸtur"""
    ui['stats_panel'] = Entity(
        parent=ui['main_panel'],
        model='quad',
        scale=(0.5, 0.8),
        position=(0.6, -0.05),
        color=color.rgba(0, 0, 0, 0.5)
    )
    
    # BaÅŸlÄ±k
    Text(
        parent=ui['stats_panel'],
        text='Ä°statistikler',
        position=(0, 0.35),
        scale=2,
        color=color.white
    )
    
    # Ä°statistikler
    stats = player['stats']
    y_pos = 0.25
    
    # Toplam iÅŸlem
    Text(
        parent=ui['stats_panel'],
        text=f"Toplam Ä°ÅŸlem: {stats['total_trades']}",
        position=(0, y_pos),
        scale=1.2,
        color=color.white
    )
    y_pos -= 0.08
    
    # BaÅŸarÄ±lÄ± iÅŸlemler
    Text(
        parent=ui['stats_panel'],
        text=f"BaÅŸarÄ±lÄ±: {stats['successful_trades']}",
        position=(0, y_pos),
        scale=1.2,
        color=color.green
    )
    y_pos -= 0.08
    
    # BaÅŸarÄ±sÄ±z iÅŸlemler
    Text(
        parent=ui['stats_panel'],
        text=f"BaÅŸarÄ±sÄ±z: {stats['failed_trades']}",
        position=(0, y_pos),
        scale=1.2,
        color=color.red
    )
    y_pos -= 0.08
    
    # Toplam kÃ¢r
    Text(
        parent=ui['stats_panel'],
        text=f"Toplam KÃ¢r: ${stats['total_profit']:,.2f}",
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
    """MenÃ¼yÃ¼ aÃ§/kapat"""
    if not ui['menu_panel']:
        create_menu()
    else:
        destroy(ui['menu_panel'])
        ui['menu_panel'] = None

def create_menu():
    """MenÃ¼ panelini oluÅŸtur"""
    ui['menu_panel'] = Entity(
        parent=camera.ui,
        model='quad',
        scale=(0.4, 0.6),
        position=(0, 0),
        color=color.rgba(0, 0, 0, 0.9)
    )
    
    # BaÅŸlÄ±k
    Text(
        parent=ui['menu_panel'],
        text='MenÃ¼',
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
    
    # YÃ¼kle butonu
    Button(
        parent=ui['menu_panel'],
        text='YÃ¼kle',
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
    
    # Ã‡Ä±kÄ±ÅŸ butonu
    Button(
        parent=ui['menu_panel'],
        text='Ã‡Ä±kÄ±ÅŸ',
        color=color.red,
        position=(0, -0.2),
        scale=(0.3, 0.05),
        on_click=Func(quit_game)
    )

def show_settings():
    """Ayarlar menÃ¼sÃ¼nÃ¼ gÃ¶ster"""
    # Mevcut menÃ¼yÃ¼ kapat
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
    
    # BaÅŸlÄ±k
    Text(
        parent=ui['settings_panel'],
        text='Ayarlar',
        position=(0, 0.25),
        scale=2,
        color=color.white
    )
    
    # Ses ayarÄ±
    Button(
        parent=ui['settings_panel'],
        text=f"Ses: {'AÃ§Ä±k' if game_settings['sound_enabled'] else 'KapalÄ±'}",
        color=color.azure,
        position=(0, 0.1),
        scale=(0.3, 0.05),
        on_click=Func(toggle_sound)
    )
    
    # MÃ¼zik ayarÄ±
    Button(
        parent=ui['settings_panel'],
        text=f"MÃ¼zik: {'AÃ§Ä±k' if game_settings['music_enabled'] else 'KapalÄ±'}",
        color=color.azure,
        position=(0, 0),
        scale=(0.3, 0.05),
        on_click=Func(toggle_music)
    )
    
    # Tam ekran ayarÄ±
    Button(
        parent=ui['settings_panel'],
        text=f"Tam Ekran: {'AÃ§Ä±k' if game_settings['fullscreen'] else 'KapalÄ±'}",
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
    """Ses ayarÄ±nÄ± deÄŸiÅŸtir"""
    game_settings['sound_enabled'] = not game_settings['sound_enabled']
    show_settings()  # Ayarlar menÃ¼sÃ¼nÃ¼ yenile

def toggle_music():
    """MÃ¼zik ayarÄ±nÄ± deÄŸiÅŸtir"""
    game_settings['music_enabled'] = not game_settings['music_enabled']
    show_settings()  # Ayarlar menÃ¼sÃ¼nÃ¼ yenile

def toggle_fullscreen():
    """Tam ekran ayarÄ±nÄ± deÄŸiÅŸtir"""
    game_settings['fullscreen'] = not game_settings['fullscreen']
    window.fullscreen = game_settings['fullscreen']
    show_settings()  # Ayarlar menÃ¼sÃ¼nÃ¼ yenile

def start_tutorial():
    """EÄŸitim modunu baÅŸlat"""
    tutorial_steps = [
        {
            'title': 'HoÅŸ Geldiniz!',
            'description': 'FinAsis finansal eÄŸitim simÃ¼lasyonuna hoÅŸ geldiniz. Size temel Ã¶zellikleri tanÄ±tacaÄŸÄ±m.',
            'position': (0, 0)
        },
        {
            'title': 'PortfÃ¶y Paneli',
            'description': 'Bu panel sahip olduÄŸunuz hisse senetlerini gÃ¶sterir.',
            'position': (-0.65, 0)
        },
        {
            'title': 'Market Paneli',
            'description': 'Bu panel piyasadaki hisse senetlerini ve fiyatlarÄ±nÄ± gÃ¶sterir.',
            'position': (0, 0)
        },
        {
            'title': 'Ä°statistik Paneli',
            'description': 'Bu panel trading performansÄ±nÄ±zÄ± gÃ¶sterir.',
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
        
        # BaÅŸlÄ±k
        if hasattr(tutorial_panel, 'title'):
            destroy(tutorial_panel.title)
        tutorial_panel.title = Text(
            parent=tutorial_panel,
            text=step['title'],
            position=(0, 0.05),
            scale=1.5,
            color=color.yellow
        )
        
        # AÃ§Ä±klama
        if hasattr(tutorial_panel, 'description'):
            destroy(tutorial_panel.description)
        tutorial_panel.description = Text(
            parent=tutorial_panel,
            text=step['description'],
            position=(0, -0.02),
            scale=1,
            color=color.white
        )
        
        # Ä°leri butonu
        if hasattr(tutorial_panel, 'next_button'):
            destroy(tutorial_panel.next_button)
        tutorial_panel.next_button = Button(
            parent=tutorial_panel,
            text='Ä°leri' if current_step < len(tutorial_steps) - 1 else 'Bitir',
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
            # Tutorial'Ä± bitir
            destroy(tutorial_panel)
            player['tutorial_progress']['basic_trading'] = True
            save_game()
    
    # Ä°lk adÄ±mÄ± gÃ¶ster
    show_step()

def save_game():
    """Oyun durumunu kaydet"""
    try:
        # Kaydedilecek verileri hazÄ±rla
        save_data = {
            'player': player,
            'market_state': market_state,
            'quest_system': quest_system,
            'game_settings': game_settings,
            'save_time': datetime.now().isoformat()
        }
        
        # datetime nesnelerini ISO formatÄ±na dÃ¶nÃ¼ÅŸtÃ¼r
        def convert_datetime(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            return obj
        
        # Verileri JSON formatÄ±nda kaydet
        with open('save_game.json', 'w', encoding='utf-8') as f:
            json.dump(save_data, f, default=convert_datetime, ensure_ascii=False, indent=4)
            
        show_notification('Oyun kaydedildi!', color.green)
    except Exception as e:
        show_notification(f'KayÄ±t hatasÄ±: {str(e)}', color.red)

def load_game():
    """KaydedilmiÅŸ oyun durumunu yÃ¼kle"""
    try:
        # JSON dosyasÄ±nÄ± oku
        with open('save_game.json', 'r', encoding='utf-8') as f:
            save_data = json.load(f)
        
        # datetime string'lerini datetime nesnelerine dÃ¶nÃ¼ÅŸtÃ¼r
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
        
        # Verileri yÃ¼kle
        global player, market_state, quest_system, game_settings
        player = parse_datetime(save_data['player'])
        market_state = parse_datetime(save_data['market_state'])
        quest_system = parse_datetime(save_data['quest_system'])
        game_settings = save_data['game_settings']
        
        show_notification('Oyun yÃ¼klendi!', color.green)
    except FileNotFoundError:
        show_notification('KayÄ±tlÄ± oyun bulunamadÄ±.', color.yellow)
    except Exception as e:
        show_notification(f'YÃ¼kleme hatasÄ±: {str(e)}', color.red)

def show_notification(message, color=color.white):
    """Bildirim gÃ¶ster"""
    notification = Text(
        text=message,
        position=(0, 0.4),
        scale=2,
        color=color
    )
    destroy(notification, delay=3)

def auto_save():
    """Otomatik kayÄ±t"""
    current_time = datetime.now()
    if not hasattr(auto_save, 'last_save'):
        auto_save.last_save = current_time
    
    if (current_time - auto_save.last_save).seconds >= game_settings['save_interval']:
        save_game()
        auto_save.last_save = current_time

def quit_game():
    """Oyundan Ã§Ä±k"""
    # Oyunu kaydet
    save_game()
    
    # Pencereyi kapat
    application.quit()

def initialize_quest_system():
    """GÃ¶rev sistemini baÅŸlat"""
    # GÃ¼nlÃ¼k gÃ¶revleri yÃ¼kle
    daily_quests = ['daily_trade', 'daily_profit', 'daily_diversity']
    for quest_id in daily_quests:
        if quest_id in quest_definitions:
            quest_system['daily_quests'].append(quest_definitions[quest_id])
    
    # HaftalÄ±k gÃ¶revleri yÃ¼kle
    weekly_quests = ['weekly_growth', 'weekly_trades', 'weekly_risk']
    for quest_id in weekly_quests:
        if quest_id in quest_definitions:
            quest_system['weekly_quests'].append(quest_definitions[quest_id])
    
    # BaÅŸarÄ± gÃ¶revlerini yÃ¼kle
    achievement_quests = ['achievement_portfolio', 'achievement_diversity', 'achievement_debt']
    for quest_id in achievement_quests:
        if quest_id in quest_definitions:
            quest_system['achievement_quests'].append(quest_definitions[quest_id])
    
    # EÄŸitim gÃ¶revlerini yÃ¼kle
    tutorial_quests = ['tutorial_buy', 'tutorial_sell', 'tutorial_diversity']
    for quest_id in tutorial_quests:
        if quest_id in quest_definitions:
            quest_system['tutorial_quests'].append(quest_definitions[quest_id])
    
    # Aktif gÃ¶revleri belirle
    assign_daily_quests()
    assign_weekly_quests()
    
    # EÄŸitim gÃ¶revlerini aktif gÃ¶revlere ekle
    for quest in quest_system['tutorial_quests']:
        if quest['id'] not in player['completed_quests']:
            player['active_quests'].append(quest['id'])
            player['quest_progress'][quest['id']] = 0
    
    # BaÅŸarÄ± gÃ¶revlerini aktif gÃ¶revlere ekle
    for quest in quest_system['achievement_quests']:
        if quest['id'] not in player['completed_quests']:
            player['active_quests'].append(quest['id'])
            player['quest_progress'][quest['id']] = 0
    
    # GÃ¶rev UI'Ä±nÄ± oluÅŸtur
    create_quest_ui()

def assign_daily_quests():
    """GÃ¼nlÃ¼k gÃ¶revleri ata"""
    # GÃ¼nlÃ¼k gÃ¶revleri sÄ±fÄ±rla
    player['active_quests'] = [q for q in player['active_quests'] if q not in [d['id'] for d in quest_system['daily_quests']]]
    
    # Rastgele 2 gÃ¼nlÃ¼k gÃ¶rev seÃ§
    selected_quests = random.sample(quest_system['daily_quests'], min(2, len(quest_system['daily_quests'])))
    
    # SeÃ§ilen gÃ¶revleri aktif gÃ¶revlere ekle
    for quest in selected_quests:
        player['active_quests'].append(quest['id'])
        player['quest_progress'][quest['id']] = 0

def assign_weekly_quests():
    """HaftalÄ±k gÃ¶revleri ata"""
    # HaftalÄ±k gÃ¶revleri sÄ±fÄ±rla
    player['active_quests'] = [q for q in player['active_quests'] if q not in [w['id'] for w in quest_system['weekly_quests']]]
    
    # Rastgele 2 haftalÄ±k gÃ¶rev seÃ§
    selected_quests = random.sample(quest_system['weekly_quests'], min(2, len(quest_system['weekly_quests'])))
    
    # SeÃ§ilen gÃ¶revleri aktif gÃ¶revlere ekle
    for quest in selected_quests:
        player['active_quests'].append(quest['id'])
        player['quest_progress'][quest['id']] = 0

def check_quest_completion():
    """GÃ¶rev tamamlanma durumunu kontrol et"""
    completed_quests = []
    
    for quest_id in player['active_quests']:
        if quest_id in quest_definitions:
            quest = quest_definitions[quest_id]
            
            # GÃ¶rev tamamlandÄ± mÄ± kontrol et
            if quest['check_completion']():
                # GÃ¶revi tamamlandÄ± olarak iÅŸaretle
                completed_quests.append(quest_id)
                
                # Ã–dÃ¼lleri ver
                give_quest_rewards(quest)
                
                # Tamamlanan gÃ¶revi gÃ¶ster
                show_quest_completion(quest)
    
    # Tamamlanan gÃ¶revleri aktif gÃ¶revlerden Ã§Ä±kar
    for quest_id in completed_quests:
        player['active_quests'].remove(quest_id)
        player['completed_quests'].append(quest_id)
    
    # GÃ¶rev UI'Ä±nÄ± gÃ¼ncelle
    update_quest_ui()

def give_quest_rewards(quest):
    """GÃ¶rev Ã¶dÃ¼llerini ver"""
    reward = quest['reward']
    
    # Para Ã¶dÃ¼lÃ¼
    if 'money' in reward:
        player['money'] += reward['money']
    
    # Deneyim Ã¶dÃ¼lÃ¼
    if 'experience' in reward:
        player['experience']['current_xp'] += reward['experience']
        player['experience']['total_xp'] += reward['experience']
        
        # Seviye atlama kontrolÃ¼
        while player['experience']['current_xp'] >= player['experience']['next_level_xp']:
            player['experience']['current_xp'] -= player['experience']['next_level_xp']
            player['experience']['level'] += 1
            player['experience']['next_level_xp'] = calculate_next_level_xp(player['experience']['level'])
            show_level_up()
    
    # BaÅŸarÄ± Ã¶dÃ¼lÃ¼
    if 'achievement' in reward:
        if reward['achievement'] not in player['achievements']:
            player['achievements'].append(reward['achievement'])

def show_quest_completion(quest):
    """GÃ¶rev tamamlanma bildirimini gÃ¶ster"""
    # Ana bildirim metni
    completion_text = Text(
        text=f"GÃ¶rev TamamlandÄ±: {quest['title']}",
        position=(0, 0.6),
        scale=2,
        color=color.gold
    )
    
    # Ã–dÃ¼l detaylarÄ±
    reward_text = None
    if 'money' in quest['reward']:
        reward_text = Text(
            text=f"Ã–dÃ¼l: +${quest['reward']['money']:,.2f}",
            position=(0, 0.5),
            scale=1.5,
            color=color.green
        )
    
    # Metinleri belirli sÃ¼re sonra kaldÄ±r
    destroy(completion_text, delay=4)
    if reward_text:
        destroy(reward_text, delay=4)

def show_level_up():
    """Seviye atlama bildirimini gÃ¶ster"""
    level_text = Text(
        text=f"Seviye AtladÄ±nÄ±z! Yeni Seviye: {player['experience']['level']}",
        position=(0, 0.4),
        scale=2,
        color=color.yellow
    )
    destroy(level_text, delay=4)

def calculate_next_level_xp(current_level):
    """Sonraki seviye iÃ§in gereken XP'yi hesapla"""
    return int(1000 * (1.5 ** (current_level - 1)))

def create_quest_ui():
    """GÃ¶rev UI'Ä±nÄ± oluÅŸtur"""
    # GÃ¶rev paneli
    quest_ui['panel'] = Entity(
        parent=camera.ui,
        model='quad',
        scale=(0.8, 0.6),
        position=(0, 0),
        color=color.rgba(0, 0, 0, 0.7),
        visible=False
    )
    
    # GÃ¶rev baÅŸlÄ±ÄŸÄ±
    Text(
        parent=quest_ui['panel'],
        text='GÃ¶revler',
        position=(0, 0.25),
        scale=2,
        color=color.white
    )
    
    # Aktif gÃ¶revler baÅŸlÄ±ÄŸÄ±
    quest_ui['active_quests_text'] = Text(
        parent=quest_ui['panel'],
        text='Aktif GÃ¶revler:',
        position=(-0.35, 0.15),
        scale=1.5,
        color=color.white
    )
    
    # Tamamlanan gÃ¶revler baÅŸlÄ±ÄŸÄ±
    quest_ui['completed_quests_text'] = Text(
        parent=quest_ui['panel'],
        text='Tamamlanan GÃ¶revler:',
        position=(-0.35, -0.15),
        scale=1.5,
        color=color.white
    )
    
    # GÃ¶rev kapatma butonu
    Button(
        parent=quest_ui['panel'],
        text='Kapat',
        color=color.red,
        position=(0, -0.25),
        scale=(0.2, 0.05),
        on_click=Func(lambda: setattr(quest_ui['panel'], 'visible', False))
    )
    
    # GÃ¶rev butonu
    Button(
        parent=camera.ui,
        text='GÃ¶revler',
        color=color.azure,
        position=(0.7, 0.4),
        scale=(0.2, 0.05),
        on_click=Func(lambda: setattr(quest_ui['panel'], 'visible', True))
    )
    
    # GÃ¶rev UI'Ä±nÄ± gÃ¼ncelle
    update_quest_ui()

def update_quest_ui():
    """GÃ¶rev UI'Ä±nÄ± gÃ¼ncelle"""
    # Mevcut gÃ¶rev Ã¶ÄŸelerini temizle
    for item in quest_ui['quest_items']:
        destroy(item)
    quest_ui['quest_items'] = []
    
    # Aktif gÃ¶revleri gÃ¶ster
    y_position = 0.1
    for quest_id in player['active_quests']:
        if quest_id in quest_definitions:
            quest = quest_definitions[quest_id]
            
            # GÃ¶rev baÅŸlÄ±ÄŸÄ±
            quest_ui['quest_items'].append(
                Text(
                    parent=quest_ui['panel'],
                    text=quest['title'],
                    position=(-0.3, y_position),
                    scale=1.2,
                    color=color.white
                )
            )
            
            # GÃ¶rev aÃ§Ä±klamasÄ±
            quest_ui['quest_items'].append(
                Text(
                    parent=quest_ui['panel'],
                    text=quest['description'],
                    position=(-0.3, y_position - 0.05),
                    scale=0.8,
                    color=color.light_gray
                )
            )
            
            # GÃ¶rev Ã¶dÃ¼lÃ¼
            reward_text = f"Ã–dÃ¼l: ${quest['reward']['money']:,.2f}"
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
    
    # Tamamlanan gÃ¶revleri gÃ¶ster
    y_position = -0.2
    for quest_id in player['completed_quests'][-5:]:  # Son 5 tamamlanan gÃ¶revi gÃ¶ster
        if quest_id in quest_definitions:
            quest = quest_definitions[quest_id]
            
            # GÃ¶rev baÅŸlÄ±ÄŸÄ±
            quest_ui['quest_items'].append(
                Text(
                    parent=quest_ui['panel'],
                    text=quest['title'],
                    position=(-0.3, y_position),
                    scale=1.2,
                    color=color.light_gray
                )
            )
            
            # TamamlandÄ± iÅŸareti
            quest_ui['quest_items'].append(
                Text(
                    parent=quest_ui['panel'],
                    text="âœ“ TamamlandÄ±",
                    position=(0.2, y_position),
                    scale=0.8,
                    color=color.green
                )
            )
            
            y_position -= 0.1

def calculate_daily_profit():
    """GÃ¼nlÃ¼k kÃ¢rÄ± hesapla"""
    today = datetime.now().date()
    today_trades = [t for t in player['trading_history'] if t['timestamp'].date() == today]
    
    profit = 0
    for trade in today_trades:
        if trade['type'] == 'sell':
            # SatÄ±ÅŸ iÅŸleminden kÃ¢r hesapla
            buy_trades = [t for t in player['trading_history'] if t['stock'] == trade['stock'] and t['type'] == 'buy' and t['timestamp'].date() <= today]
            if buy_trades:
                # En eski alÄ±m fiyatÄ±nÄ± bul
                oldest_buy = min(buy_trades, key=lambda t: t['timestamp'])
                buy_price = oldest_buy['price']
                sell_price = trade['price']
                profit += (sell_price - buy_price) * trade['amount']
    
    return profit

def calculate_weekly_growth():
    """HaftalÄ±k bÃ¼yÃ¼meyi hesapla"""
    # BaÅŸlangÄ±Ã§ portfÃ¶y deÄŸeri (1 hafta Ã¶nce)
    week_ago = datetime.now() - timedelta(days=7)
    week_ago_trades = [t for t in player['trading_history'] if t['timestamp'] <= week_ago]
    
    # Åžu anki portfÃ¶y deÄŸeri
    current_value = calculate_portfolio_value()
    
    # HaftalÄ±k bÃ¼yÃ¼me oranÄ±
    if current_value > 0:
        return (current_value / 100000) - 1  # BaÅŸlangÄ±Ã§ deÄŸerine gÃ¶re bÃ¼yÃ¼me
    return 0

def update_market_state():
    """Piyasa durumunu gÃ¼ncelle"""
    current_time = datetime.now()
    if (current_time - market_state['last_update']).seconds >= 30:  # Her 30 saniyede bir gÃ¼ncelle
        # Piyasa trendini gÃ¼ncelle
        trend_chance = random.random()
        if trend_chance < 0.4:
            market_state['trend'] = 'stable'
        elif trend_chance < 0.7:
            market_state['trend'] = 'bull'
        else:
            market_state['trend'] = 'bear'
        
        # Volatiliteyi gÃ¼ncelle
        market_state['volatility'] = random.uniform(0.3, 0.8)
        
        # Piyasa olaylarÄ± oluÅŸtur
        if random.random() < 0.2:  # %20 ÅŸans
            event = generate_market_event()
            market_state['market_events'].append(event)
            show_market_event(event)
            apply_market_event(event)
        
        # Oyuncuya Ã¶zel olaylar oluÅŸtur
        if random.random() < 0.15:  # %15 ÅŸans
            player_event = generate_player_event()
            if player_event:
                show_player_event(player_event)
                apply_player_event(player_event)
        
        # GÃ¶rev tamamlanma durumunu kontrol et
        check_quest_completion()
        
        market_state['last_update'] = current_time

def update():
    """Ana oyun dÃ¶ngÃ¼sÃ¼"""
    # Piyasa gÃ¼ncellemesi
    update_market()
    
    # UI gÃ¼ncellemesi
    update_ui()
    
    # GÃ¶rev kontrolÃ¼
    check_quests()
    
    # Otomatik kayÄ±t
    if game_settings['auto_save']:
        auto_save()

def update_market():
    """Piyasa durumunu gÃ¼ncelle"""
    current_time = datetime.now()
    
    # Piyasa gÃ¼ncellemesi
    if (current_time - market_state['last_update']).seconds >= game_settings['market_update_interval']:
        # Trend gÃ¼ncelleme
        update_market_trend()
        
        # Fiyat gÃ¼ncelleme
        update_stock_prices()
        
        # Olay kontrolÃ¼
        check_market_events()
        
        market_state['last_update'] = current_time

def update_market_trend():
    """Piyasa trendini gÃ¼ncelle"""
    trend_chance = random.random()
    
    # Zorluk seviyesine gÃ¶re trend olasÄ±lÄ±klarÄ±
    if game_settings['difficulty'] == 'easy':
        if trend_chance < 0.5:  # %50 ÅŸans
            market_state['trend'] = 'bull'
        elif trend_chance < 0.8:  # %30 ÅŸans
            market_state['trend'] = 'stable'
        else:  # %20 ÅŸans
            market_state['trend'] = 'bear'
    elif game_settings['difficulty'] == 'normal':
        if trend_chance < 0.4:  # %40 ÅŸans
            market_state['trend'] = 'bull'
        elif trend_chance < 0.7:  # %30 ÅŸans
            market_state['trend'] = 'stable'
        else:  # %30 ÅŸans
            market_state['trend'] = 'bear'
    else:  # hard
        if trend_chance < 0.3:  # %30 ÅŸans
            market_state['trend'] = 'bull'
        elif trend_chance < 0.5:  # %20 ÅŸans
            market_state['trend'] = 'stable'
        else:  # %50 ÅŸans
            market_state['trend'] = 'bear'
    
    # Volatilite gÃ¼ncelleme
    market_state['volatility'] = random.uniform(
        0.2 if game_settings['difficulty'] == 'easy' else 0.3 if game_settings['difficulty'] == 'normal' else 0.4,
        0.5 if game_settings['difficulty'] == 'easy' else 0.7 if game_settings['difficulty'] == 'normal' else 0.9
    )

def update_stock_prices():
    """Hisse senedi fiyatlarÄ±nÄ± gÃ¼ncelle"""
    for symbol, data in player['portfolio'].items():
        base_price = data['price']
        
        # Trend etkisi
        trend_effect = {
            'bull': random.uniform(0.001, 0.01),
            'stable': random.uniform(-0.003, 0.003),
            'bear': random.uniform(-0.01, -0.001)
        }[market_state['trend']]
        
        # SektÃ¶r etkisi
        sector_effect = calculate_sector_effect(data['sector'])
        
        # Volatilite etkisi
        volatility_effect = random.uniform(-market_state['volatility'], market_state['volatility'])
        
        # Toplam deÄŸiÅŸim
        total_change = trend_effect + sector_effect + volatility_effect
        
        # Zorluk seviyesine gÃ¶re deÄŸiÅŸim sÄ±nÄ±rlamasÄ±
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
    """SektÃ¶r bazlÄ± fiyat etkisini hesapla"""
    sector_trends = {
        'tech': random.uniform(-0.005, 0.008),
        'auto': random.uniform(-0.004, 0.006),
        'retail': random.uniform(-0.003, 0.005),
        'media': random.uniform(-0.004, 0.007),
        'finance': random.uniform(-0.003, 0.004)
    }
    return sector_trends.get(sector, 0)

def check_market_events():
    """Piyasa olaylarÄ±nÄ± kontrol et"""
    if random.random() < game_settings['event_chance']:
        event = generate_market_event()
        if event:
            market_state['market_events'].append(event)
            apply_market_event(event)
            show_market_event(event)

def generate_market_event():
    """Piyasa olayÄ± oluÅŸtur"""
    event_types = {
        'global': [
            {
                'title': 'KÃ¼resel Ekonomik BÃ¼yÃ¼me',
                'description': 'KÃ¼resel ekonomik bÃ¼yÃ¼me beklentileri yÃ¼kseldi!',
                'effect': {'market_trend': 'bull', 'volatility': -0.1},
                'duration': 300,
                'probability': 0.2
            },
            {
                'title': 'Ekonomik Kriz',
                'description': 'KÃ¼resel ekonomik kriz endiÅŸeleri artÄ±yor!',
                'effect': {'market_trend': 'bear', 'volatility': 0.2},
                'duration': 300,
                'probability': 0.1
            }
        ],
        'sector': [
            {
                'title': 'Teknoloji AtÄ±lÄ±mÄ±',
                'description': 'Yeni teknolojik geliÅŸmeler sektÃ¶rÃ¼ hareketlendirdi!',
                'effect': {'sector': 'tech', 'change': 0.05},
                'duration': 180,
                'probability': 0.15
            },
            {
                'title': 'Otomotiv Krizi',
                'description': 'Tedarik zinciri sorunlarÄ± otomotiv sektÃ¶rÃ¼nÃ¼ vuruyor!',
                'effect': {'sector': 'auto', 'change': -0.05},
                'duration': 180,
                'probability': 0.15
            }
        ],
        'company': [
            {
                'title': 'ÃœrÃ¼n LansmanÄ±',
                'description': 'AAPL yeni Ã¼rÃ¼nlerini tanÄ±ttÄ±!',
                'effect': {'symbol': 'AAPL', 'change': 0.08},
                'duration': 120,
                'probability': 0.2
            },
            {
                'title': 'CEO Ä°stifasÄ±',
                'description': 'TSLA CEO\'su istifa etti!',
                'effect': {'symbol': 'TSLA', 'change': -0.08},
                'duration': 120,
                'probability': 0.1
            }
        ]
    }
    
    # Olay tÃ¼rÃ¼ seÃ§
    event_type = random.choice(list(event_types.keys()))
    events = event_types[event_type]
    
    # OlasÄ±lÄ±k kontrolÃ¼
    for event in events:
        if random.random() < event['probability']:
            return event
    
    return None

def apply_market_event(event):
    """Piyasa olayÄ±nÄ± uygula"""
    effect = event['effect']
    
    # Piyasa trendi etkisi
    if 'market_trend' in effect:
        market_state['trend'] = effect['market_trend']
    
    # Volatilite etkisi
    if 'volatility' in effect:
        market_state['volatility'] = max(0.1, min(1.0, market_state['volatility'] + effect['volatility']))
    
    # SektÃ¶r etkisi
    if 'sector' in effect:
        for symbol, data in player['portfolio'].items():
            if data['sector'] == effect['sector']:
                data['price'] *= (1 + effect['change'])
    
    # Åžirket etkisi
    if 'symbol' in effect:
        if effect['symbol'] in player['portfolio']:
            player['portfolio'][effect['symbol']]['price'] *= (1 + effect['change'])

def show_market_event(event):
    """Piyasa olayÄ±nÄ± gÃ¶ster"""
    # Bildirim paneli
    notification = Entity(
        parent=camera.ui,
        model='quad',
        scale=(0.6, 0.2),
        position=(0, 0.3),
        color=color.rgba(0, 0, 0, 0.9)
    )
    
    # BaÅŸlÄ±k
    title_text = Text(
        parent=notification,
        text=event['title'],
        position=(0, 0.05),
        scale=1.5,
        color=color.yellow
    )
    
    # AÃ§Ä±klama
    desc_text = Text(
        parent=notification,
        text=event['description'],
        position=(0, -0.02),
        scale=1.2,
        color=color.white
    )
    
    # Efekt aÃ§Ä±klamasÄ±
    effect = event['effect']
    effect_text = ""
    
    if 'market_trend' in effect:
        effect_text = "Piyasa trendi deÄŸiÅŸti!"
    elif 'sector' in effect:
        effect_text = f"{effect['sector'].upper()} sektÃ¶rÃ¼ etkilendi!"
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
    """PortfÃ¶y deÄŸerini hesapla"""
    total_value = player['money']
    for symbol, data in player['portfolio'].items():
        total_value += data['shares'] * data['price']
    return total_value

def calculate_risk_score():
    """Risk skorunu hesapla"""
    # PortfÃ¶y Ã§eÅŸitliliÄŸi (0-1 arasÄ±)
    portfolio_diversity = calculate_portfolio_diversity()
    
    # BorÃ§/gelir oranÄ± (0-1 arasÄ±)
    debt_to_income = calculate_debt_to_income_ratio()
    
    # Toplam risk skoru (0-1 arasÄ±)
    risk_score = (1 - portfolio_diversity) * 0.6 + debt_to_income * 0.4
    return min(max(risk_score, 0), 1)

def calculate_portfolio_diversity():
    """PortfÃ¶y Ã§eÅŸitliliÄŸini hesapla"""
    total_value = calculate_portfolio_value()
    if total_value == 0:
        return 0
    
    # Her sektÃ¶rdeki yatÄ±rÄ±m oranÄ±nÄ± hesapla
    sector_weights = {}
    for symbol, data in player['portfolio'].items():
        sector = data['sector']
        value = data['shares'] * data['price']
        sector_weights[sector] = sector_weights.get(sector, 0) + value / total_value
    
    # Herfindahl-Hirschman Index'ini hesapla (ters Ã§evrilmiÅŸ)
    hhi = sum(weight * weight for weight in sector_weights.values())
    diversity = 1 - hhi
    return min(max(diversity, 0), 1)

def calculate_debt_to_income_ratio():
    """BorÃ§/gelir oranÄ±nÄ± hesapla"""
    total_income = sum(t['amount'] for t in player.get('trading_history', []) 
                      if t['type'] == 'profit' and (datetime.now() - t['timestamp']).days <= 30)
    total_debt = sum(t['amount'] for t in player.get('trading_history', [])
                    if t['type'] == 'loss' and (datetime.now() - t['timestamp']).days <= 30)
    
    if total_income == 0:
        return 1 if total_debt > 0 else 0
    
    ratio = total_debt / total_income
    return min(max(ratio, 0), 1)

def update_ui():
    """UI'Ä± gÃ¼ncelle"""
    # Para ve portfÃ¶y deÄŸerini gÃ¼ncelle
    ui['text_elements']['money'].text = f"Para: ${player['money']:,.2f}"
    ui['text_elements']['portfolio_value'].text = f"PortfÃ¶y: ${calculate_portfolio_value():,.2f}"
    ui['text_elements']['risk_score'].text = f"Risk: {calculate_risk_score():.2f}"
    
    # Hisse senedi fiyatlarÄ±nÄ± gÃ¼ncelle
    for symbol, data in player['portfolio'].items():
        if symbol in ui['text_elements']:
            ui['text_elements'][symbol].text = f"{symbol}: ${data['price']:,.2f}"
    
    # Hisse senedi butonlarÄ±nÄ± gÃ¼ncelle
    update_stock_buttons()
    
    # GÃ¶revleri gÃ¼ncelle
    update_quest_ui()
    
    # Bildirimleri gÃ¼ncelle
    update_notifications()

def update_stock_buttons():
    """Hisse senedi butonlarÄ±nÄ± gÃ¼ncelle"""
    for symbol, data in player['portfolio'].items():
        # AlÄ±m butonu
        if symbol + '_buy' in ui['buttons']:
            ui['buttons'][symbol + '_buy'].enabled = player['money'] >= data['price']
        
        # SatÄ±m butonu
        if symbol + '_sell' in ui['buttons']:
            ui['buttons'][symbol + '_sell'].enabled = data['shares'] > 0

def update_notifications():
    """Bildirimleri gÃ¼ncelle"""
    current_time = datetime.now()
    
    # SÃ¼resi dolmuÅŸ bildirimleri kaldÄ±r
    ui['notifications'] = [n for n in ui['notifications'] 
                         if (current_time - n['timestamp']).seconds < 5]
    
    # Bildirimleri gÃ¶ster
    for i, notification in enumerate(ui['notifications']):
        if 'text' in notification:
            notification['text'].y = -0.3 - i * 0.1

def buy_stock(symbol):
    """Hisse senedi satÄ±n al"""
    stock = player['portfolio'][symbol]
    price = stock['price']
    
    # Yeterli para var mÄ± kontrol et
    if player['money'] < price:
        show_notification('Yeterli paranÄ±z yok!', color.red)
        return
    
    # Ä°ÅŸlemi gerÃ§ekleÅŸtir
    player['money'] -= price
    stock['shares'] += 1
    
    # Ä°ÅŸlem kaydÄ±nÄ± tut
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

# Django ayarlarÄ±nÄ± yÃ¼kle
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
# django.setup() satÄ±rÄ± kaldÄ±rÄ±ldÄ± - circular import sorununa yol aÃ§Ä±yor

# Oyun iÃ§indeki ÅŸirket modelleri yerine sÄ±nÄ±flar kullan
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

# Oyun ayarlarÄ±
game_settings = {
    'difficulty': 'normal',  # easy, normal, hard
    'market_update_interval': 5,  # saniye
    'event_chance': 0.2,  # 0-1 arasÄ±
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
    'volatility': 0.5,  # 0-1 arasÄ±
    'last_update': datetime.now(),
    'market_events': []
}

# UI bileÅŸenleri
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
        'debt_to_income': 0.0,  # BorÃ§/gelir oranÄ±
        'portfolio_diversity': 0.0,  # PortfÃ¶y Ã§eÅŸitliliÄŸi
        'total_debt': 0,  # Toplam borÃ§
        'total_income': 0,  # Toplam gelir
        'monthly_income': 0,  # AylÄ±k gelir
        'monthly_expenses': 0  # AylÄ±k giderler
    },
    'skills': {
        'analysis': 1,  # 1-10 arasÄ±
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

# GÃ¶rev sistemi
quest_system = {
    'daily_quests': [],
    'weekly_quests': [],
    'achievement_quests': [],
    'tutorial_quests': []
}

# GÃ¶rev tanÄ±mlamalarÄ±
quest_definitions = {
    # GÃ¼nlÃ¼k gÃ¶revler
    'daily_trade': {
        'id': 'daily_trade',
        'title': 'GÃ¼nlÃ¼k Ä°ÅŸlem',
        'description': 'BugÃ¼n en az 1 hisse senedi alÄ±m veya satÄ±m iÅŸlemi yapÄ±n.',
        'reward': {'money': 500, 'experience': 100},
        'type': 'daily',
        'check_completion': lambda: len([t for t in player['trading_history'] if (datetime.now() - t['timestamp']).days < 1]) > 0
    },
    'daily_profit': {
        'id': 'daily_profit',
        'title': 'GÃ¼nlÃ¼k KÃ¢r',
        'description': 'BugÃ¼n portfÃ¶yÃ¼nÃ¼zden 1000$ kÃ¢r elde edin.',
        'reward': {'money': 1000, 'experience': 200},
        'type': 'daily',
        'check_completion': lambda: calculate_daily_profit() >= 1000
    },
    'daily_diversity': {
        'id': 'daily_diversity',
        'title': 'Ã‡eÅŸitlilik UstasÄ±',
        'description': 'PortfÃ¶y Ã§eÅŸitliliÄŸinizi 0.7\'nin Ã¼zerine Ã§Ä±karÄ±n.',
        'reward': {'money': 800, 'experience': 150},
        'type': 'daily',
        'check_completion': lambda: player['stats']['portfolio_diversity'] > 0.7
    },
    
    # HaftalÄ±k gÃ¶revler
    'weekly_growth': {
        'id': 'weekly_growth',
        'title': 'HaftalÄ±k BÃ¼yÃ¼me',
        'description': 'PortfÃ¶yÃ¼nÃ¼zÃ¼ bu hafta %10 bÃ¼yÃ¼tÃ¼n.',
        'reward': {'money': 5000, 'experience': 500},
        'type': 'weekly',
        'check_completion': lambda: calculate_weekly_growth() >= 0.1
    },
    'weekly_trades': {
        'id': 'weekly_trades',
        'title': 'Aktif Trader',
        'description': 'Bu hafta en az 10 iÅŸlem yapÄ±n.',
        'reward': {'money': 3000, 'experience': 400},
        'type': 'weekly',
        'check_completion': lambda: len([t for t in player['trading_history'] if (datetime.now() - t['timestamp']).days < 7]) >= 10
    },
    'weekly_risk': {
        'id': 'weekly_risk',
        'title': 'Risk YÃ¶neticisi',
        'description': 'Risk skorunuzu 0.5\'in altÄ±na dÃ¼ÅŸÃ¼rÃ¼n.',
        'reward': {'money': 4000, 'experience': 450},
        'type': 'weekly',
        'check_completion': lambda: calculate_risk_score() < 0.5
    },
    
    # BaÅŸarÄ± gÃ¶revleri
    'achievement_portfolio': {
        'id': 'achievement_portfolio',
        'title': 'PortfÃ¶y UstasÄ±',
        'description': 'PortfÃ¶yÃ¼nÃ¼zÃ¼ 200.000$ deÄŸerine ulaÅŸtÄ±rÄ±n.',
        'reward': {'money': 10000, 'experience': 1000, 'achievement': 'portfolio_master'},
        'type': 'achievement',
        'check_completion': lambda: calculate_portfolio_value() >= 200000
    },
    'achievement_diversity': {
        'id': 'achievement_diversity',
        'title': 'Ã‡eÅŸitlilik KralÄ±',
        'description': 'PortfÃ¶y Ã§eÅŸitliliÄŸinizi 0.9\'un Ã¼zerine Ã§Ä±karÄ±n.',
        'reward': {'money': 8000, 'experience': 800, 'achievement': 'diversity_king'},
        'type': 'achievement',
        'check_completion': lambda: player['stats']['portfolio_diversity'] > 0.9
    },
    'achievement_debt': {
        'id': 'achievement_debt',
        'title': 'BorÃ§suz YaÅŸam',
        'description': 'BorÃ§/gelir oranÄ±nÄ±zÄ± 0.1\'in altÄ±na dÃ¼ÅŸÃ¼rÃ¼n.',
        'reward': {'money': 6000, 'experience': 600, 'achievement': 'debt_free'},
        'type': 'achievement',
        'check_completion': lambda: player['stats']['debt_to_income'] < 0.1
    },
    
    # EÄŸitim gÃ¶revleri
    'tutorial_buy': {
        'id': 'tutorial_buy',
        'title': 'Ä°lk AlÄ±m',
        'description': 'Ä°lk hisse senedi alÄ±m iÅŸleminizi yapÄ±n.',
        'reward': {'money': 1000, 'experience': 200},
        'type': 'tutorial',
        'check_completion': lambda: len([t for t in player['trading_history'] if t['type'] == 'buy']) > 0
    },
    'tutorial_sell': {
        'id': 'tutorial_sell',
        'title': 'Ä°lk SatÄ±m',
        'description': 'Ä°lk hisse senedi satÄ±m iÅŸleminizi yapÄ±n.',
        'reward': {'money': 1000, 'experience': 200},
        'type': 'tutorial',
        'check_completion': lambda: len([t for t in player['trading_history'] if t['type'] == 'sell']) > 0
    },
    'tutorial_diversity': {
        'id': 'tutorial_diversity',
        'title': 'Ã‡eÅŸitlendirme',
        'description': 'En az 3 farklÄ± hisse senedine yatÄ±rÄ±m yapÄ±n.',
        'reward': {'money': 2000, 'experience': 300},
        'type': 'tutorial',
        'check_completion': lambda: len([s for s in player['portfolio'].values() if s['shares'] > 0]) >= 3
    }
}

# GÃ¶rev UI elementleri
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
        
        # Dil yÃ¶neticisi
        self.locale_manager = LocaleManager()
        
        # Platform kontrolÃ¼
        self.platform = self.oyun.platform
        self.is_mobile = self.platform in ['android', 'ios']
        
        # AR yÃ¶neticisini baÅŸlat (mobil platformlarda)
        if self.is_mobile:
            self.ar_manager = ARManager(use_aruco=True, show_camera=True)
            self.ar_manager.start()
            
        # DÃ¼nya oluÅŸturma
        self.dunya = Entity(
            model='plane',
            texture='white_cube',
            scale=(100, 1, 100),
            color=color.gray
        )
        
        # Binalar ve iÅŸ yerleri
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
        
        # TuÅŸ durumlarÄ±
        self.held_keys = {'w': False, 'a': False, 's': False, 'd': False, 'left mouse': False, 'right mouse': False}
        
        # Ä°nitialize
        self.bina_olustur()
        self.is_yeri_olustur()
        self.olay_olustur()
        self.ui_olustur()
        
        # Otomatik kayÄ±t
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
        
        # Bakiye gÃ¶stergesi
        self.ui_elements['bakiye'] = Text(
            parent=self.ui_elements['ana_panel'],
            text=f"{self.locale_manager.get_text('game.stats.balance')}: ${self.oyun.oyuncu_bakiyesi:,.2f}",
            position=(-0.4, 0.4),
            scale=2,
            color=color.green
        )
        
        # Puan gÃ¶stergesi
        self.ui_elements['puan'] = Text(
            parent=self.ui_elements['ana_panel'],
            text=f"{self.locale_manager.get_text('game.stats.score')}: {self.oyun.oyuncu_puani}",
            position=(0.4, 0.4),
            scale=2,
            color=color.yellow
        )
        
        # Seviye gÃ¶stergesi
        self.ui_elements['seviye'] = Text(
            parent=self.ui_elements['ana_panel'],
            text=f"{self.locale_manager.get_text('game.stats.level')}: {self.oyun.oyuncu_seviyesi}",
            position=(0, 0.4),
            scale=2,
            color=color.azure
        )
        
        # Ä°ÅŸlem butonlarÄ±
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
        
        # MenÃ¼ butonu
        self.ui_elements['menu_buton'] = Button(
            parent=camera.ui,
            text=self.locale_manager.get_text('game.menu.settings'),
            color=color.azure,
            position=(0.8, 0.45),
            scale=(0.2, 0.05),
            on_click=self.toggle_menu
        )
        
        # Dil seÃ§imi butonu
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
        """Dil seÃ§imini deÄŸiÅŸtir"""
        available_locales = self.locale_manager.get_available_locales()
        current_index = available_locales.index(self.locale_manager.get_current_locale())
        next_index = (current_index + 1) % len(available_locales)
        self.locale_manager.set_locale(available_locales[next_index])
        
        # UI'Ä± gÃ¼ncelle
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
        """MenÃ¼yÃ¼ aÃ§/kapat"""
        self.is_paused = not self.is_paused
        
        if self.is_paused:
            # MenÃ¼ panelini gÃ¶ster
            self.ui_elements['menu_panel'] = Entity(
                parent=camera.ui,
                model='quad',
                scale=(0.4, 0.6),
                position=(0, 0),
                color=color.rgba(0, 0, 0, 0.9)
            )
            
            # MenÃ¼ butonlarÄ±
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
                text='YÃ¼kle',
                color=color.azure,
                position=(0, 0),
                scale=(0.3, 0.05),
                on_click=self.oyun.load_game
            )
            
            Button(
                parent=self.ui_elements['menu_panel'],
                text='Ã‡Ä±kÄ±ÅŸ',
                color=color.red,
                position=(0, -0.2),
                scale=(0.3, 0.05),
                on_click=application.quit
            )
        else:
            # MenÃ¼ panelini kaldÄ±r
            if 'menu_panel' in self.ui_elements:
                destroy(self.ui_elements['menu_panel'])
                del self.ui_elements['menu_panel']
        
    def update(self):
        # Performans kontrolÃ¼
        current_time = time.time()
        if current_time - self.last_update < self.update_interval:
            return
        self.last_update = current_time
        
        if self.is_paused:
            return
            
        # Oyun gÃ¼ncellemeleri
        if self.held_keys['left mouse']:
            self.alis_yap()
            
        if self.held_keys['right mouse']:
            self.satis_yap()
            
        # AR gÃ¼ncellemeleri
        if self.is_mobile:
            self.ar_manager.ar_nesne_guncelle()
            
        # Olay gÃ¼ncellemeleri
        self.olay_guncelle()
        
    def olay_guncelle(self):
        simdiki_zaman = time.time()
        for olay in self.olaylar:
            if simdiki_zaman - olay['baslangic'] > olay['sure']:
                # Olay sÃ¼resi doldu, yeni olay oluÅŸtur
                olay['tip'] = random.choice([
                    'Borsa YÃ¼kseliÅŸi', 'Borsa DÃ¼ÅŸÃ¼ÅŸÃ¼',
                    'Enflasyon ArtÄ±ÅŸÄ±', 'Enflasyon DÃ¼ÅŸÃ¼ÅŸÃ¼',
                    'Faiz ArtÄ±ÅŸÄ±', 'Faiz DÃ¼ÅŸÃ¼ÅŸÃ¼',
                    'DÃ¶viz DalgalanmasÄ±', 'AltÄ±n FiyatÄ± DeÄŸiÅŸimi'
                ])
                olay['etki'] = random.uniform(-0.2, 0.2)
                olay['baslangic'] = simdiki_zaman
                
                # Olay bildirimi
                self.ui_elements['bildirim'].text = f"Yeni Olay: {olay['tip']}"
                self.ui_elements['bildirim'].color = color.yellow

def run_game(online_mode: bool = False):
    """Oyunu baÅŸlat"""
    app = Ursina()
    dunya = FinansalDunya(online_mode=online_mode)
    app.run()

def create_ui():
    """Ana UI'Ä± oluÅŸtur"""
    # Ana panel
    ui['main_panel'] = Entity(
        parent=camera.ui,
        model='quad',
        scale=(1.8, 1),
        position=(0, 0),
        color=color.rgba(0, 0, 0, 0.8)
    )
    
    # Ãœst bilgi paneli
    create_top_info_panel()
    
    # PortfÃ¶y paneli
    create_portfolio_panel()
    
    # Market paneli
    create_market_panel()
    
    # Ä°statistik paneli
    create_stats_panel()
    
    # MenÃ¼ butonu
    Button(
        parent=camera.ui,
        text='MenÃ¼',
        color=color.azure,
        position=(0.8, 0.45),
        scale=(0.2, 0.05),
        on_click=Func(toggle_menu)
    )

def create_top_info_panel():
    """Ãœst bilgi panelini oluÅŸtur"""
    # Para
    ui['text_elements']['money'] = Text(
        parent=camera.ui,
        text=f"${player['money']:,.2f}",
        position=(-0.8, 0.45),
        scale=2,
        color=color.green
    )
    
    # PortfÃ¶y deÄŸeri
    ui['text_elements']['portfolio_value'] = Text(
        parent=camera.ui,
        text=f"PortfÃ¶y: ${calculate_portfolio_value():,.2f}",
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
    """PortfÃ¶y panelini oluÅŸtur"""
    ui['portfolio_panel'] = Entity(
        parent=ui['main_panel'],
        model='quad',
        scale=(0.5, 0.8),
        position=(-0.6, -0.05),
        color=color.rgba(0, 0, 0, 0.5)
    )
    
    # BaÅŸlÄ±k
    Text(
        parent=ui['portfolio_panel'],
        text='PortfÃ¶y',
        position=(0, 0.35),
        scale=2,
        color=color.white
    )
    
    # Hisse senetleri listesi
    y_pos = 0.25
    for symbol, data in player['portfolio'].items():
        if data['shares'] > 0:
            # Hisse adÄ± ve miktar
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
    """Market panelini oluÅŸtur"""
    ui['market_panel'] = Entity(
        parent=ui['main_panel'],
        model='quad',
        scale=(0.5, 0.8),
        position=(0, -0.05),
        color=color.rgba(0, 0, 0, 0.5)
    )
    
    # BaÅŸlÄ±k
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
        # Hisse adÄ± ve fiyat
        Text(
            parent=ui['market_panel'],
            text=f"{symbol}: ${data['price']:,.2f}",
            position=(-0.2, y_pos),
            scale=1.2,
            color=color.white
        )
        
        # AlÄ±m butonu
        Button(
            parent=ui['market_panel'],
            text='Al',
            color=color.green,
            position=(0.1, y_pos),
            scale=(0.1, 0.04),
            on_click=Func(lambda s=symbol: buy_stock(s))
        )
        
        # SatÄ±m butonu
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
    """Ä°statistik panelini oluÅŸtur"""
    ui['stats_panel'] = Entity(
        parent=ui['main_panel'],
        model='quad',
        scale=(0.5, 0.8),
        position=(0.6, -0.05),
        color=color.rgba(0, 0, 0, 0.5)
    )
    
    # BaÅŸlÄ±k
    Text(
        parent=ui['stats_panel'],
        text='Ä°statistikler',
        position=(0, 0.35),
        scale=2,
        color=color.white
    )
    
    # Ä°statistikler
    stats = player['stats']
    y_pos = 0.25
    
    # Toplam iÅŸlem
    Text(
        parent=ui['stats_panel'],
        text=f"Toplam Ä°ÅŸlem: {stats['total_trades']}",
        position=(0, y_pos),
        scale=1.2,
        color=color.white
    )
    y_pos -= 0.08
    
    # BaÅŸarÄ±lÄ± iÅŸlemler
    Text(
        parent=ui['stats_panel'],
        text=f"BaÅŸarÄ±lÄ±: {stats['successful_trades']}",
        position=(0, y_pos),
        scale=1.2,
        color=color.green
    )
    y_pos -= 0.08
    
    # BaÅŸarÄ±sÄ±z iÅŸlemler
    Text(
        parent=ui['stats_panel'],
        text=f"BaÅŸarÄ±sÄ±z: {stats['failed_trades']}",
        position=(0, y_pos),
        scale=1.2,
        color=color.red
    )
    y_pos -= 0.08
    
    # Toplam kÃ¢r
    Text(
        parent=ui['stats_panel'],
        text=f"Toplam KÃ¢r: ${stats['total_profit']:,.2f}",
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
    """MenÃ¼yÃ¼ aÃ§/kapat"""
    if not ui['menu_panel']:
        create_menu()
    else:
        destroy(ui['menu_panel'])
        ui['menu_panel'] = None

def create_menu():
    """MenÃ¼ panelini oluÅŸtur"""
    ui['menu_panel'] = Entity(
        parent=camera.ui,
        model='quad',
        scale=(0.4, 0.6),
        position=(0, 0),
        color=color.rgba(0, 0, 0, 0.9)
    )
    
    # BaÅŸlÄ±k
    Text(
        parent=ui['menu_panel'],
        text='MenÃ¼',
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
    
    # YÃ¼kle butonu
    Button(
        parent=ui['menu_panel'],
        text='YÃ¼kle',
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
    
    # Ã‡Ä±kÄ±ÅŸ butonu
    Button(
        parent=ui['menu_panel'],
        text='Ã‡Ä±kÄ±ÅŸ',
        color=color.red,
        position=(0, -0.2),
        scale=(0.3, 0.05),
        on_click=Func(quit_game)
    )

def show_settings():
    """Ayarlar menÃ¼sÃ¼nÃ¼ gÃ¶ster"""
    # Mevcut menÃ¼yÃ¼ kapat
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
    
    # BaÅŸlÄ±k
    Text(
        parent=ui['settings_panel'],
        text='Ayarlar',
        position=(0, 0.25),
        scale=2,
        color=color.white
    )
    
    # Ses ayarÄ±
    Button(
        parent=ui['settings_panel'],
        text=f"Ses: {'AÃ§Ä±k' if game_settings['sound_enabled'] else 'KapalÄ±'}",
        color=color.azure,
        position=(0, 0.1),
        scale=(0.3, 0.05),
        on_click=Func(toggle_sound)
    )
    
    # MÃ¼zik ayarÄ±
    Button(
        parent=ui['settings_panel'],
        text=f"MÃ¼zik: {'AÃ§Ä±k' if game_settings['music_enabled'] else 'KapalÄ±'}",
        color=color.azure,
        position=(0, 0),
        scale=(0.3, 0.05),
        on_click=Func(toggle_music)
    )
    
    # Tam ekran ayarÄ±
    Button(
        parent=ui['settings_panel'],
        text=f"Tam Ekran: {'AÃ§Ä±k' if game_settings['fullscreen'] else 'KapalÄ±'}",
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
    """Ses ayarÄ±nÄ± deÄŸiÅŸtir"""
    game_settings['sound_enabled'] = not game_settings['sound_enabled']
    show_settings()  # Ayarlar menÃ¼sÃ¼nÃ¼ yenile

def toggle_music():
    """MÃ¼zik ayarÄ±nÄ± deÄŸiÅŸtir"""
    game_settings['music_enabled'] = not game_settings['music_enabled']
    show_settings()  # Ayarlar menÃ¼sÃ¼nÃ¼ yenile

def toggle_fullscreen():
    """Tam ekran ayarÄ±nÄ± deÄŸiÅŸtir"""
    game_settings['fullscreen'] = not game_settings['fullscreen']
    window.fullscreen = game_settings['fullscreen']
    show_settings()  # Ayarlar menÃ¼sÃ¼nÃ¼ yenile

def start_tutorial():
    """EÄŸitim modunu baÅŸlat"""
    tutorial_steps = [
        {
            'title': 'HoÅŸ Geldiniz!',
            'description': 'FinAsis finansal eÄŸitim simÃ¼lasyonuna hoÅŸ geldiniz. Size temel Ã¶zellikleri tanÄ±tacaÄŸÄ±m.',
            'position': (0, 0)
        },
        {
            'title': 'PortfÃ¶y Paneli',
            'description': 'Bu panel sahip olduÄŸunuz hisse senetlerini gÃ¶sterir.',
            'position': (-0.65, 0)
        },
        {
            'title': 'Market Paneli',
            'description': 'Bu panel piyasadaki hisse senetlerini ve fiyatlarÄ±nÄ± gÃ¶sterir.',
            'position': (0, 0)
        },
        {
            'title': 'Ä°statistik Paneli',
            'description': 'Bu panel trading performansÄ±nÄ±zÄ± gÃ¶sterir.',
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
        
        # BaÅŸlÄ±k
        if hasattr(tutorial_panel, 'title'):
            destroy(tutorial_panel.title)
        tutorial_panel.title = Text(
            parent=tutorial_panel,
            text=step['title'],
            position=(0, 0.05),
            scale=1.5,
            color=color.yellow
        )
        
        # AÃ§Ä±klama
        if hasattr(tutorial_panel, 'description'):
            destroy(tutorial_panel.description)
        tutorial_panel.description = Text(
            parent=tutorial_panel,
            text=step['description'],
            position=(0, -0.02),
            scale=1,
            color=color.white
        )
        
        # Ä°leri butonu
        if hasattr(tutorial_panel, 'next_button'):
            destroy(tutorial_panel.next_button)
        tutorial_panel.next_button = Button(
            parent=tutorial_panel,
            text='Ä°leri' if current_step < len(tutorial_steps) - 1 else 'Bitir',
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
            # Tutorial'Ä± bitir
            destroy(tutorial_panel)
            player['tutorial_progress']['basic_trading'] = True
            save_game()
    
    # Ä°lk adÄ±mÄ± gÃ¶ster
    show_step()

def save_game():
    """Oyun durumunu kaydet"""
    try:
        # Kaydedilecek verileri hazÄ±rla
        save_data = {
            'player': player,
            'market_state': market_state,
            'quest_system': quest_system,
            'game_settings': game_settings,
            'save_time': datetime.now().isoformat()
        }
        
        # datetime nesnelerini ISO formatÄ±na dÃ¶nÃ¼ÅŸtÃ¼r
        def convert_datetime(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            return obj
        
        # Verileri JSON formatÄ±nda kaydet
        with open('save_game.json', 'w', encoding='utf-8') as f:
            json.dump(save_data, f, default=convert_datetime, ensure_ascii=False, indent=4)
            
        show_notification('Oyun kaydedildi!', color.green)
    except Exception as e:
        show_notification(f'KayÄ±t hatasÄ±: {str(e)}', color.red)

def load_game():
    """KaydedilmiÅŸ oyun durumunu yÃ¼kle"""
    try:
        # JSON dosyasÄ±nÄ± oku
        with open('save_game.json', 'r', encoding='utf-8') as f:
            save_data = json.load(f)
        
        # datetime string'lerini datetime nesnelerine dÃ¶nÃ¼ÅŸtÃ¼r
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
        
        # Verileri yÃ¼kle
        global player, market_state, quest_system, game_settings
        player = parse_datetime(save_data['player'])
        market_state = parse_datetime(save_data['market_state'])
        quest_system = parse_datetime(save_data['quest_system'])
        game_settings = save_data['game_settings']
        
        show_notification('Oyun yÃ¼klendi!', color.green)
    except FileNotFoundError:
        show_notification('KayÄ±tlÄ± oyun bulunamadÄ±.', color.yellow)
    except Exception as e:
        show_notification(f'YÃ¼kleme hatasÄ±: {str(e)}', color.red)

def show_notification(message, color=color.white):
    """Bildirim gÃ¶ster"""
    notification = Text(
        text=message,
        position=(0, 0.4),
        scale=2,
        color=color
    )
    destroy(notification, delay=3)

def auto_save():
    """Otomatik kayÄ±t"""
    current_time = datetime.now()
    if not hasattr(auto_save, 'last_save'):
        auto_save.last_save = current_time
    
    if (current_time - auto_save.last_save).seconds >= game_settings['save_interval']:
        save_game()
        auto_save.last_save = current_time

def quit_game():
    """Oyundan Ã§Ä±k"""
    # Oyunu kaydet
    save_game()
    
    # Pencereyi kapat
    application.quit()

def initialize_quest_system():
    """GÃ¶rev sistemini baÅŸlat"""
    # GÃ¼nlÃ¼k gÃ¶revleri yÃ¼kle
    daily_quests = ['daily_trade', 'daily_profit', 'daily_diversity']
    for quest_id in daily_quests:
        if quest_id in quest_definitions:
            quest_system['daily_quests'].append(quest_definitions[quest_id])
    
    # HaftalÄ±k gÃ¶revleri yÃ¼kle
    weekly_quests = ['weekly_growth', 'weekly_trades', 'weekly_risk']
    for quest_id in weekly_quests:
        if quest_id in quest_definitions:
            quest_system['weekly_quests'].append(quest_definitions[quest_id])
    
    # BaÅŸarÄ± gÃ¶revlerini yÃ¼kle
    achievement_quests = ['achievement_portfolio', 'achievement_diversity', 'achievement_debt']
    for quest_id in achievement_quests:
        if quest_id in quest_definitions:
            quest_system['achievement_quests'].append(quest_definitions[quest_id])
    
    # EÄŸitim gÃ¶revlerini yÃ¼kle
    tutorial_quests = ['tutorial_buy', 'tutorial_sell', 'tutorial_diversity']
    for quest_id in tutorial_quests:
        if quest_id in quest_definitions:
            quest_system['tutorial_quests'].append(quest_definitions[quest_id])
    
    # Aktif gÃ¶revleri belirle
    assign_daily_quests()
    assign_weekly_quests()
    
    # EÄŸitim gÃ¶revlerini aktif gÃ¶revlere ekle
    for quest in quest_system['tutorial_quests']:
        if quest['id'] not in player['completed_quests']:
            player['active_quests'].append(quest['id'])
            player['quest_progress'][quest['id']] = 0
    
    # BaÅŸarÄ± gÃ¶revlerini aktif gÃ¶revlere ekle
    for quest in quest_system['achievement_quests']:
        if quest['id'] not in player['completed_quests']:
            player['active_quests'].append(quest['id'])
            player['quest_progress'][quest['id']] = 0
    
    # GÃ¶rev UI'Ä±nÄ± oluÅŸtur
    create_quest_ui()

def assign_daily_quests():
    """GÃ¼nlÃ¼k gÃ¶revleri ata"""
    # GÃ¼nlÃ¼k gÃ¶revleri sÄ±fÄ±rla
    player['active_quests'] = [q for q in player['active_quests'] if q not in [d['id'] for d in quest_system['daily_quests']]]
    
    # Rastgele 2 gÃ¼nlÃ¼k gÃ¶rev seÃ§
    selected_quests = random.sample(quest_system['daily_quests'], min(2, len(quest_system['daily_quests'])))
    
    # SeÃ§ilen gÃ¶revleri aktif gÃ¶revlere ekle
    for quest in selected_quests:
        player['active_quests'].append(quest['id'])
        player['quest_progress'][quest['id']] = 0

def assign_weekly_quests():
    """HaftalÄ±k gÃ¶revleri ata"""
    # HaftalÄ±k gÃ¶revleri sÄ±fÄ±rla
    player['active_quests'] = [q for q in player['active_quests'] if q not in [w['id'] for w in quest_system['weekly_quests']]]
    
    # Rastgele 2 haftalÄ±k gÃ¶rev seÃ§
    selected_quests = random.sample(quest_system['weekly_quests'], min(2, len(quest_system['weekly_quests'])))
    
    # SeÃ§ilen gÃ¶revleri aktif gÃ¶revlere ekle
    for quest in selected_quests:
        player['active_quests'].append(quest['id'])
        player['quest_progress'][quest['id']] = 0

def check_quest_completion():
    """GÃ¶rev tamamlanma durumunu kontrol et"""
    completed_quests = []
    
    for quest_id in player['active_quests']:
        if quest_id in quest_definitions:
            quest = quest_definitions[quest_id]
            
            # GÃ¶rev tamamlandÄ± mÄ± kontrol et
            if quest['check_completion']():
                # GÃ¶revi tamamlandÄ± olarak iÅŸaretle
                completed_quests.append(quest_id)
                
                # Ã–dÃ¼lleri ver
                give_quest_rewards(quest)
                
                # Tamamlanan gÃ¶revi gÃ¶ster
                show_quest_completion(quest)
    
    # Tamamlanan gÃ¶revleri aktif gÃ¶revlerden Ã§Ä±kar
    for quest_id in completed_quests:
        player['active_quests'].remove(quest_id)
        player['completed_quests'].append(quest_id)
    
    # GÃ¶rev UI'Ä±nÄ± gÃ¼ncelle
    update_quest_ui()

def give_quest_rewards(quest):
    """GÃ¶rev Ã¶dÃ¼llerini ver"""
    reward = quest['reward']
    
    # Para Ã¶dÃ¼lÃ¼
    if 'money' in reward:
        player['money'] += reward['money']
    
    # Deneyim Ã¶dÃ¼lÃ¼
    if 'experience' in reward:
        player['experience']['current_xp'] += reward['experience']
        player['experience']['total_xp'] += reward['experience']
        
        # Seviye atlama kontrolÃ¼
        while player['experience']['current_xp'] >= player['experience']['next_level_xp']:
            player['experience']['current_xp'] -= player['experience']['next_level_xp']
            player['experience']['level'] += 1
            player['experience']['next_level_xp'] = calculate_next_level_xp(player['experience']['level'])
            show_level_up()
    
    # BaÅŸarÄ± Ã¶dÃ¼lÃ¼
    if 'achievement' in reward:
        if reward['achievement'] not in player['achievements']:
            player['achievements'].append(reward['achievement'])

def show_quest_completion(quest):
    """GÃ¶rev tamamlanma bildirimini gÃ¶ster"""
    # Ana bildirim metni
    completion_text = Text(
        text=f"GÃ¶rev TamamlandÄ±: {quest['title']}",
        position=(0, 0.6),
        scale=2,
        color=color.gold
    )
    
    # Ã–dÃ¼l detaylarÄ±
    reward_text = None
    if 'money' in quest['reward']:
        reward_text = Text(
            text=f"Ã–dÃ¼l: +${quest['reward']['money']:,.2f}",
            position=(0, 0.5),
            scale=1.5,
            color=color.green
        )
    
    # Metinleri belirli sÃ¼re sonra kaldÄ±r
    destroy(completion_text, delay=4)
    if reward_text:
        destroy(reward_text, delay=4)

def show_level_up():
    """Seviye atlama bildirimini gÃ¶ster"""
    level_text = Text(
        text=f"Seviye AtladÄ±nÄ±z! Yeni Seviye: {player['experience']['level']}",
        position=(0, 0.4),
        scale=2,
        color=color.yellow
    )
    destroy(level_text, delay=4)

def calculate_next_level_xp(current_level):
    """Sonraki seviye iÃ§in gereken XP'yi hesapla"""
    return int(1000 * (1.5 ** (current_level - 1)))

def create_quest_ui():
    """GÃ¶rev UI'Ä±nÄ± oluÅŸtur"""
    # GÃ¶rev paneli
    quest_ui['panel'] = Entity(
        parent=camera.ui,
        model='quad',
        scale=(0.8, 0.6),
        position=(0, 0),
        color=color.rgba(0, 0, 0, 0.7),
        visible=False
    )
    
    # GÃ¶rev baÅŸlÄ±ÄŸÄ±
    Text(
        parent=quest_ui['panel'],
        text='GÃ¶revler',
        position=(0, 0.25),
        scale=2,
        color=color.white
    )
    
    # Aktif gÃ¶revler baÅŸlÄ±ÄŸÄ±
    quest_ui['active_quests_text'] = Text(
        parent=quest_ui['panel'],
        text='Aktif GÃ¶revler:',
        position=(-0.35, 0.15),
        scale=1.5,
        color=color.white
    )
    
    # Tamamlanan gÃ¶revler baÅŸlÄ±ÄŸÄ±
    quest_ui['completed_quests_text'] = Text(
        parent=quest_ui['panel'],
        text='Tamamlanan GÃ¶revler:',
        position=(-0.35, -0.15),
        scale=1.5,
        color=color.white
    )
    
    # GÃ¶rev kapatma butonu
    Button(
        parent=quest_ui['panel'],
        text='Kapat',
        color=color.red,
        position=(0, -0.25),
        scale=(0.2, 0.05),
        on_click=Func(lambda: setattr(quest_ui['panel'], 'visible', False))
    )
    
    # GÃ¶rev butonu
    Button(
        parent=camera.ui,
        text='GÃ¶revler',
        color=color.azure,
        position=(0.7, 0.4),
        scale=(0.2, 0.05),
        on_click=Func(lambda: setattr(quest_ui['panel'], 'visible', True))
    )
    
    # GÃ¶rev UI'Ä±nÄ± gÃ¼ncelle
    update_quest_ui()

def update_quest_ui():
    """GÃ¶rev UI'Ä±nÄ± gÃ¼ncelle"""
    # Mevcut gÃ¶rev Ã¶ÄŸelerini temizle
    for item in quest_ui['quest_items']:
        destroy(item)
    quest_ui['quest_items'] = []
    
    # Aktif gÃ¶revleri gÃ¶ster
    y_position = 0.1
    for quest_id in player['active_quests']:
        if quest_id in quest_definitions:
            quest = quest_definitions[quest_id]
            
            # GÃ¶rev baÅŸlÄ±ÄŸÄ±
            quest_ui['quest_items'].append(
                Text(
                    parent=quest_ui['panel'],
                    text=quest['title'],
                    position=(-0.3, y_position),
                    scale=1.2,
                    color=color.white
                )
            )
            
            # GÃ¶rev aÃ§Ä±klamasÄ±
            quest_ui['quest_items'].append(
                Text(
                    parent=quest_ui['panel'],
                    text=quest['description'],
                    position=(-0.3, y_position - 0.05),
                    scale=0.8,
                    color=color.light_gray
                )
            )
            
            # GÃ¶rev Ã¶dÃ¼lÃ¼
            reward_text = f"Ã–dÃ¼l: ${quest['reward']['money']:,.2f}"
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
    
    # Tamamlanan gÃ¶revleri gÃ¶ster
    y_position = -0.2
    for quest_id in player['completed_quests'][-5:]:  # Son 5 tamamlanan gÃ¶revi gÃ¶ster
        if quest_id in quest_definitions:
            quest = quest_definitions[quest_id]
            
            # GÃ¶rev baÅŸlÄ±ÄŸÄ±
            quest_ui['quest_items'].append(
                Text(
                    parent=quest_ui['panel'],
                    text=quest['title'],
                    position=(-0.3, y_position),
                    scale=1.2,
                    color=color.light_gray
                )
            )
            
            # TamamlandÄ± iÅŸareti
            quest_ui['quest_items'].append(
                Text(
                    parent=quest_ui['panel'],
                    text="âœ“ TamamlandÄ±",
                    position=(0.2, y_position),
                    scale=0.8,
                    color=color.green
                )
            )
            
            y_position -= 0.1

def calculate_daily_profit():
    """GÃ¼nlÃ¼k kÃ¢rÄ± hesapla"""
    today = datetime.now().date()
    today_trades = [t for t in player['trading_history'] if t['timestamp'].date() == today]
    
    profit = 0
    for trade in today_trades:
        if trade['type'] == 'sell':
            # SatÄ±ÅŸ iÅŸleminden kÃ¢r hesapla
            buy_trades = [t for t in player['trading_history'] if t['stock'] == trade['stock'] and t['type'] == 'buy' and t['timestamp'].date() <= today]
            if buy_trades:
                # En eski alÄ±m fiyatÄ±nÄ± bul
                oldest_buy = min(buy_trades, key=lambda t: t['timestamp'])
                buy_price = oldest_buy['price']
                sell_price = trade['price']
                profit += (sell_price - buy_price) * trade['amount']
    
    return profit

def calculate_weekly_growth():
    """HaftalÄ±k bÃ¼yÃ¼meyi hesapla"""
    # BaÅŸlangÄ±Ã§ portfÃ¶y deÄŸeri (1 hafta Ã¶nce)
    week_ago = datetime.now() - timedelta(days=7)
    week_ago_trades = [t for t in player['trading_history'] if t['timestamp'] <= week_ago]
    
    # Åžu anki portfÃ¶y deÄŸeri
    current_value = calculate_portfolio_value()
    
    # HaftalÄ±k bÃ¼yÃ¼me oranÄ±
    if current_value > 0:
        return (current_value / 100000) - 1  # BaÅŸlangÄ±Ã§ deÄŸerine gÃ¶re bÃ¼yÃ¼me
    return 0

def update_market_state():
    """Piyasa durumunu gÃ¼ncelle"""
    current_time = datetime.now()
    if (current_time - market_state['last_update']).seconds >= 30:  # Her 30 saniyede bir gÃ¼ncelle
        # Piyasa trendini gÃ¼ncelle
        trend_chance = random.random()
        if trend_chance < 0.4:
            market_state['trend'] = 'stable'
        elif trend_chance < 0.7:
            market_state['trend'] = 'bull'
        else:
            market_state['trend'] = 'bear'
        
        # Volatiliteyi gÃ¼ncelle
        market_state['volatility'] = random.uniform(0.3, 0.8)
        
        # Piyasa olaylarÄ± oluÅŸtur
        if random.random() < 0.2:  # %20 ÅŸans
            event = generate_market_event()
            market_state['market_events'].append(event)
            show_market_event(event)
            apply_market_event(event)
        
        # Oyuncuya Ã¶zel olaylar oluÅŸtur
        if random.random() < 0.15:  # %15 ÅŸans
            player_event = generate_player_event()
            if player_event:
                show_player_event(player_event)
                apply_player_event(player_event)
        
        # GÃ¶rev tamamlanma durumunu kontrol et
        check_quest_completion()
        
        market_state['last_update'] = current_time

def update():
    """Ana oyun dÃ¶ngÃ¼sÃ¼"""
    # Piyasa gÃ¼ncellemesi
    update_market()
    
    # UI gÃ¼ncellemesi
    update_ui()
    
    # GÃ¶rev kontrolÃ¼
    check_quests()
    
    # Otomatik kayÄ±t
    if game_settings['auto_save']:
        auto_save()

def update_market():
    """Piyasa durumunu gÃ¼ncelle"""
    current_time = datetime.now()
    
    # Piyasa gÃ¼ncellemesi
    if (current_time - market_state['last_update']).seconds >= game_settings['market_update_interval']:
        # Trend gÃ¼ncelleme
        update_market_trend()
        
        # Fiyat gÃ¼ncelleme
        update_stock_prices()
        
        # Olay kontrolÃ¼
        check_market_events()
        
        market_state['last_update'] = current_time

def update_market_trend():
    """Piyasa trendini gÃ¼ncelle"""
    trend_chance = random.random()
    
    # Zorluk seviyesine gÃ¶re trend olasÄ±lÄ±klarÄ±
    if game_settings['difficulty'] == 'easy':
        if trend_chance < 0.5:  # %50 ÅŸans
            market_state['trend'] = 'bull'
        elif trend_chance < 0.8:  # %30 ÅŸans
            market_state['trend'] = 'stable'
        else:  # %20 ÅŸans
            market_state['trend'] = 'bear'
    elif game_settings['difficulty'] == 'normal':
        if trend_chance < 0.4:  # %40 ÅŸans
            market_state['trend'] = 'bull'
        elif trend_chance < 0.7:  # %30 ÅŸans
            market_state['trend'] = 'stable'
        else:  # %30 ÅŸans
            market_state['trend'] = 'bear'
    else:  # hard
        if trend_chance < 0.3:  # %30 ÅŸans
            market_state['trend'] = 'bull'
        elif trend_chance < 0.5:  # %20 ÅŸans
            market_state['trend'] = 'stable'
        else:  # %50 ÅŸans
            market_state['trend'] = 'bear'
    
    # Volatilite gÃ¼ncelleme
    market_state['volatility'] = random.uniform(
        0.2 if game_settings['difficulty'] == 'easy' else 0.3 if game_settings['difficulty'] == 'normal' else 0.4,
        0.5 if game_settings['difficulty'] == 'easy' else 0.7 if game_settings['difficulty'] == 'normal' else 0.9
    )

def update_stock_prices():
    """Hisse senedi fiyatlarÄ±nÄ± gÃ¼ncelle"""
    for symbol, data in player['portfolio'].items():
        base_price = data['price']
        
        # Trend etkisi
        trend_effect = {
            'bull': random.uniform(0.001, 0.01),
            'stable': random.uniform(-0.003, 0.003),
            'bear': random.uniform(-0.01, -0.001)
        }[market_state['trend']]
        
        # SektÃ¶r etkisi
        sector_effect = calculate_sector_effect(data['sector'])
        
        # Volatilite etkisi
        volatility_effect = random.uniform(-market_state['volatility'], market_state['volatility'])
        
        # Toplam deÄŸiÅŸim
        total_change = trend_effect + sector_effect + volatility_effect
        
        # Zorluk seviyesine gÃ¶re deÄŸiÅŸim sÄ±nÄ±rlamasÄ±
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
    """SektÃ¶r bazlÄ± fiyat etkisini hesapla"""
    sector_trends = {
        'tech': random.uniform(-0.005, 0.008),
        'auto': random.uniform(-0.004, 0.006),
        'retail': random.uniform(-0.003, 0.005),
        'media': random.uniform(-0.004, 0.007),
        'finance': random.uniform(-0.003, 0.004)
    }
    return sector_trends.get(sector, 0)

def check_market_events():
    """Piyasa olaylarÄ±nÄ± kontrol et"""
    if random.random() < game_settings['event_chance']:
        event = generate_market_event()
        if event:
            market_state['market_events'].append(event)
            apply_market_event(event)
            show_market_event(event)

def generate_market_event():
    """Piyasa olayÄ± oluÅŸtur"""
    event_types = {
        'global': [
            {
                'title': 'KÃ¼resel Ekonomik BÃ¼yÃ¼me',
                'description': 'KÃ¼resel ekonomik bÃ¼yÃ¼me beklentileri yÃ¼kseldi!',
                'effect': {'market_trend': 'bull', 'volatility': -0.1},
                'duration': 300,
                'probability': 0.2
            },
            {
                'title': 'Ekonomik Kriz',
                'description': 'KÃ¼resel ekonomik kriz endiÅŸeleri artÄ±yor!',
                'effect': {'market_trend': 'bear', 'volatility': 0.2},
                'duration': 300,
                'probability': 0.1
            }
        ],
        'sector': [
            {
                'title': 'Teknoloji AtÄ±lÄ±mÄ±',
                'description': 'Yeni teknolojik geliÅŸmeler sektÃ¶rÃ¼ hareketlendirdi!',
                'effect': {'sector': 'tech', 'change': 0.05},
                'duration': 180,
                'probability': 0.15
            },
            {
                'title': 'Otomotiv Krizi',
                'description': 'Tedarik zinciri sorunlarÄ± otomotiv sektÃ¶rÃ¼nÃ¼ vuruyor!',
                'effect': {'sector': 'auto', 'change': -0.05},
                'duration': 180,
                'probability': 0.15
            }
        ],
        'company': [
            {
                'title': 'ÃœrÃ¼n LansmanÄ±',
                'description': 'AAPL yeni Ã¼rÃ¼nlerini tanÄ±ttÄ±!',
                'effect': {'symbol': 'AAPL', 'change': 0.08},
                'duration': 120,
                'probability': 0.2
            },
            {
                'title': 'CEO Ä°stifasÄ±',
                'description': 'TSLA CEO\'su istifa etti!',
                'effect': {'symbol': 'TSLA', 'change': -0.08},
                'duration': 120,
                'probability': 0.1
            }
        ]
    }
    
    # Olay tÃ¼rÃ¼ seÃ§
    event_type = random.choice(list(event_types.keys()))
    events = event_types[event_type]
    
    # OlasÄ±lÄ±k kontrolÃ¼
    for event in events:
        if random.random() < event['probability']:
            return event
    
    return None

def apply_market_event(event):
    """Piyasa olayÄ±nÄ± uygula"""
    effect = event['effect']
    
    # Piyasa trendi etkisi
    if 'market_trend' in effect:
        market_state['trend'] = effect['market_trend']
    
    # Volatilite etkisi
    if 'volatility' in effect:
        market_state['volatility'] = max(0.1, min(1.0, market_state['volatility'] + effect['volatility']))
    
    # SektÃ¶r etkisi
    if 'sector' in effect:
        for symbol, data in player['portfolio'].items():
            if data['sector'] == effect['sector']:
                data['price'] *= (1 + effect['change'])
    
    # Åžirket etkisi
    if 'symbol' in effect:
        if effect['symbol'] in player['portfolio']:
            player['portfolio'][effect['symbol']]['price'] *= (1 + effect['change'])

def show_market_event(event):
    """Piyasa olayÄ±nÄ± gÃ¶ster"""
    # Bildirim paneli
    notification = Entity(
        parent=camera.ui,
        model='quad',
        scale=(0.6, 0.2),
        position=(0, 0.3),
        color=color.rgba(0, 0, 0, 0.9)
    )
    
    # BaÅŸlÄ±k
    title_text = Text(
        parent=notification,
        text=event['title'],
        position=(0, 0.05),
        scale=1.5,
        color=color.yellow
    )
    
    # AÃ§Ä±klama
    desc_text = Text(
        parent=notification,
        text=event['description'],
        position=(0, -0.02),
        scale=1.2,
        color=color.white
    )
    
    # Efekt aÃ§Ä±klamasÄ±
    effect = event['effect']
    effect_text = ""
    
    if 'market_trend' in effect:
        effect_text = "Piyasa trendi deÄŸiÅŸti!"
    elif 'sector' in effect:
        effect_text = f"{effect['sector'].upper()} sektÃ¶rÃ¼ etkilendi!"
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
    """PortfÃ¶y deÄŸerini hesapla"""
    total_value = player['money']
    for symbol, data in player['portfolio'].items():
        total_value += data['shares'] * data['price']
    return total_value

def calculate_risk_score():
    """Risk skorunu hesapla"""
    # PortfÃ¶y Ã§eÅŸitliliÄŸi (0-1 arasÄ±)
    portfolio_diversity = calculate_portfolio_diversity()
    
    # BorÃ§/gelir oranÄ± (0-1 arasÄ±)
    debt_to_income = calculate_debt_to_income_ratio()
    
    # Toplam risk skoru (0-1 arasÄ±)
    risk_score = (1 - portfolio_diversity) * 0.6 + debt_to_income * 0.4
    return min(max(risk_score, 0), 1)

def calculate_portfolio_diversity():
    """PortfÃ¶y Ã§eÅŸitliliÄŸini hesapla"""
    total_value = calculate_portfolio_value()
    if total_value == 0:
        return 0
    
    # Her sektÃ¶rdeki yatÄ±rÄ±m oranÄ±nÄ± hesapla
    sector_weights = {}
    for symbol, data in player['portfolio'].items():
        sector = data['sector']
        value = data['shares'] * data['price']
        sector_weights[sector] = sector_weights.get(sector, 0) + value / total_value
    
    # Herfindahl-Hirschman Index'ini hesapla (ters Ã§evrilmiÅŸ)
    hhi = sum(weight * weight for weight in sector_weights.values())
    diversity = 1 - hhi
    return min(max(diversity, 0), 1)

def calculate_debt_to_income_ratio():
    """BorÃ§/gelir oranÄ±nÄ± hesapla"""
    total_income = sum(t['amount'] for t in player.get('trading_history', []) 
                      if t['type'] == 'profit' and (datetime.now() - t['timestamp']).days <= 30)
    total_debt = sum(t['amount'] for t in player.get('trading_history', [])
                    if t['type'] == 'loss' and (datetime.now() - t['timestamp']).days <= 30)
    
    if total_income == 0:
        return 1 if total_debt > 0 else 0
    
    ratio = total_debt / total_income
    return min(max(ratio, 0), 1)

def update_ui():
    """UI'Ä± gÃ¼ncelle"""
    # Para ve portfÃ¶y deÄŸerini gÃ¼ncelle
    ui['text_elements']['money'].text = f"Para: ${player['money']:,.2f}"
    ui['text_elements']['portfolio_value'].text = f"PortfÃ¶y: ${calculate_portfolio_value():,.2f}"
    ui['text_elements']['risk_score'].text = f"Risk: {calculate_risk_score():.2f}"
    
    # Hisse senedi fiyatlarÄ±nÄ± gÃ¼ncelle
    for symbol, data in player['portfolio'].items():
        if symbol in ui['text_elements']:
            ui['text_elements'][symbol].text = f"{symbol}: ${data['price']:,.2f}"
    
    # Hisse senedi butonlarÄ±nÄ± gÃ¼ncelle
    update_stock_buttons()
    
    # GÃ¶revleri gÃ¼ncelle
    update_quest_ui()
    
    # Bildirimleri gÃ¼ncelle
    update_notifications()

def update_stock_buttons():
    """Hisse senedi butonlarÄ±nÄ± gÃ¼ncelle"""
    for symbol, data in player['portfolio'].items():
        # AlÄ±m butonu
        if symbol + '_buy' in ui['buttons']:
            ui['buttons'][symbol + '_buy'].enabled = player['money'] >= data['price']
        
        # SatÄ±m butonu
        if symbol + '_sell' in ui['buttons']:
            ui['buttons'][symbol + '_sell'].enabled = data['shares'] > 0

def update_notifications():
    """Bildirimleri gÃ¼ncelle"""
    current_time = datetime.now()
    
    # SÃ¼resi dolmuÅŸ bildirimleri kaldÄ±r
    ui['notifications'] = [n for n in ui['notifications'] 
                         if (current_time - n['timestamp']).seconds < 5]
    
    # Bildirimleri gÃ¶ster
    for i, notification in enumerate(ui['notifications']):
        if 'text' in notification:
            notification['text'].y = -0.3 - i * 0.1

def buy_stock(symbol):
    """Hisse senedi satÄ±n al"""
    stock = player['portfolio'][symbol]
    price = stock['price']
    
    # Yeterli para var mÄ± kontrol et
    if player['money'] < price:
        show_notification('Yeterli paranÄ±z yok!', color.red)
        return
    
    # Ä°ÅŸlemi gerÃ§ekleÅŸtir
    player['money'] -= price
    stock['shares'] += 1
    
    # Ä°ÅŸlem kaydÄ±nÄ± tut
    trade = {
        'type': 'buy',
        'symbol': symbol,
        'price': price,
        'shares': 1,
        'total': price,
        'timestamp': datetime.now()
    }
    player['trading_history'].append(trade)
    
    # Ä°statistikleri gÃ¼ncelle
    player['stats']['total_trades'] += 1
    
    # Bildirimi gÃ¶ster
    show_notification(f'{symbol} hissesinden 1 adet satÄ±n alÄ±ndÄ±.', color.green)
    
    # UI'Ä± gÃ¼ncelle
    update_ui()

def sell_stock(symbol):
    """Hisse senedi sat"""
    stock = player['portfolio'][symbol]
    price = stock['price']
    
    # Yeterli hisse var mÄ± kontrol et
    if stock['shares'] <= 0:
        show_notification('Yeterli hisseniz yok!', color.red)
        return
    
    # Ä°ÅŸlemi gerÃ§ekleÅŸtir
    player['money'] += price
    stock['shares'] -= 1
    
    # Ä°ÅŸlem kaydÄ±nÄ± tut
    trade = {
        'type': 'sell',
        'symbol': symbol,
        'price': price,
        'shares': 1,
        'total': price,
        'timestamp': datetime.now()
    }
    player['trading_history'].append(trade)
    
    # Ä°statistikleri gÃ¼ncelle
    player['stats']['total_trades'] += 1
    
    # Bildirimi gÃ¶ster
    show_notification(f'{symbol} hissesinden 1 adet satÄ±ldÄ±.', color.green)
    
    # UI'Ä± gÃ¼ncelle
    update_ui()

def check_quests():
    """GÃ¶revleri kontrol et"""
    # GÃ¼nlÃ¼k gÃ¶revleri kontrol et
    for quest in quest_system['daily_quests']:
        if not quest.get('completed', False) and quest_definitions[quest['id']]['check_completion']():
            quest['completed'] = True
            give_quest_rewards(quest)
            show_quest_completion(quest)
    
    # HaftalÄ±k gÃ¶revleri kontrol et
    for quest in quest_system['weekly_quests']:
        if not quest.get('completed', False) and quest_definitions[quest['id']]['check_completion']():
            quest['completed'] = True
            give_quest_rewards(quest)
            show_quest_completion(quest)
    
    # BaÅŸarÄ± gÃ¶revlerini kontrol et
    for quest in quest_system['achievement_quests']:
        if not quest.get('completed', False) and quest_definitions[quest['id']]['check_completion']():
            quest['completed'] = True
            give_quest_rewards(quest)
            show_quest_completion(quest)
            
    # Ã–ÄŸretici gÃ¶revleri kontrol et
    for quest in quest_system['tutorial_quests']:
        if not quest.get('completed', False) and quest_definitions[quest['id']]['check_completion']():
            quest['completed'] = True
            give_quest_rewards(quest)
            show_quest_completion(quest)
            
    # Seviye atlamayÄ± kontrol et
    check_level_up()

def check_level_up():
    """Seviye atlamayÄ± kontrol et"""
    while player['experience']['current_xp'] >= player['experience']['next_level_xp']:
        # Seviye atla
        player['experience']['level'] += 1
        player['experience']['current_xp'] -= player['experience']['next_level_xp']
        player['experience']['next_level_xp'] = calculate_next_level_xp(player['experience']['level'])
        
        # Seviye atlama Ã¶dÃ¼llerini ver
        rewards = {
            'money': 1000 * player['experience']['level'],
            'experience': 0
        }
        give_quest_rewards({'reward': rewards})
        
        # Seviye atlama bildirimini gÃ¶ster
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
        # Karakter seÃ§im paneli
        self.ui_elements['panel'] = Entity(
            model='quad',
            scale=(1, 1),
            color=color.black90,
            position=(0, 0, -1)
        )
        
        # Karakter kartlarÄ±
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
            
            # SeÃ§im butonu
            Button(
                text='SeÃ§',
                position=(-0.5 + i * 0.3, -0.1, -0.8),
                scale=(0.1, 0.05),
                on_click=Func(self.select_character, char),
                parent=self.ui_elements['panel']
            )
            
    def select_character(self, character):
        self.selected_character = character
        # Oyuncu verilerini gÃ¼ncelle
        player['money'] = character['starting_money']
        player['stats']['risk_tolerance'] = character['advantages']['risk_tolerance']
        # Karakter seÃ§im ekranÄ±nÄ± kapat
        destroy(self.ui_elements['panel'])
        # Oyunu baÅŸlat
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
        # GÃ¶rev paneli
        self.ui_elements['panel'] = Entity(
            model='quad',
            scale=(0.4, 0.3),
            color=color.black90,
            position=(0.7, 0.6, -1)
        )
        
        # GÃ¶rev baÅŸlÄ±ÄŸÄ±
        self.ui_elements['title'] = Text(
            text='GÃ¶revler',
            position=(0.7, 0.7, -0.9),
            scale=2,
            parent=self.ui_elements['panel']
        )
        
        # GÃ¶rev listesi
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
            mission = level['missions'][0]  # Ä°lk gÃ¶revi gÃ¶ster
            
            # GÃ¶rev bilgilerini gÃ¼ncelle
            Text(
                text=f"Seviye: {level['name']}",
                position=(0.7, 0.6, -0.8),
                scale=1.5,
                parent=self.ui_elements['panel']
            )
            
            Text(
                text=f"GÃ¶rev: {mission['title']}",
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
                # DiÄŸer gereksinimler iÃ§in kontroller...
                
            if completed:
                self.complete_mission()
                
    def complete_mission(self):
        if self.current_mission is None:
            return
            
        if isinstance(self.current_mission, dict) and 'rewards' in self.current_mission:
            rewards = self.current_mission['rewards']
            player['money'] += rewards.get('money', 0)
            player['experience']['current_xp'] += rewards.get('experience', 0)
        
        # GÃ¶rev tamamlandÄ± bildirimi
        show_notification('ðŸ“ˆ GÃ¶rev BaÅŸarÄ±yla TamamlandÄ±!', color.green)
        
        # Yeni gÃ¶rev atama
        self.assign_next_mission()
        
    def assign_next_mission(self):
        level = self.levels[self.current_level - 1]
        if len(level['missions']) > 1:
            self.current_mission = level['missions'][1]
        else:
            # Seviye tamamlandÄ±
            self.level_up()
            
    def level_up(self):
        self.current_level += 1
        if self.current_level <= len(self.levels):
            # Yeni seviye arka planÄ±nÄ± yÃ¼kle
            self.load_level_background()
            # Ä°lk gÃ¶revi ata
            self.current_mission = self.levels[self.current_level - 1]['missions'][0]
            show_notification(f'ðŸŽ‰ Seviye {self.current_level} AÃ§Ä±ldÄ±!', color.yellow)
            
    def load_level_background(self):
        level = self.levels[self.current_level - 1]
        background = level['background']
        # Arka plan deÄŸiÅŸtirme iÅŸlemi
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
        
        # Yeni Ã¶znitelikler
        self.last_update = time.time()
        self.update_interval = 0.016  # ~60 FPS
        self.is_paused = False
        self.is_mobile = platform.system().lower() in ['android', 'ios']
        self.ar_manager = None  # AR yÃ¶neticisi mobil platformlarda baÅŸlatÄ±lacak
        
        # OlaylarÄ± ve kartlarÄ± yÃ¼kle
        self.load_game_data()

    def load_game_data(self):
        """Oyun verilerini yÃ¼kle"""
        self.events = self.load_events()
        self.loot_cards = self.load_loot_cards()

    def load_events(self):
        """Olay verilerini yÃ¼kle"""
        try:
            with open('games/ursina_game/arena_events.json', 'r', encoding='utf-8') as f:
                return json.load(f)['events']
        except (FileNotFoundError, KeyError, json.JSONDecodeError):
            return []

    def load_loot_cards(self):
        """Kart verilerini yÃ¼kle"""
        try:
            with open('games/ursina_game/loot_cards.json', 'r', encoding='utf-8') as f:
                return json.load(f)['cards']
        except (FileNotFoundError, KeyError, json.JSONDecodeError):
            return []

    def alis_yap(self):
        """AlÄ±ÅŸ iÅŸlemi yap"""
        if self.player and hasattr(self.player, 'money') and self.player.money >= 1000:
            self.player.money -= 1000
            return True
        return False

    def satis_yap(self):
        """SatÄ±ÅŸ iÅŸlemi yap"""
        if self.player and hasattr(self.player, 'shares') and self.player.shares > 0:
            self.player.money += 1000
            self.player.shares -= 1
            return True
        return False

    def olay_guncelle(self):
        """OlaylarÄ± gÃ¼ncelle"""
        current_time = time.time()
        for event in self.events:
            if 'start_time' in event and current_time - event['start_time'] > event.get('duration', 0):
                self.generate_new_event()

    def generate_new_event(self):
        """Yeni olay oluÅŸtur"""
        event_types = ['market_change', 'resource_discovery', 'crisis']
        new_event = {
            'type': random.choice(event_types),
            'start_time': time.time(),
            'duration': random.randint(30, 180)
        }
        self.events.append(new_event)

    def update(self):
        """Oyun durumunu gÃ¼ncelle"""
        current_time = time.time()
        if current_time - self.last_update < self.update_interval:
            return
        self.last_update = current_time
        
        if self.is_paused:
            return
            
        # Oyun gÃ¼ncellemeleri
        if self.held_keys['left mouse']:
            self.alis_yap()
            
        if self.held_keys['right mouse']:
            self.satis_yap()
            
        # AR gÃ¼ncellemeleri
        if self.is_mobile and self.ar_manager:
            self.ar_manager.ar_nesne_guncelle()
            
        # Olay gÃ¼ncellemeleri
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
    
    # Oyun modlarÄ±
    battle_royale = BattleRoyaleMode()
    tournament = FastFinanceTournament()
    
    # Ana menÃ¼
    menu = Entity(parent=camera.ui)
    Button(text='Battle Royale Modu', scale=(0.3, 0.1), position=(0, 0.2), parent=menu)
    Button(text='HÄ±zlÄ± Finans TurnuvasÄ±', scale=(0.3, 0.1), position=(0, -0.2), parent=menu)
    
    app.run()

def generate_player_event(player=None):
    if player is None:
        return None
        
    events = [
        {
            'type': 'market_opportunity',
            'description': 'Yeni bir yatÄ±rÄ±m fÄ±rsatÄ±!',
            'effect': lambda p: setattr(p, 'market_multiplier', p.market_multiplier * 1.2)
        },
        {
            'type': 'resource_discovery',
            'description': 'Yeni kaynaklar keÅŸfedildi!',
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
        
        # Oyun ayarlarÄ±
        window.title = "FinAsis - Ticaretin Ä°zinde"
        window.borderless = False
        window.fullscreen = False
        window.exit_button.visible = False
        
        # Oyun durumu
        self.game_state = {
            'is_paused': False,
            'current_time': time.time(),
            'game_speed': 1.0,  # Oyun hÄ±zÄ± Ã§arpanÄ±
            'difficulty': 'normal',  # easy, normal, hard
            'save_interval': 60,  # Otomatik kayÄ±t aralÄ±ÄŸÄ±
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
        
        # GÃ¶rev sistemi
        self.quest_system = {
            'active_quests': [],
            'completed_quests': [],
            'daily_quests': [],
            'achievements': [],
            'rewards': {}
        }
        
        # Pazar araÅŸtÄ±rmasÄ±
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
        
        # Ãœretim sistemi
        self.production_system = {
            'factories': [],
            'production_lines': [],
            'inventory': {},
            'supply_chain': {},
            'quality_control': {},
            'efficiency': 1.0
        }
        
        # Ä°nsan kaynaklarÄ±
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
        
        # Grafik ayarlarÄ±
        self.graphics_settings = {
            'quality': 'high',
            'shadows': True,
            'particles': True,
            'effects': True
        }
        
        # Ã‡oklu oyuncu desteÄŸi
        self.multiplayer = {
            'is_online': False,
            'players': [],
            'trades': [],
            'alliances': [],
            'competitions': []
        }
        
        # BaÅŸlangÄ±Ã§ durumu
        self.initialize_game()
        
        # EÄŸitim sistemi
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
                    {'name': 'Temel Ãœretim', 'duration': 2, 'cost': 1000, 'skill': 'production'}
                ],
                'advanced': [
                    {'name': 'Ä°leri Finans', 'duration': 4, 'cost': 2000, 'skill': 'finance'},
                    {'name': 'Ä°leri Pazarlama', 'duration': 4, 'cost': 2000, 'skill': 'marketing'},
                    {'name': 'Ä°leri Ãœretim', 'duration': 4, 'cost': 2000, 'skill': 'production'}
                ],
                'management': [
                    {'name': 'Liderlik EÄŸitimi', 'duration': 6, 'cost': 3000, 'skill': 'management'},
                    {'name': 'Stratejik YÃ¶netim', 'duration': 6, 'cost': 3000, 'skill': 'management'},
                    {'name': 'Proje YÃ¶netimi', 'duration': 6, 'cost': 3000, 'skill': 'management'}
                ]
            }
        }
        
        # EÄŸitim paneli
        self.training_panel = Entity(
            model='quad',
            texture='white_cube',
            scale=(0.3, 0.4),
            position=(0.7, 0.2),
            color=color.rgba(0, 0, 0, 0.7)
        )
        
        # Kalite yÃ¶netim sistemi
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
        
        # SÃ¼rdÃ¼rÃ¼lebilirlik sistemi
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
        
        # SÃ¼rdÃ¼rÃ¼lebilirlik paneli
        self.sustainability_panel = Entity(
            model='quad',
            texture='white_cube',
            scale=(0.3, 0.4),
            position=(0.7, -0.3),
            color=color.rgba(0, 0, 0, 0.7)
        )
        
        # Kriz yÃ¶netim sistemi
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
        
        # Kriz yÃ¶netim paneli
        self.crisis_panel = Entity(
            model='quad',
            texture='white_cube',
            scale=(0.3, 0.4),
            position=(0.7, -0.3),
            color=color.rgba(0, 0, 0, 0.7)
        )
        
        # UluslararasÄ± ticaret sistemi
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
        
        # UluslararasÄ± ticaret paneli
        self.international_trade_panel = Entity(
            model='quad',
            texture='white_cube',
            scale=(0.3, 0.4),
            position=(0.7, -0.3),
            color=color.rgba(0, 0, 0, 0.7)
        )
        
        # Dijital dÃ¶nÃ¼ÅŸÃ¼m sistemi
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
        
        # Dijital dÃ¶nÃ¼ÅŸÃ¼m paneli
        self.digital_panel = Entity(
            model='quad',
            texture='white_cube',
            scale=(0.3, 0.4),
            position=(0.7, -0.3),
            color=color.rgba(0, 0, 0, 0.7)
        )
        
        # Ä°novasyon yÃ¶netim sistemi
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
        
        # Ä°novasyon yÃ¶netim paneli
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
        
        # Tedarik zinciri yÃ¶netim sistemi
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
        
        # Proje yÃ¶netim sistemi
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
        
        # SaÄŸlÄ±k yÃ¶netim sistemi
        self.health_system = {
            'player_age': 18,  # VarsayÄ±lan yaÅŸ
            'play_time': 0,    # Toplam oyun sÃ¼resi (saniye)
            'break_time': 0,   # Toplam mola sÃ¼resi (saniye)
            'last_break': time.time(),
            'health_tips': [],
            'recommended_play_time': 7200,  # 2 saat
            'recommended_break_interval': 1800,  # 30 dakika
            'break_duration': 300  # 5 dakika
        }
        
        # SaÄŸlÄ±k paneli
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
                    "Omuz Ã§evirme",
                    "Kol esnetme",
                    "Bel dÃ¶ndÃ¼rme",
                    "Bacak esnetme"
                ],
                'strength': [
                    "ÅžÄ±nav",
                    "Mekik",
                    "Squat",
                    "Plank",
                    "Lunge"
                ],
                'cardio': [
                    "Yerinde koÅŸu",
                    "ZÄ±plama",
                    "Merdiven Ã§Ä±kma",
                    "Dans etme",
                    "Ä°p atlama"
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
        """Oyunu baÅŸlatÄ±r ve baÅŸlangÄ±Ã§ durumunu ayarlar"""
        # BaÅŸlangÄ±Ã§ gÃ¶revlerini yÃ¼kle
        self.load_initial_quests()
        
        # BaÅŸlangÄ±Ã§ binalarÄ±nÄ± oluÅŸtur
        self.create_initial_buildings()
        
        # BaÅŸlangÄ±Ã§ Ã§alÄ±ÅŸanlarÄ±nÄ± iÅŸe al
        self.hire_initial_employees()
        
        # Pazar verilerini baÅŸlat
        self.initialize_market_data()
        
        # Finansal durumu baÅŸlat
        self.initialize_financial_state()
        
        # Stratejik planÄ± oluÅŸtur
        self.create_initial_strategic_plan()
        
    def create_ui(self):
        """UI elementlerini oluÅŸturur"""
        # Ana menÃ¼
        self.main_menu = Entity(
            model='quad',
            texture='white_cube',
            scale=(1, 1),
            position=(0, 0),
            color=color.rgba(0, 0, 0, 0.8)
        )
        
        # Pazar araÅŸtÄ±rmasÄ± paneli
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
        
        # Ãœretim paneli
        self.production_panel = Entity(
            model='quad',
            texture='white_cube',
            scale=(0.3, 0.4),
            position=(0.7, 0.2),
            color=color.rgba(0, 0, 0, 0.7)
        )
        
        # Ä°K paneli
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
        """Her frame'de Ã§alÄ±ÅŸacak gÃ¼ncelleme fonksiyonu"""
        current_time = time.time()
        
        # Oyun hÄ±zÄ± kontrolÃ¼
        if not self.game_state['is_paused']:
            time_delta = (current_time - self.game_state['current_time']) * self.game_state['game_speed']
            self.game_state['current_time'] = current_time
            
            # Sistem gÃ¼ncellemeleri
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
            
            # Otomatik kayÄ±t
            if current_time - self.game_state['last_save_time'] >= self.game_state['save_interval']:
                self.save_game()
                self.game_state['last_save_time'] = current_time
            
            # UI gÃ¼ncelleme
            self.update_ui()
            
            # Bildirim kontrolÃ¼
            self.check_notifications()
            
            # Ã‡oklu oyuncu gÃ¼ncelleme
            if self.multiplayer['is_online']:
                self.update_multiplayer()
                
            # EÄŸitim sistemi gÃ¼ncellemesi
            self.update_training_system()
            
            # Kalite sistemi gÃ¼ncellemesi
            self.update_quality_system()
            
            # SÃ¼rdÃ¼rÃ¼lebilirlik sistemi gÃ¼ncellemesi
            self.update_sustainability_system()
            
            # Kriz yÃ¶netim sistemi gÃ¼ncellemesi
            self.update_crisis_system()
            
            # UluslararasÄ± ticaret sistemi gÃ¼ncellemesi
            self.update_international_trade()
            
            # Dijital dÃ¶nÃ¼ÅŸÃ¼m sistemi gÃ¼ncellemesi
            self.update_digital_transformation()
            
            # Ä°novasyon yÃ¶netim sistemi gÃ¼ncellemesi
            self.update_innovation_system()
            
            # CRM sistemi gÃ¼ncellemesi
            self.update_crm_system()
            
            # Tedarik zinciri yÃ¶netim sistemi gÃ¼ncellemesi
            self.update_scm_system()
            
            # PM sistemi gÃ¼ncellemesi
            self.update_pm_system()
            
            # FR sistemi gÃ¼ncellemesi
            self.update_fr_system()
            
            # SaÄŸlÄ±k sistemi gÃ¼ncellemesi
            self.update_health_system()
            
            # Egzersiz sistemi gÃ¼ncellemesi
            self.update_exercise_system()
            
    def input(self, key):
        """Klavye giriÅŸlerini iÅŸler"""
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
            
        # Ã‡oklu oyuncu kontrolleri
        if key == 't':
            self.initiate_trade()
        elif key == 'a':
            self.propose_alliance()
            
        # EÄŸitim sistemi kontrolleri
        if key == 'e':
            self.show_training_panel()
            
        # Kalite yÃ¶netimi kontrolleri
        if key == 'q':
            self.show_quality_panel()
            
        # SÃ¼rdÃ¼rÃ¼lebilirlik kontrolleri
        if key == 's':
            self.show_sustainability_panel()
            
        # Kriz yÃ¶netimi kontrolleri
        if key == 'k':
            self.show_crisis_panel()
            
        # UluslararasÄ± ticaret kontrolleri
        if key == 'u':
            self.show_international_trade_panel()
            
        # Dijital dÃ¶nÃ¼ÅŸÃ¼m kontrolleri
        if key == 'd':
            self.show_digital_panel()
            
        # Ä°novasyon yÃ¶netimi kontrolleri
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
            
        # SaÄŸlÄ±k kontrolleri
        if key == 'h':
            self.show_health_panel()
            
        # Egzersiz kontrolleri
        if key == 'e':
            self.show_exercise_panel()
            
    def toggle_pause(self):
        """Oyunu duraklatÄ±r/devam ettirir"""
        self.game_state['is_paused'] = not self.game_state['is_paused']
        self.show_notification("Oyun " + ("duraklatÄ±ldÄ±" if self.game_state['is_paused'] else "devam ediyor"))
        
    def toggle_game_speed(self):
        """Oyun hÄ±zÄ±nÄ± deÄŸiÅŸtirir"""
        speeds = [0.5, 1.0, 2.0, 4.0]
        current_index = speeds.index(self.game_state['game_speed'])
        next_index = (current_index + 1) % len(speeds)
        self.game_state['game_speed'] = speeds[next_index]
        self.show_notification(f"Oyun hÄ±zÄ±: {self.game_state['game_speed']}x")
        
    def show_notification(self, message, duration=3):
        """Bildirim gÃ¶sterir"""
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
            self.show_notification(f"KayÄ±t hatasÄ±: {str(e)}", color.red)
            
    def load_game(self):
        """KaydedilmiÅŸ oyunu yÃ¼kler"""
        try:
            with open(f'save_{self.player_id}.json', 'r') as f:
                save_data = json.load(f)
                
            # Verileri yÃ¼kle
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
            
            self.show_notification("Oyun yÃ¼klendi")
        except Exception as e:
            self.show_notification(f"YÃ¼kleme hatasÄ±: {str(e)}", color.red)
            
    def update_training_system(self):
        """EÄŸitim sistemini gÃ¼nceller"""
        current_time = time.time()
        if current_time - self.training_system['last_training_update'] >= self.training_system['training_interval']:
            # EÄŸitimleri kontrol et
            self.check_training_completion()
            
            # Yeni eÄŸitim fÄ±rsatlarÄ± oluÅŸtur
            self.generate_training_opportunities()
            
            # EÄŸitim bÃ¼tÃ§esini gÃ¼ncelle
            self.update_training_budget()
            
            self.training_system['last_training_update'] = current_time
            
    def check_training_completion(self):
        """Tamamlanan eÄŸitimleri kontrol eder"""
        for training in self.training_system['employee_trainings'][:]:
            if current_time - training['start_time'] >= training['duration'] * 3600:
                # EÄŸitimi tamamla
                self.complete_training(training)
                self.training_system['employee_trainings'].remove(training)
                
    def complete_training(self, training):
        """EÄŸitimi tamamlar ve Ã¶dÃ¼lleri verir"""
        employee = training['employee']
        course = training['course']
        
        # Beceri artÄ±ÅŸÄ±
        skill_increase = random.uniform(0.1, 0.3)
        employee['skills'][course['skill']] = min(10, employee['skills'][course['skill']] + skill_increase)
        
        # Sertifika kontrolÃ¼
        if course['level'] == 'advanced' and random.random() < 0.7:
            self.training_system['certifications'].append({
                'employee': employee['id'],
                'course': course['name'],
                'date': time.time()
            })
            
        # Bildirim gÃ¶ster
        self.show_notification(f"{employee['name']} {course['name']} eÄŸitimini tamamladÄ±!")
        
    def generate_training_opportunities(self):
        """Yeni eÄŸitim fÄ±rsatlarÄ± oluÅŸturur"""
        # Ã‡alÄ±ÅŸanlar iÃ§in eÄŸitim fÄ±rsatlarÄ±
        for employee in self.hr_system['personnel']['employees']:
            if random.random() < 0.3:  # %30 ÅŸans
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
        """Ã‡alÄ±ÅŸan iÃ§in uygun kurslarÄ± dÃ¶ndÃ¼rÃ¼r"""
        available = []
        for level, courses in self.training_system['available_courses'].items():
            for course in courses:
                if employee['skills'][course['skill']] < 8:  # Beceri 8'den dÃ¼ÅŸÃ¼kse
                    available.append(course)
        return available
        
    def update_training_budget(self):
        """EÄŸitim bÃ¼tÃ§esini gÃ¼nceller"""
        # BÃ¼tÃ§enin %5'i eÄŸitim iÃ§in ayrÄ±lÄ±r
        self.training_system['training_budget'] = self.player_data['balance'] * 0.05
        
    def show_training_panel(self):
        """EÄŸitim panelini gÃ¶sterir"""
        self.training_panel.visible = True
        
        # Panel baÅŸlÄ±ÄŸÄ±
        Text(
            parent=self.training_panel,
            text='EÄŸitim Sistemi',
            position=(0, 0.15),
            scale=2,
            color=color.white
        )
        
        # EÄŸitim bÃ¼tÃ§esi
        Text(
            parent=self.training_panel,
            text=f"EÄŸitim BÃ¼tÃ§esi: ${self.training_system['training_budget']:,.2f}",
            position=(0, 0.05),
            scale=1.2,
            color=color.green
        )
        
        # Devam eden eÄŸitimler
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
        """Kalite sistemini gÃ¼nceller"""
        current_time = time.time()
        
        # Denetim kontrolÃ¼
        if current_time - self.quality_system['quality_control']['last_audit'] >= self.quality_system['quality_control']['audit_interval']:
            self.perform_quality_audit()
            self.quality_system['quality_control']['last_audit'] = current_time
            
        # MÃ¼ÅŸteri memnuniyeti anketi
        if current_time - self.quality_system['customer_satisfaction']['last_survey'] >= self.quality_system['customer_satisfaction']['survey_interval']:
            self.perform_customer_survey()
            self.quality_system['customer_satisfaction']['last_survey'] = current_time
            
        # SÃ¼rekli iyileÅŸtirme gÃ¶zden geÃ§irmesi
        if current_time - self.quality_system['continuous_improvement']['last_review'] >= self.quality_system['continuous_improvement']['review_interval']:
            self.review_improvement_projects()
            self.quality_system['continuous_improvement']['last_review'] = current_time
            
    def perform_quality_audit(self):
        """Kalite denetimi yapar"""
        # Hata oranÄ±nÄ± kontrol et
        defect_rate = self.quality_system['quality_control']['defect_rate']
        
        # ISO standartlarÄ±na uygunluk kontrolÃ¼
        for standard in self.quality_system['iso_standards']:
            if not self.quality_system['iso_standards'][standard]:
                if random.random() < 0.3:  # %30 ÅŸans
                    self.quality_system['iso_standards'][standard] = True
                    self.show_notification(f"{standard} sertifikasÄ± alÄ±ndÄ±!")
                    
        # Kalite metriklerini gÃ¼ncelle
        self.update_quality_metrics()
        
    def perform_customer_survey(self):
        """MÃ¼ÅŸteri memnuniyeti anketi yapar"""
        # Yeni geri bildirimler topla
        new_feedback = {
            'product_quality': random.uniform(0.7, 1.0),
            'service_quality': random.uniform(0.7, 1.0),
            'delivery_time': random.uniform(0.7, 1.0),
            'price_value': random.uniform(0.7, 1.0)
        }
        
        self.quality_system['customer_satisfaction']['feedback'].append(new_feedback)
        
        # Memnuniyet skorunu gÃ¼ncelle
        total_score = sum(f['product_quality'] + f['service_quality'] + f['delivery_time'] + f['price_value'] 
                         for f in self.quality_system['customer_satisfaction']['feedback'])
        feedback_count = len(self.quality_system['customer_satisfaction']['feedback'])
        self.quality_system['customer_satisfaction']['score'] = total_score / (feedback_count * 4)
        
    def review_improvement_projects(self):
        """Ä°yileÅŸtirme projelerini gÃ¶zden geÃ§irir"""
        # Tamamlanan projeleri kontrol et
        for project in self.quality_system['continuous_improvement']['projects'][:]:
            if project['status'] == 'in_progress' and random.random() < 0.2:  # %20 ÅŸans
                project['status'] = 'completed'
                self.apply_improvement_results(project)
                
        # Yeni projeler oluÅŸtur
        if random.random() < 0.3:  # %30 ÅŸans
            self.create_new_improvement_project()
            
    def apply_improvement_results(self, project):
        """Ä°yileÅŸtirme sonuÃ§larÄ±nÄ± uygular"""
        if project['type'] == 'process':
            # SÃ¼reÃ§ verimliliÄŸini artÄ±r
            self.production_system['efficiency'] *= 1.1
        elif project['type'] == 'quality':
            # Hata oranÄ±nÄ± dÃ¼ÅŸÃ¼r
            self.quality_system['quality_control']['defect_rate'] *= 0.9
        elif project['type'] == 'customer':
            # MÃ¼ÅŸteri memnuniyetini artÄ±r
            self.quality_system['customer_satisfaction']['score'] = min(1.0, 
                self.quality_system['customer_satisfaction']['score'] * 1.05)
                
        self.show_notification(f"{project['name']} iyileÅŸtirme projesi tamamlandÄ±!")
        
    def create_new_improvement_project(self):
        """Yeni iyileÅŸtirme projesi oluÅŸturur"""
        project_types = ['process', 'quality', 'customer']
        project_type = random.choice(project_types)
        
        new_project = {
            'name': f"{project_type.capitalize()} Ä°yileÅŸtirme Projesi",
            'type': project_type,
            'status': 'in_progress',
            'start_time': time.time(),
            'duration': random.randint(3600, 7200)  # 1-2 saat
        }
        
        self.quality_system['continuous_improvement']['projects'].append(new_project)
        
    def show_quality_panel(self):
        """Kalite panelini gÃ¶sterir"""
        self.quality_panel.visible = True
        
        # Panel baÅŸlÄ±ÄŸÄ±
        Text(
            parent=self.quality_panel,
            text='Kalite YÃ¶netimi',
            position=(0, 0.15),
            scale=2,
            color=color.white
        )
        
        # ISO standartlarÄ±
        y_pos = 0.05
        for standard, certified in self.quality_system['iso_standards'].items():
            Text(
                parent=self.quality_panel,
                text=f"{standard}: {'âœ“' if certified else 'âœ—'}",
                position=(0, y_pos),
                scale=1.2,
                color=color.green if certified else color.red
            )
            y_pos -= 0.05
            
        # MÃ¼ÅŸteri memnuniyeti
        Text(
            parent=self.quality_panel,
            text=f"MÃ¼ÅŸteri Memnuniyeti: %{self.quality_system['customer_satisfaction']['score']*100:.0f}",
            position=(0, y_pos),
            scale=1.2,
            color=color.yellow
        )
        y_pos -= 0.05
        
        # Hata oranÄ±
        Text(
            parent=self.quality_panel,
            text=f"Hata OranÄ±: %{self.quality_system['quality_control']['defect_rate']*100:.1f}",
            position=(0, y_pos),
            scale=1.2,
            color=color.red
        )
        
    def update_sustainability_system(self):
        """SÃ¼rdÃ¼rÃ¼lebilirlik sistemini gÃ¼nceller"""
        current_time = time.time()
        
        # Ã‡evresel etki Ã¶lÃ§Ã¼mÃ¼
        if current_time - self.sustainability_system['environmental_impact']['last_measurement'] >= self.sustainability_system['environmental_impact']['measurement_interval']:
            self.measure_environmental_impact()
            self.sustainability_system['environmental_impact']['last_measurement'] = current_time
            
        # Sosyal sorumluluk deÄŸerlendirmesi
        if current_time - self.sustainability_system['social_responsibility']['last_assessment'] >= self.sustainability_system['social_responsibility']['assessment_interval']:
            self.assess_social_responsibility()
            self.sustainability_system['social_responsibility']['last_assessment'] = current_time
            
        # Enerji verimliliÄŸi denetimi
        if current_time - self.sustainability_system['energy_efficiency']['last_audit'] >= self.sustainability_system['energy_efficiency']['audit_interval']:
            self.audit_energy_efficiency()
            self.sustainability_system['energy_efficiency']['last_audit'] = current_time
            
        # AtÄ±k yÃ¶netimi gÃ¶zden geÃ§irmesi
        if current_time - self.sustainability_system['waste_management']['last_review'] >= self.sustainability_system['waste_management']['review_interval']:
            self.review_waste_management()
            self.sustainability_system['waste_management']['last_review'] = current_time
            
    def measure_environmental_impact(self):
        """Ã‡evresel etkiyi Ã¶lÃ§er"""
        # Karbon ayak izi
        self.sustainability_system['environmental_impact']['carbon_footprint'] *= random.uniform(0.95, 1.05)
        
        # Enerji tÃ¼ketimi
        self.sustainability_system['environmental_impact']['energy_consumption'] *= random.uniform(0.95, 1.05)
        
        # Su kullanÄ±mÄ±
        self.sustainability_system['environmental_impact']['water_usage'] *= random.uniform(0.95, 1.05)
        
        # AtÄ±k Ã¼retimi
        self.sustainability_system['environmental_impact']['waste_generated'] *= random.uniform(0.95, 1.05)
        
    def assess_social_responsibility(self):
        """Sosyal sorumluluÄŸu deÄŸerlendirir"""
        # Topluluk projeleri
        if random.random() < 0.2:  # %20 ÅŸans
            new_project = {
                'name': f"Topluluk Projesi {len(self.sustainability_system['social_responsibility']['community_projects']) + 1}",
                'impact': random.uniform(0.1, 0.3),
                'completion_time': random.randint(3600, 7200)  # 1-2 saat
            }
            self.sustainability_system['social_responsibility']['community_projects'].append(new_project)
            
        # Ã‡alÄ±ÅŸan refahÄ±
        self.sustainability_system['social_responsibility']['employee_wellbeing'] = min(1.0,
            self.sustainability_system['social_responsibility']['employee_wellbeing'] * random.uniform(1.0, 1.05))
            
        # Ã‡eÅŸitlilik skoru
        self.sustainability_system['social_responsibility']['diversity_score'] = min(1.0,
            self.sustainability_system['social_responsibility']['diversity_score'] * random.uniform(1.0, 1.05))
            
    def audit_energy_efficiency(self):
        """Enerji verimliliÄŸini denetler"""
        # Yenilenebilir enerji oranÄ±
        if random.random() < 0.3:  # %30 ÅŸans
            self.sustainability_system['energy_efficiency']['renewable_energy_ratio'] = min(1.0,
                self.sustainability_system['energy_efficiency']['renewable_energy_ratio'] * 1.1)
                
        # Enerji tasarrufu
        self.sustainability_system['energy_efficiency']['energy_savings'] += random.uniform(0.1, 0.5)
        
        # Verimlilik projeleri
        if random.random() < 0.2:  # %20 ÅŸans
            new_project = {
                'name': f"Enerji VerimliliÄŸi Projesi {len(self.sustainability_system['energy_efficiency']['efficiency_projects']) + 1}",
                'savings': random.uniform(0.1, 0.3),
                'completion_time': random.randint(3600, 7200)  # 1-2 saat
            }
            self.sustainability_system['energy_efficiency']['efficiency_projects'].append(new_project)
            
    def review_waste_management(self):
        """AtÄ±k yÃ¶netimini gÃ¶zden geÃ§irir"""
        # Geri dÃ¶nÃ¼ÅŸÃ¼m oranÄ±
        if random.random() < 0.3:  # %30 ÅŸans
            self.sustainability_system['waste_management']['recycling_rate'] = min(1.0,
                self.sustainability_system['waste_management']['recycling_rate'] * 1.1)
                
        # AtÄ±k azaltma
        self.sustainability_system['waste_management']['waste_reduction'] += random.uniform(0.1, 0.5)
        
        # AtÄ±k projeleri
        if random.random() < 0.2:  # %20 ÅŸans
            new_project = {
                'name': f"AtÄ±k YÃ¶netimi Projesi {len(self.sustainability_system['waste_management']['waste_projects']) + 1}",
                'reduction': random.uniform(0.1, 0.3),
                'completion_time': random.randint(3600, 7200)  # 1-2 saat
            }
            self.sustainability_system['waste_management']['waste_projects'].append(new_project)
            
    def show_sustainability_panel(self):
        """SÃ¼rdÃ¼rÃ¼lebilirlik panelini gÃ¶sterir"""
        self.sustainability_panel.visible = True
        
        # Panel baÅŸlÄ±ÄŸÄ±
        Text(
            parent=self.sustainability_panel,
            text='SÃ¼rdÃ¼rÃ¼lebilirlik',
            position=(0, 0.15),
            scale=2,
            color=color.white
        )
        
        # Ã‡evresel etki
        y_pos = 0.05
        Text(
            parent=self.sustainability_panel,
            text=f"Karbon Ayak Ä°zi: {self.sustainability_system['environmental_impact']['carbon_footprint']:.0f} kg CO2",
            position=(0, y_pos),
            scale=1.2,
            color=color.red
        )
        y_pos -= 0.05
        
        Text(
            parent=self.sustainability_panel,
            text=f"Enerji TÃ¼ketimi: {self.sustainability_system['environmental_impact']['energy_consumption']:.0f} kWh",
            position=(0, y_pos),
            scale=1.2,
            color=color.yellow
        )
        y_pos -= 0.05
        
        # Sosyal sorumluluk
        Text(
            parent=self.sustainability_panel,
            text=f"Ã‡alÄ±ÅŸan RefahÄ±: %{self.sustainability_system['social_responsibility']['employee_wellbeing']*100:.0f}",
            position=(0, y_pos),
            scale=1.2,
            color=color.green
        )
        y_pos -= 0.05
        
        # Enerji verimliliÄŸi
        Text(
            parent=self.sustainability_panel,
            text=f"Yenilenebilir Enerji: %{self.sustainability_system['energy_efficiency']['renewable_energy_ratio']*100:.0f}",
            position=(0, y_pos),
            scale=1.2,
            color=color.blue
        )
        y_pos -= 0.05
        
        # AtÄ±k yÃ¶netimi
        Text(
            parent=self.sustainability_panel,
            text=f"Geri DÃ¶nÃ¼ÅŸÃ¼m OranÄ±: %{self.sustainability_system['waste_management']['recycling_rate']*100:.0f}",
            position=(0, y_pos),
            scale=1.2,
            color=color.orange
        )
        
    def update_crisis_system(self):
        """Kriz yÃ¶netim sistemini gÃ¼nceller"""
        current_time = time.time()
        
        # Risk deÄŸerlendirmesi
        if current_time - self.crisis_system['risk_assessment']['last_assessment'] >= self.crisis_system['risk_assessment']['assessment_interval']:
            self.assess_risks()
            self.crisis_system['risk_assessment']['last_assessment'] = current_time
            
        # Acil durum planlarÄ± gÃ¼ncellemesi
        for plan_type in self.crisis_system['emergency_plans']:
            if current_time - self.crisis_system['emergency_plans'][plan_type]['last_update'] >= self.crisis_system['emergency_plans'][plan_type]['update_interval']:
                self.update_emergency_plan(plan_type)
                self.crisis_system['emergency_plans'][plan_type]['last_update'] = current_time
                
        # Ä°ÅŸ sÃ¼rekliliÄŸi testi
        if current_time - self.crisis_system['business_continuity']['last_test'] >= self.crisis_system['business_continuity']['test_interval']:
            self.test_business_continuity()
            self.crisis_system['business_continuity']['last_test'] = current_time
            
        # Kriz iletiÅŸimi gÃ¶zden geÃ§irmesi
        if current_time - self.crisis_system['crisis_communication']['last_review'] >= self.crisis_system['crisis_communication']['review_interval']:
            self.review_crisis_communication()
            self.crisis_system['crisis_communication']['last_review'] = current_time
            
    def assess_risks(self):
        """Riskleri deÄŸerlendirir"""
        # Finansal riskler
        if random.random() < 0.2:  # %20 ÅŸans
            new_risk = {
                'type': 'financial',
                'severity': random.uniform(0.1, 0.5),
                'probability': random.uniform(0.1, 0.3),
                'mitigation_plan': f"Finansal Risk {len(self.crisis_system['risk_assessment']['financial_risks']) + 1}"
            }
            self.crisis_system['risk_assessment']['financial_risks'].append(new_risk)
            
        # Operasyonel riskler
        if random.random() < 0.2:  # %20 ÅŸans
            new_risk = {
                'type': 'operational',
                'severity': random.uniform(0.1, 0.5),
                'probability': random.uniform(0.1, 0.3),
                'mitigation_plan': f"Operasyonel Risk {len(self.crisis_system['risk_assessment']['operational_risks']) + 1}"
            }
            self.crisis_system['risk_assessment']['operational_risks'].append(new_risk)
            
        # Pazar riskleri
        if random.random() < 0.2:  # %20 ÅŸans
            new_risk = {
                'type': 'market',
                'severity': random.uniform(0.1, 0.5),
                'probability': random.uniform(0.1, 0.3),
                'mitigation_plan': f"Pazar Risk {len(self.crisis_system['risk_assessment']['market_risks']) + 1}"
            }
            self.crisis_system['risk_assessment']['market_risks'].append(new_risk)
            
    def update_emergency_plan(self, plan_type):
        """Acil durum planÄ±nÄ± gÃ¼nceller"""
        if random.random() < 0.3:  # %30 ÅŸans
            self.crisis_system['emergency_plans'][plan_type]['status'] = 'updated'
            self.show_notification(f"{plan_type.replace('_', ' ').title()} acil durum planÄ± gÃ¼ncellendi!")
            
    def test_business_continuity(self):
        """Ä°ÅŸ sÃ¼rekliliÄŸini test eder"""
        # Yedek sistemler
        if random.random() < 0.2:  # %20 ÅŸans
            new_system = {
                'name': f"Yedek Sistem {len(self.crisis_system['business_continuity']['backup_systems']) + 1}",
                'type': random.choice(['financial', 'operational', 'technical']),
                'recovery_time': random.randint(3600, 7200)  # 1-2 saat
            }
            self.crisis_system['business_continuity']['backup_systems'].append(new_system)
            
        # Kurtarma planlarÄ±
        if random.random() < 0.2:  # %20 ÅŸans
            new_plan = {
                'name': f"Kurtarma PlanÄ± {len(self.crisis_system['business_continuity']['recovery_plans']) + 1}",
                'scenario': random.choice(['financial_crisis', 'market_crisis', 'operational_crisis']),
                'recovery_steps': random.randint(3, 7)
            }
            self.crisis_system['business_continuity']['recovery_plans'].append(new_plan)
            
    def review_crisis_communication(self):
        """Kriz iletiÅŸimini gÃ¶zden geÃ§irir"""
        # PaydaÅŸlar
        if random.random() < 0.2:  # %20 ÅŸans
            new_stakeholder = {
                'name': f"PaydaÅŸ {len(self.crisis_system['crisis_communication']['stakeholders']) + 1}",
                'type': random.choice(['investor', 'customer', 'supplier', 'employee']),
                'communication_channel': random.choice(['email', 'phone', 'meeting'])
            }
            self.crisis_system['crisis_communication']['stakeholders'].append(new_stakeholder)
            
        # Ä°letiÅŸim planlarÄ±
        if random.random() < 0.2:  # %20 ÅŸans
            new_plan = {
                'name': f"Ä°letiÅŸim PlanÄ± {len(self.crisis_system['crisis_communication']['communication_plans']) + 1}",
                'crisis_type': random.choice(['financial', 'market', 'operational']),
                'channels': random.randint(2, 4)
            }
            self.crisis_system['crisis_communication']['communication_plans'].append(new_plan)
            
    def show_crisis_panel(self):
        """Kriz yÃ¶netim panelini gÃ¶sterir"""
        self.crisis_panel.visible = True
        
        # Panel baÅŸlÄ±ÄŸÄ±
        Text(
            parent=self.crisis_panel,
            text='Kriz YÃ¶netimi',
            position=(0, 0.15),
            scale=2,
            color=color.white
        )
        
        # Risk deÄŸerlendirmesi
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
        
        # Acil durum planlarÄ±
        Text(
            parent=self.crisis_panel,
            text=f"Finansal Kriz PlanÄ±: {self.crisis_system['emergency_plans']['financial_crisis']['status']}",
            position=(0, y_pos),
            scale=1.2,
            color=color.green
        )
        y_pos -= 0.05
        
        # Ä°ÅŸ sÃ¼rekliliÄŸi
        Text(
            parent=self.crisis_panel,
            text=f"Yedek Sistemler: {len(self.crisis_system['business_continuity']['backup_systems'])}",
            position=(0, y_pos),
            scale=1.2,
            color=color.blue
        )
        y_pos -= 0.05
        
        # Kriz iletiÅŸimi
        Text(
            parent=self.crisis_panel,
            text=f"Ä°letiÅŸim PlanlarÄ±: {len(self.crisis_system['crisis_communication']['communication_plans'])}",
            position=(0, y_pos),
            scale=1.2,
            color=color.orange
        )
        
    def update_international_trade(self):
        """UluslararasÄ± ticaret sistemini gÃ¼nceller"""
        current_time = time.time()
        
        # DÃ¶viz kurlarÄ± gÃ¼ncellemesi
        if current_time - self.international_trade['exchange_rates']['last_update'] >= self.international_trade['exchange_rates']['update_interval']:
            self.update_exchange_rates()
            self.international_trade['exchange_rates']['last_update'] = current_time
            
        # GÃ¼mrÃ¼k sÃ¼reÃ§leri kontrolÃ¼
        if current_time - self.international_trade['customs_processes']['last_check'] >= self.international_trade['customs_processes']['check_interval']:
            self.check_customs_processes()
            self.international_trade['customs_processes']['last_check'] = current_time
            
        # KÃ¼ltÃ¼rel uyum gÃ¶zden geÃ§irmesi
        if current_time - self.international_trade['cultural_adaptation']['last_review'] >= self.international_trade['cultural_adaptation']['review_interval']:
            self.review_cultural_adaptation()
            self.international_trade['cultural_adaptation']['last_review'] = current_time
            
        # Tedarik zinciri denetimi
        if current_time - self.international_trade['supply_chain']['last_audit'] >= self.international_trade['supply_chain']['audit_interval']:
            self.audit_supply_chain()
            self.international_trade['supply_chain']['last_audit'] = current_time
            
    def update_exchange_rates(self):
        """DÃ¶viz kurlarÄ±nÄ± gÃ¼nceller"""
        for currency in self.international_trade['exchange_rates']:
            if currency != 'last_update' and currency != 'update_interval':
                # Kurlarda %1'e kadar dalgalanma
                change = random.uniform(-0.01, 0.01)
                self.international_trade['exchange_rates'][currency] *= (1 + change)
                
    def check_customs_processes(self):
        """GÃ¼mrÃ¼k sÃ¼reÃ§lerini kontrol eder"""
        # GÃ¼mrÃ¼k belgeleri
        if random.random() < 0.2:  # %20 ÅŸans
            new_document = {
                'name': f"GÃ¼mrÃ¼k Belgesi {len(self.international_trade['customs_processes']['documents']) + 1}",
                'type': random.choice(['import', 'export']),
                'validity': random.randint(30, 90)  # 30-90 gÃ¼n
            }
            self.international_trade['customs_processes']['documents'].append(new_document)
            
        # DÃ¼zenlemeler
        if random.random() < 0.2:  # %20 ÅŸans
            new_regulation = {
                'name': f"GÃ¼mrÃ¼k DÃ¼zenlemesi {len(self.international_trade['customs_processes']['regulations']) + 1}",
                'country': random.choice(['ABD', 'AB', 'Ã‡in', 'Japonya', 'Ä°ngiltere']),
                'impact': random.uniform(0.1, 0.3)
            }
            self.international_trade['customs_processes']['regulations'].append(new_regulation)
            
    def review_cultural_adaptation(self):
        """KÃ¼ltÃ¼rel uyumu gÃ¶zden geÃ§irir"""
        # Pazar araÅŸtÄ±rmasÄ±
        if random.random() < 0.2:  # %20 ÅŸans
            new_market = {
                'name': f"Pazar {len(self.international_trade['cultural_adaptation']['markets']) + 1}",
                'country': random.choice(['ABD', 'AB', 'Ã‡in', 'Japonya', 'Ä°ngiltere']),
                'potential': random.uniform(0.5, 1.0)
            }
            self.international_trade['cultural_adaptation']['markets'].append(new_market)
            
        # YerelleÅŸtirme
        if random.random() < 0.2:  # %20 ÅŸans
            new_localization = {
                'name': f"YerelleÅŸtirme {len(self.international_trade['cultural_adaptation']['localization']) + 1}",
                'type': random.choice(['language', 'design', 'marketing']),
                'progress': random.uniform(0.1, 0.5)
            }
            self.international_trade['cultural_adaptation']['localization'].append(new_localization)
            
    def audit_supply_chain(self):
        """Tedarik zincirini denetler"""
        # TedarikÃ§iler
        if random.random() < 0.2:  # %20 ÅŸans
            new_supplier = {
                'name': f"TedarikÃ§i {len(self.international_trade['supply_chain']['suppliers']) + 1}",
                'country': random.choice(['ABD', 'AB', 'Ã‡in', 'Japonya', 'Ä°ngiltere']),
                'reliability': random.uniform(0.7, 1.0)
            }
            self.international_trade['supply_chain']['suppliers'].append(new_supplier)
            
        # Lojistik
        if random.random() < 0.2:  # %20 ÅŸans
            new_logistics = {
                'name': f"Lojistik {len(self.international_trade['supply_chain']['logistics']) + 1}",
                'type': random.choice(['air', 'sea', 'land']),
                'efficiency': random.uniform(0.7, 1.0)
            }
            self.international_trade['supply_chain']['logistics'].append(new_logistics)
            
    def show_international_trade_panel(self):
        """UluslararasÄ± ticaret panelini gÃ¶sterir"""
        self.international_trade_panel.visible = True
        
        # Panel baÅŸlÄ±ÄŸÄ±
        Text(
            parent=self.international_trade_panel,
            text='UluslararasÄ± Ticaret',
            position=(0, 0.15),
            scale=2,
            color=color.white
        )
        
        # DÃ¶viz kurlarÄ±
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
        
        # GÃ¼mrÃ¼k sÃ¼reÃ§leri
        Text(
            parent=self.international_trade_panel,
            text=f"GÃ¼mrÃ¼k Belgeleri: {len(self.international_trade['customs_processes']['documents'])}",
            position=(0, y_pos),
            scale=1.2,
            color=color.yellow
        )
        y_pos -= 0.05
        
        # KÃ¼ltÃ¼rel uyum
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
            text=f"TedarikÃ§iler: {len(self.international_trade['supply_chain']['suppliers'])}",
            position=(0, y_pos),
            scale=1.2,
            color=color.red
        )
        
    def update_digital_transformation(self):
        """Dijital dÃ¶nÃ¼ÅŸÃ¼m sistemini gÃ¼nceller"""
        current_time = time.time()
        
        # Yapay zeka gÃ¼ncellemesi
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
            
        # Siber gÃ¼venlik kontrolÃ¼
        if current_time - self.digital_transformation['cyber_security']['last_check'] >= self.digital_transformation['cyber_security']['check_interval']:
            self.check_security()
            self.digital_transformation['cyber_security']['last_check'] = current_time
            
    def update_ai_systems(self):
        """Yapay zeka sistemlerini gÃ¼nceller"""
        # AI modelleri
        if random.random() < 0.2:  # %20 ÅŸans
            new_model = {
                'name': f"AI Modeli {len(self.digital_transformation['artificial_intelligence']['models']) + 1}",
                'type': random.choice(['classification', 'regression', 'clustering']),
                'accuracy': random.uniform(0.8, 0.95)
            }
            self.digital_transformation['artificial_intelligence']['models'].append(new_model)
            
        # AI uygulamalarÄ±
        if random.random() < 0.2:  # %20 ÅŸans
            new_application = {
                'name': f"AI UygulamasÄ± {len(self.digital_transformation['artificial_intelligence']['applications']) + 1}",
                'department': random.choice(['finans', 'pazarlama', 'Ã¼retim', 'insan_kaynaklari']),
                'efficiency': random.uniform(0.1, 0.3)
            }
            self.digital_transformation['artificial_intelligence']['applications'].append(new_application)
            
    def audit_automation(self):
        """Otomasyon sistemlerini denetler"""
        # Otomatik sÃ¼reÃ§ler
        if random.random() < 0.2:  # %20 ÅŸans
            new_process = {
                'name': f"Otomatik SÃ¼reÃ§ {len(self.digital_transformation['automation']['processes']) + 1}",
                'type': random.choice(['iÅŸ akÄ±ÅŸÄ±', 'raporlama', 'kontrol']),
                'savings': random.uniform(0.1, 0.5)
            }
            self.digital_transformation['automation']['processes'].append(new_process)
            
        # Robotlar
        if random.random() < 0.2:  # %20 ÅŸans
            new_robot = {
                'name': f"Robot {len(self.digital_transformation['automation']['robots']) + 1}",
                'task': random.choice(['veri giriÅŸi', 'kontrol', 'analiz']),
                'reliability': random.uniform(0.9, 1.0)
            }
            self.digital_transformation['automation']['robots'].append(new_robot)
            
    def analyze_data(self):
        """Veri analizi yapar"""
        # GÃ¶sterge panelleri
        if random.random() < 0.2:  # %20 ÅŸans
            new_dashboard = {
                'name': f"GÃ¶sterge Paneli {len(self.digital_transformation['data_analytics']['dashboards']) + 1}",
                'metrics': random.randint(5, 15),
                'update_frequency': random.choice(['gerÃ§ek zamanlÄ±', 'saatlik', 'gÃ¼nlÃ¼k'])
            }
            self.digital_transformation['data_analytics']['dashboards'].append(new_dashboard)
            
        # Raporlar
        if random.random() < 0.2:  # %20 ÅŸans
            new_report = {
                'name': f"Rapor {len(self.digital_transformation['data_analytics']['reports']) + 1}",
                'type': random.choice(['performans', 'trend', 'tahmin']),
                'insight_value': random.uniform(0.1, 0.5)
            }
            self.digital_transformation['data_analytics']['reports'].append(new_report)
            
    def check_security(self):
        """Siber gÃ¼venliÄŸi kontrol eder"""
        # Tehditler
        if random.random() < 0.2:  # %20 ÅŸans
            new_threat = {
                'name': f"Tehdit {len(self.digital_transformation['cyber_security']['threats']) + 1}",
                'type': random.choice(['phishing', 'malware', 'ddos']),
                'severity': random.uniform(0.1, 0.5)
            }
            self.digital_transformation['cyber_security']['threats'].append(new_threat)
            
        # Savunmalar
        if random.random() < 0.2:  # %20 ÅŸans
            new_defense = {
                'name': f"Savunma {len(self.digital_transformation['cyber_security']['defenses']) + 1}",
                'type': random.choice(['firewall', 'antivirus', 'encryption']),
                'effectiveness': random.uniform(0.7, 1.0)
            }
            self.digital_transformation['cyber_security']['defenses'].append(new_defense)
            
    def show_digital_panel(self):
        """Dijital dÃ¶nÃ¼ÅŸÃ¼m panelini gÃ¶sterir"""
        self.digital_panel.visible = True
        
        # Panel baÅŸlÄ±ÄŸÄ±
        Text(
            parent=self.digital_panel,
            text='Dijital DÃ¶nÃ¼ÅŸÃ¼m',
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
            text=f"Otomatik SÃ¼reÃ§ler: {len(self.digital_transformation['automation']['processes'])}",
            position=(0, y_pos),
            scale=1.2,
            color=color.green
        )
        y_pos -= 0.05
        
        # Veri analizi
        Text(
            parent=self.digital_panel,
            text=f"GÃ¶sterge Panelleri: {len(self.digital_transformation['data_analytics']['dashboards'])}",
            position=(0, y_pos),
            scale=1.2,
            color=color.yellow
        )
        y_pos -= 0.05
        
        # Siber gÃ¼venlik
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
        """Ä°novasyon yÃ¶netim sistemini gÃ¼nceller"""
        current_time = time.time()
        
        # Fikir yÃ¶netimi gÃ¶zden geÃ§irmesi
        if current_time - self.innovation_system['idea_management']['last_review'] >= self.innovation_system['idea_management']['review_interval']:
            self.review_ideas()
            self.innovation_system['idea_management']['last_review'] = current_time
            
        # Patent yÃ¶netimi kontrolÃ¼
        if current_time - self.innovation_system['patent_management']['last_check'] >= self.innovation_system['patent_management']['check_interval']:
            self.check_patents()
            self.innovation_system['patent_management']['last_check'] = current_time
            
        # Ar-Ge projeleri gÃ¼ncellemesi
        if current_time - self.innovation_system['rnd_projects']['last_update'] >= self.innovation_system['rnd_projects']['update_interval']:
            self.update_rnd_projects()
            self.innovation_system['rnd_projects']['last_update'] = current_time
            
        # Teknoloji transferi denetimi
        if current_time - self.innovation_system['technology_transfer']['last_audit'] >= self.innovation_system['technology_transfer']['audit_interval']:
            self.audit_technology_transfer()
            self.innovation_system['technology_transfer']['last_audit'] = current_time
            
    def review_ideas(self):
        """Fikirleri gÃ¶zden geÃ§irir"""
        # Yeni fikirler
        if random.random() < 0.2:  # %20 ÅŸans
            new_idea = {
                'name': f"Fikir {len(self.innovation_system['idea_management']['ideas']) + 1}",
                'category': random.choice(['Ã¼rÃ¼n', 'sÃ¼reÃ§', 'hizmet', 'iÅŸ modeli']),
                'potential': random.uniform(0.1, 0.5)
            }
            self.innovation_system['idea_management']['ideas'].append(new_idea)
            
        # Fikir deÄŸerlendirmeleri
        if random.random() < 0.2:  # %20 ÅŸans
            new_evaluation = {
                'idea_id': random.randint(0, len(self.innovation_system['idea_management']['ideas'])),
                'score': random.uniform(0.1, 1.0),
                'feedback': random.choice(['geliÅŸtir', 'reddet', 'beklet'])
            }
            self.innovation_system['idea_management']['evaluations'].append(new_evaluation)
            
    def check_patents(self):
        """Patentleri kontrol eder"""
        # Yeni patentler
        if random.random() < 0.2:  # %20 ÅŸans
            new_patent = {
                'name': f"Patent {len(self.innovation_system['patent_management']['patents']) + 1}",
                'type': random.choice(['icat', 'tasarÄ±m', 'faydalÄ± model']),
                'value': random.uniform(0.1, 0.5)
            }
            self.innovation_system['patent_management']['patents'].append(new_patent)
            
        # Patent baÅŸvurularÄ±
        if random.random() < 0.2:  # %20 ÅŸans
            new_application = {
                'name': f"BaÅŸvuru {len(self.innovation_system['patent_management']['applications']) + 1}",
                'status': random.choice(['beklemede', 'deÄŸerlendirmede', 'onaylandÄ±']),
                'priority': random.uniform(0.1, 1.0)
            }
            self.innovation_system['patent_management']['applications'].append(new_application)
            
    def update_rnd_projects(self):
        """Ar-Ge projelerini gÃ¼nceller"""
        # Aktif projeler
        if random.random() < 0.2:  # %20 ÅŸans
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
        # OrtaklÄ±klar
        if random.random() < 0.2:  # %20 ÅŸans
            new_partnership = {
                'name': f"OrtaklÄ±k {len(self.innovation_system['technology_transfer']['partnerships']) + 1}",
                'type': random.choice(['Ã¼niversite', 'araÅŸtÄ±rma merkezi', 'ÅŸirket']),
                'value': random.uniform(0.1, 0.5)
            }
            self.innovation_system['technology_transfer']['partnerships'].append(new_partnership)
            
        # Lisanslar
        if random.random() < 0.2:  # %20 ÅŸans
            new_license = {
                'name': f"Lisans {len(self.innovation_system['technology_transfer']['licenses']) + 1}",
                'type': random.choice(['in', 'out']),
                'revenue': random.uniform(1000, 10000)
            }
            self.innovation_system['technology_transfer']['licenses'].append(new_license)
            
    def show_innovation_panel(self):
        """Ä°novasyon yÃ¶netim panelini gÃ¶sterir"""
        self.innovation_panel.visible = True
        
        # Panel baÅŸlÄ±ÄŸÄ±
        Text(
            parent=self.innovation_panel,
            text='Ä°novasyon YÃ¶netimi',
            position=(0, 0.15),
            scale=2,
            color=color.white
        )
        
        # Fikir yÃ¶netimi
        y_pos = 0.05
        Text(
            parent=self.innovation_panel,
            text=f"Aktif Fikirler: {len(self.innovation_system['idea_management']['ideas'])}",
            position=(0, y_pos),
            scale=1.2,
            color=color.blue
        )
        y_pos -= 0.05
        
        # Patent yÃ¶netimi
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
            text=f"OrtaklÄ±klar: {len(self.innovation_system['technology_transfer']['partnerships'])}",
            position=(0, y_pos),
            scale=1.2,
            color=color.orange
        )
        y_pos -= 0.05
        
        # Ä°novasyon skoru
        innovation_score = (
            len(self.innovation_system['idea_management']['ideas']) * 0.2 +
            len(self.innovation_system['patent_management']['patents']) * 0.3 +
            len(self.innovation_system['rnd_projects']['active_projects']) * 0.3 +
            len(self.innovation_system['technology_transfer']['partnerships']) * 0.2
        )
        Text(
            parent=self.innovation_panel,
            text=f"Ä°novasyon Skoru: {innovation_score:.1f}",
            position=(0, y_pos),
            scale=1.2,
            color=color.red
        )
        
    def update_crm_system(self):
        """CRM sistemini gÃ¼nceller"""
        current_time = time.time()
        
        # MÃ¼ÅŸteri verileri gÃ¼ncellemesi
        if current_time - self.crm_system['customer_data']['last_update'] >= self.crm_system['customer_data']['update_interval']:
            self.update_customer_data()
            self.crm_system['customer_data']['last_update'] = current_time
            
        # SatÄ±ÅŸ geÃ§miÅŸi kontrolÃ¼
        if current_time - self.crm_system['sales_history']['last_check'] >= self.crm_system['sales_history']['check_interval']:
            self.check_sales_history()
            self.crm_system['sales_history']['last_check'] = current_time
            
        # MÃ¼ÅŸteri memnuniyeti anketi
        if current_time - self.crm_system['customer_satisfaction']['last_survey'] >= self.crm_system['customer_satisfaction']['survey_interval']:
            self.conduct_customer_survey()
            self.crm_system['customer_satisfaction']['last_survey'] = current_time
            
        # Pazarlama kampanyalarÄ± gÃ¶zden geÃ§irmesi
        if current_time - self.crm_system['marketing_campaigns']['last_review'] >= self.crm_system['marketing_campaigns']['review_interval']:
            self.review_marketing_campaigns()
            self.crm_system['marketing_campaigns']['last_review'] = current_time
            
    def update_customer_data(self):
        """MÃ¼ÅŸteri verilerini gÃ¼nceller"""
        # Yeni mÃ¼ÅŸteriler
        if random.random() < 0.2:  # %20 ÅŸans
            new_customer = {
                'id': len(self.crm_system['customer_data']['customers']) + 1,
                'name': f"MÃ¼ÅŸteri {len(self.crm_system['customer_data']['customers']) + 1}",
                'segment': random.choice(['kurumsal', 'bireysel', 'VIP']),
                'value': random.uniform(1000, 10000)
            }
            self.crm_system['customer_data']['customers'].append(new_customer)
            
        # MÃ¼ÅŸteri segmentleri
        if random.random() < 0.2:  # %20 ÅŸans
            new_segment = {
                'name': f"Segment {len(self.crm_system['customer_data']['segments']) + 1}",
                'size': random.randint(10, 100),
                'value': random.uniform(0.1, 0.5)
            }
            self.crm_system['customer_data']['segments'].append(new_segment)
            
    def check_sales_history(self):
        """SatÄ±ÅŸ geÃ§miÅŸini kontrol eder"""
        # Yeni iÅŸlemler
        if random.random() < 0.2:  # %20 ÅŸans
            new_transaction = {
                'customer_id': random.randint(1, len(self.crm_system['customer_data']['customers'])),
                'amount': random.uniform(100, 1000),
                'product': random.choice(['Ã¼rÃ¼n', 'hizmet', 'abonelik']),
                'date': time.time()
            }
        
    def update_scm_system(self):
        """Tedarik zinciri yÃ¶netim sistemini gÃ¼nceller"""
        current_time = time.time()
        
        # TedarikÃ§i kontrolÃ¼
        if current_time - self.scm_system['suppliers']['last_check'] >= self.scm_system['suppliers']['check_interval']:
            self.check_suppliers()
            self.scm_system['suppliers']['last_check'] = current_time
            
        # Envanter denetimi
        if current_time - self.scm_system['inventory']['last_audit'] >= self.scm_system['inventory']['audit_interval']:
            self.audit_inventory()
            self.scm_system['inventory']['last_audit'] = current_time
            
        # Lojistik gÃ¼ncellemesi
        if current_time - self.scm_system['logistics']['last_update'] >= self.scm_system['logistics']['update_interval']:
            self.update_logistics()
            self.scm_system['logistics']['last_update'] = current_time
            
        # Risk deÄŸerlendirmesi
        if current_time - self.scm_system['risk_management']['last_assessment'] >= self.scm_system['risk_management']['assessment_interval']:
            self.assess_risks()
            self.scm_system['risk_management']['last_assessment'] = current_time
            
    def check_suppliers(self):
        """TedarikÃ§ileri kontrol eder"""
        # Yeni tedarikÃ§iler
        if random.random() < 0.2:  # %20 ÅŸans
            new_supplier = {
                'id': len(self.scm_system['suppliers']['active_suppliers']) + 1,
                'name': f"TedarikÃ§i {len(self.scm_system['suppliers']['active_suppliers']) + 1}",
                'category': random.choice(['hammadde', 'yarÄ± mamul', 'tam mamul']),
                'reliability': random.uniform(0.1, 1.0)
            }
            self.scm_system['suppliers']['active_suppliers'].append(new_supplier)
            
        # TedarikÃ§i deÄŸerlendirmeleri
        if random.random() < 0.2:  # %20 ÅŸans
            new_evaluation = {
                'supplier_id': random.randint(1, len(self.scm_system['suppliers']['active_suppliers'])),
                'score': random.uniform(0.1, 1.0),
                'criteria': random.choice(['kalite', 'teslimat', 'fiyat', 'hizmet'])
            }
            self.scm_system['suppliers']['evaluations'].append(new_evaluation)
            
    def audit_inventory(self):
        """Envanteri denetler"""
        # Stok seviyeleri
        if random.random() < 0.2:  # %20 ÅŸans
            new_stock = {
                'product_id': len(self.scm_system['inventory']['stock_levels']) + 1,
                'quantity': random.randint(100, 1000),
                'location': random.choice(['depo1', 'depo2', 'depo3']),
                'value': random.uniform(1000, 10000)
            }
            self.scm_system['inventory']['stock_levels'].append(new_stock)
            
        # SipariÅŸler
        if random.random() < 0.2:  # %20 ÅŸans
            new_order = {
                'order_id': len(self.scm_system['inventory']['orders']) + 1,
                'supplier_id': random.randint(1, len(self.scm_system['suppliers']['active_suppliers'])),
                'quantity': random.randint(10, 100),
                'status': random.choice(['beklemede', 'yolda', 'teslim edildi'])
            }
            self.scm_system['inventory']['orders'].append(new_order)
            
    def update_logistics(self):
        """Lojistik durumunu gÃ¼nceller"""
        # Sevkiyatlar
        if random.random() < 0.2:  # %20 ÅŸans
            new_shipment = {
                'shipment_id': len(self.scm_system['logistics']['shipments']) + 1,
                'from_location': random.choice(['depo1', 'depo2', 'depo3']),
                'to_location': random.choice(['mÃ¼ÅŸteri1', 'mÃ¼ÅŸteri2', 'mÃ¼ÅŸteri3']),
                'status': random.choice(['yÃ¼klendi', 'yolda', 'teslim edildi'])
            }
            self.scm_system['logistics']['shipments'].append(new_shipment)
            
        # Rotalar
        if random.random() < 0.2:  # %20 ÅŸans
            new_route = {
                'route_id': len(self.scm_system['logistics']['routes']) + 1,
                'distance': random.uniform(10, 100),
                'duration': random.uniform(1, 5),
                'cost': random.uniform(100, 1000)
            }
            self.scm_system['logistics']['routes'].append(new_route)
            
    def assess_risks(self):
        """Riskleri deÄŸerlendirir"""
        # Riskler
        if random.random() < 0.2:  # %20 ÅŸans
            new_risk = {
                'risk_id': len(self.scm_system['risk_management']['risks']) + 1,
                'type': random.choice(['tedarik', 'lojistik', 'envanter', 'maliyet']),
                'probability': random.uniform(0.1, 0.5),
                'impact': random.uniform(0.1, 0.5)
            }
            self.scm_system['risk_management']['risks'].append(new_risk)
            
        # Risk azaltma Ã¶nlemleri
        if random.random() < 0.2:  # %20 ÅŸans
            new_mitigation = {
                'risk_id': random.randint(1, len(self.scm_system['risk_management']['risks'])),
                'action': random.choice(['yedek tedarikÃ§i', 'stok artÄ±rÄ±mÄ±', 'alternatif rota']),
                'effectiveness': random.uniform(0.1, 1.0)
            }
            self.scm_system['risk_management']['mitigations'].append(new_mitigation)
            
    def show_scm_panel(self):
        """SCM panelini gÃ¶sterir"""
        self.scm_panel.visible = True
        
        # Panel baÅŸlÄ±ÄŸÄ±
        Text(
            parent=self.scm_panel,
            text='Tedarik Zinciri',
            position=(0, 0.15),
            scale=2,
            color=color.white
        )
        
        # TedarikÃ§iler
        y_pos = 0.05
        Text(
            parent=self.scm_panel,
            text=f"Aktif TedarikÃ§iler: {len(self.scm_system['suppliers']['active_suppliers'])}",
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
        
        # Risk yÃ¶netimi
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
        """Klavye giriÅŸlerini iÅŸler"""
        # ... existing code ...
        
        # SCM kontrolleri
        if key == 't':
            self.show_scm_panel()
            
    def update(self):
        """Her frame'de Ã§alÄ±ÅŸacak gÃ¼ncelleme fonksiyonu"""
        # ... existing code ...
        
        # SCM sistemi gÃ¼ncellemesi
        self.update_scm_system()
        
        # PM sistemi gÃ¼ncellemesi
        self.update_pm_system()

    def update_pm_system(self):
        """Proje yÃ¶netim sistemini gÃ¼nceller"""
        current_time = time.time()
        
        # Proje gÃ¶zden geÃ§irmesi
        if current_time - self.pm_system['projects']['last_review'] >= self.pm_system['projects']['review_interval']:
            self.review_projects()
            self.pm_system['projects']['last_review'] = current_time
            
        # Kaynak kontrolÃ¼
        if current_time - self.pm_system['resources']['last_check'] >= self.pm_system['resources']['check_interval']:
            self.check_resources()
            self.pm_system['resources']['last_check'] = current_time
            
        # Zamanlama gÃ¼ncellemesi
        if current_time - self.pm_system['scheduling']['last_update'] >= self.pm_system['scheduling']['update_interval']:
            self.update_schedule()
            self.pm_system['scheduling']['last_update'] = current_time
            
        # Performans deÄŸerlendirmesi
        if current_time - self.pm_system['performance']['last_assessment'] >= self.pm_system['performance']['assessment_interval']:
            self.assess_performance()
            self.pm_system['performance']['last_assessment'] = current_time
            
    def review_projects(self):
        """Projeleri gÃ¶zden geÃ§irir"""
        # Yeni projeler
        if random.random() < 0.2:  # %20 ÅŸans
            new_project = {
                'id': len(self.pm_system['projects']['active_projects']) + 1,
                'name': f"Proje {len(self.pm_system['projects']['active_projects']) + 1}",
                'type': random.choice(['Ã¼rÃ¼n', 'hizmet', 'altyapÄ±', 'araÅŸtÄ±rma']),
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
        """KaynaklarÄ± kontrol eder"""
        # Ekipler
        if random.random() < 0.2:  # %20 ÅŸans
            new_team = {
                'id': len(self.pm_system['resources']['teams']) + 1,
                'name': f"Ekip {len(self.pm_system['resources']['teams']) + 1}",
                'size': random.randint(3, 10),
                'skills': random.sample(['planlama', 'geliÅŸtirme', 'test', 'dokÃ¼mantasyon'], 2)
            }
            self.pm_system['resources']['teams'].append(new_team)
            
        # Ekipman
        if random.random() < 0.2:  # %20 ÅŸans
            new_equipment = {
                'id': len(self.pm_system['resources']['equipment']) + 1,
                'name': f"Ekipman {len(self.pm_system['resources']['equipment']) + 1}",
                'type': random.choice(['yazÄ±lÄ±m', 'donanÄ±m', 'laboratuvar', 'ofis']),
                'status': random.choice(['kullanÄ±mda', 'bakÄ±mda', 'yedek'])
            }
            self.pm_system['resources']['equipment'].append(new_equipment)
            
    def update_schedule(self):
        """ZamanlamayÄ± gÃ¼nceller"""
        # GÃ¶revler
        if random.random() < 0.2:  # %20 ÅŸans
            new_task = {
                'id': len(self.pm_system['scheduling']['tasks']) + 1,
                'project_id': random.randint(1, len(self.pm_system['projects']['active_projects'])),
                'name': f"GÃ¶rev {len(self.pm_system['scheduling']['tasks']) + 1}",
                'duration': random.uniform(1, 5),
                'status': random.choice(['beklemede', 'devam ediyor', 'tamamlandÄ±'])
            }
            self.pm_system['scheduling']['tasks'].append(new_task)
            
        # Kilometre taÅŸlarÄ±
        if random.random() < 0.2:  # %20 ÅŸans
            new_milestone = {
                'id': len(self.pm_system['scheduling']['milestones']) + 1,
                'project_id': random.randint(1, len(self.pm_system['projects']['active_projects'])),
                'name': f"Kilometre TaÅŸÄ± {len(self.pm_system['scheduling']['milestones']) + 1}",
                'date': time.time() + random.uniform(86400, 604800),  # 1-7 gÃ¼n
                'status': random.choice(['gelecek', 'yaklaÅŸÄ±yor', 'tamamlandÄ±'])
            }
            self.pm_system['scheduling']['milestones'].append(new_milestone)
            
    def assess_performance(self):
        """PerformansÄ± deÄŸerlendirir"""
        # Metrikler
        if random.random() < 0.2:  # %20 ÅŸans
            new_metric = {
                'id': len(self.pm_system['performance']['metrics']) + 1,
                'project_id': random.randint(1, len(self.pm_system['projects']['active_projects'])),
                'type': random.choice(['zaman', 'maliyet', 'kalite', 'kapsam']),
                'value': random.uniform(0.1, 1.0)
            }
            self.pm_system['performance']['metrics'].append(new_metric)
            
        # Raporlar
        if random.random() < 0.2:  # %20 ÅŸans
            new_report = {
                'id': len(self.pm_system['performance']['reports']) + 1,
                'project_id': random.randint(1, len(self.pm_system['projects']['active_projects'])),
                'period': random.choice(['gÃ¼nlÃ¼k', 'haftalÄ±k', 'aylÄ±k']),
                'status': random.choice(['iyi', 'orta', 'kÃ¶tÃ¼'])
            }
            self.pm_system['performance']['reports'].append(new_report)
            
    def show_pm_panel(self):
        """PM panelini gÃ¶sterir"""
        self.pm_panel.visible = True
        
        # Panel baÅŸlÄ±ÄŸÄ±
        Text(
            parent=self.pm_panel,
            text='Proje YÃ¶netimi',
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
            text=f"Aktif GÃ¶revler: {len(self.pm_system['scheduling']['tasks'])}",
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
            sum(1 for t in self.pm_system['scheduling']['tasks'] if t['status'] == 'tamamlandÄ±') / max(1, len(self.pm_system['scheduling']['tasks'])) * 0.2 +
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
        """Klavye giriÅŸlerini iÅŸler"""
        # ... existing code ...
        
        # PM kontrolleri
        if key == 'p':
            self.show_pm_panel()
            
    def update(self):
        """Her frame'de Ã§alÄ±ÅŸacak gÃ¼ncelleme fonksiyonu"""
        # ... existing code ...
        
        # PM sistemi gÃ¼ncellemesi
        self.update_pm_system()

    def update_hr_system(self):
        """Ä°nsan kaynaklarÄ± sistemini gÃ¼nceller"""
        current_time = time.time()
        
        # Personel gÃ¼ncellemesi
        if current_time - self.hr_system['personnel']['last_update'] >= self.hr_system['personnel']['update_interval']:
            self.update_personnel()
            self.hr_system['personnel']['last_update'] = current_time
            
        # EÄŸitim gÃ¶zden geÃ§irmesi
        if current_time - self.hr_system['training']['last_review'] >= self.hr_system['training']['review_interval']:
            self.review_training()
            self.hr_system['training']['last_review'] = current_time
            
        # Performans deÄŸerlendirmesi
        if current_time - self.hr_system['performance']['last_assessment'] >= self.hr_system['performance']['assessment_interval']:
            self.assess_performance()
            self.hr_system['performance']['last_assessment'] = current_time
            
        # Kariyer kontrolÃ¼
        if current_time - self.hr_system['career']['last_check'] >= self.hr_system['career']['check_interval']:
            self.check_career()
            self.hr_system['career']['last_check'] = current_time
            
    def update_personnel(self):
        """Personel verilerini gÃ¼nceller"""
        # Yeni Ã§alÄ±ÅŸanlar
        if random.random() < 0.2:  # %20 ÅŸans
            new_employee = {
                'id': len(self.hr_system['personnel']['employees']) + 1,
                'name': f"Ã‡alÄ±ÅŸan {len(self.hr_system['personnel']['employees']) + 1}",
                'department': random.choice(['Ã¼retim', 'pazarlama', 'satÄ±ÅŸ', 'ar-ge']),
                'position': random.choice(['uzman', 'yÃ¶netici', 'mÃ¼dÃ¼r', 'direktÃ¶r']),
                'salary': random.uniform(5000, 20000)
            }
            self.hr_system['personnel']['employees'].append(new_employee)
            
        # Departmanlar
        if random.random() < 0.2:  # %20 ÅŸans
            new_department = {
                'id': len(self.hr_system['personnel']['departments']) + 1,
                'name': f"Departman {len(self.hr_system['personnel']['departments']) + 1}",
                'size': random.randint(5, 20),
                'budget': random.uniform(100000, 500000)
            }
            self.hr_system['personnel']['departments'].append(new_department)
            
    def review_training(self):
        """EÄŸitim programlarÄ±nÄ± gÃ¶zden geÃ§irir"""
        # EÄŸitim programlarÄ±
        if random.random() < 0.2:  # %20 ÅŸans
            new_program = {
                'id': len(self.hr_system['training']['programs']) + 1,
                'name': f"EÄŸitim {len(self.hr_system['training']['programs']) + 1}",
                'type': random.choice(['teknik', 'yÃ¶netim', 'kiÅŸisel geliÅŸim']),
                'duration': random.uniform(1, 5),
                'cost': random.uniform(1000, 5000)
            }
            self.hr_system['training']['programs'].append(new_program)
            
        # Sertifikalar
        if random.random() < 0.2:  # %20 ÅŸans
            new_certification = {
                'id': len(self.hr_system['training']['certifications']) + 1,
                'employee_id': random.randint(1, len(self.hr_system['personnel']['employees'])),
                'name': f"Sertifika {len(self.hr_system['training']['certifications']) + 1}",
                'level': random.choice(['temel', 'orta', 'ileri'])
            }
            self.hr_system['training']['certifications'].append(new_certification)
            
    def assess_performance(self):
        """Performans deÄŸerlendirmesi yapar"""
        # DeÄŸerlendirmeler
        if random.random() < 0.2:  # %20 ÅŸans
            new_evaluation = {
                'id': len(self.hr_system['performance']['evaluations']) + 1,
                'employee_id': random.randint(1, len(self.hr_system['personnel']['employees'])),
                'score': random.uniform(1, 5),
                'criteria': random.choice(['iÅŸ kalitesi', 'verimlilik', 'takÄ±m Ã§alÄ±ÅŸmasÄ±', 'liderlik'])
            }
            self.hr_system['performance']['evaluations'].append(new_evaluation)
            
        # Ã–dÃ¼ller
        if random.random() < 0.2:  # %20 ÅŸans
            new_reward = {
                'id': len(self.hr_system['performance']['rewards']) + 1,
                'employee_id': random.randint(1, len(self.hr_system['personnel']['employees'])),
                'type': random.choice(['prim', 'terfi', 'plaket', 'izin']),
                'value': random.uniform(1000, 10000)
            }
            self.hr_system['performance']['rewards'].append(new_reward)
            
    def check_career(self):
        """Kariyer geliÅŸimini kontrol eder"""
        # Kariyer yollarÄ±
        if random.random() < 0.2:  # %20 ÅŸans
            new_path = {
                'id': len(self.hr_system['career']['paths']) + 1,
                'employee_id': random.randint(1, len(self.hr_system['personnel']['employees'])),
                'current_level': random.choice(['junior', 'mid', 'senior']),
                'next_level': random.choice(['mid', 'senior', 'lead']),
                'progress': random.uniform(0.1, 0.9)
            }
            self.hr_system['career']['paths'].append(new_path)
            
        # Terfiler
        if random.random() < 0.2:  # %20 ÅŸans
            new_promotion = {
                'id': len(self.hr_system['career']['promotions']) + 1,
                'employee_id': random.randint(1, len(self.hr_system['personnel']['employees'])),
                'from_position': random.choice(['uzman', 'yÃ¶netici', 'mÃ¼dÃ¼r']),
                'to_position': random.choice(['yÃ¶netici', 'mÃ¼dÃ¼r', 'direktÃ¶r']),
                'date': time.time()
            }
            self.hr_system['career']['promotions'].append(new_promotion)
            
    def show_hr_panel(self):
        """HR panelini gÃ¶sterir"""
        self.hr_panel.visible = True
        
        # Panel baÅŸlÄ±ÄŸÄ±
        Text(
            parent=self.hr_panel,
            text='Ä°nsan KaynaklarÄ±',
            position=(0, 0.15),
            scale=2,
            color=color.white
        )
        
        # Personel
        y_pos = 0.05
        Text(
            parent=self.hr_panel,
            text=f"Toplam Ã‡alÄ±ÅŸan: {len(self.hr_system['personnel']['employees'])}",
            position=(0, y_pos),
            scale=1.2,
            color=color.blue
        )
        y_pos -= 0.05
        
        # EÄŸitim
        Text(
            parent=self.hr_panel,
            text=f"Aktif EÄŸitimler: {len(self.hr_system['training']['programs'])}",
            position=(0, y_pos),
            scale=1.2,
            color=color.green
        )
        y_pos -= 0.05
        
        # Performans
        Text(
            parent=self.hr_panel,
            text=f"DeÄŸerlendirmeler: {len(self.hr_system['performance']['evaluations'])}",
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
        
        # Ä°K performans skoru
        hr_score = (
            len(self.hr_system['personnel']['employees']) / 100 * 0.3 +
            sum(p['score'] for p in self.hr_system['performance']['evaluations']) / max(1, len(self.hr_system['performance']['evaluations'])) * 0.3 +
            sum(p['progress'] for p in self.hr_system['career']['paths']) / max(1, len(self.hr_system['career']['paths'])) * 0.2 +
            len(self.hr_system['training']['certifications']) / 50 * 0.2
        ) * 10
        Text(
            parent=self.hr_panel,
            text=f"Ä°K Skoru: {hr_score:.1f}/10",
            position=(0, y_pos),
            scale=1.2,
            color=color.red
        )
        
    def input(self, key):
        """Klavye giriÅŸlerini iÅŸler"""
        # ... existing code ...
        
        # HR kontrolleri
        if key == 'h':
            self.show_hr_panel()
            
    def update(self):
        """Her frame'de Ã§alÄ±ÅŸacak gÃ¼ncelleme fonksiyonu"""
        # ... existing code ...
        
        # HR sistemi gÃ¼ncellemesi
        self.update_hr_system()

    def set_player_age(self, age):
        """Oyuncunun yaÅŸÄ±nÄ± ayarlar ve Ã¶nerilen sÃ¼releri gÃ¼nceller"""
        self.health_system['player_age'] = age
        
        # YaÅŸa gÃ¶re Ã¶nerilen sÃ¼releri ayarla
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
        """SaÄŸlÄ±k sistemini gÃ¼nceller"""
        current_time = time.time()
        
        # Oyun sÃ¼resini gÃ¼ncelle
        self.health_system['play_time'] = current_time - self.start_time
        
        # Mola kontrolÃ¼
        if current_time - self.health_system['last_break'] >= self.health_system['recommended_break_interval']:
            self.show_break_notification()
            self.health_system['last_break'] = current_time
            self.health_system['break_time'] += self.health_system['break_duration']
            
        # SaÄŸlÄ±k tavsiyeleri gÃ¼ncelle
        if len(self.health_system['health_tips']) < 5:
            self.generate_health_tips()
            
    def show_break_notification(self):
        """Mola bildirimi gÃ¶sterir"""
        self.show_notification(
            "Mola zamanÄ±! LÃ¼tfen 5 dakika ara verin ve ÅŸunlarÄ± yapÄ±n:\n"
            "1. GÃ¶zlerinizi dinlendirin\n"
            "2. Esneme hareketleri yapÄ±n\n"
            "3. Su iÃ§in\n"
            "4. KÄ±sa bir yÃ¼rÃ¼yÃ¼ÅŸ yapÄ±n",
            duration=10
        )
        
    def generate_health_tips(self):
        """SaÄŸlÄ±klÄ± yaÅŸam tavsiyeleri oluÅŸturur"""
        tips = [
            "DÃ¼zenli egzersiz yapÄ±n - gÃ¼nde en az 30 dakika",
            "SaÄŸlÄ±klÄ± beslenin - meyve ve sebze tÃ¼ketin",
            "Yeterli uyku alÄ±n - gÃ¼nde 7-9 saat",
            "Su tÃ¼ketimine dikkat edin - gÃ¼nde 2-3 litre",
            "GÃ¶z saÄŸlÄ±ÄŸÄ±nÄ±z iÃ§in ekranla aranÄ±za mesafe bÄ±rakÄ±n",
            "DuruÅŸunuza dikkat edin - dÃ¼z oturun",
            "Stres yÃ¶netimi iÃ§in meditasyon yapÄ±n",
            "Sosyal iliÅŸkilerinizi gÃ¼Ã§lendirin",
            "Zihinsel aktiviteler yapÄ±n - kitap okuyun",
            "DÃ¼zenli saÄŸlÄ±k kontrolleri yaptÄ±rÄ±n"
        ]
        
        # Rastgele 5 tavsiye seÃ§
        selected_tips = random.sample(tips, 5)
        self.health_system['health_tips'] = selected_tips
        
    def show_health_panel(self):
        """SaÄŸlÄ±k panelini gÃ¶sterir"""
        self.health_panel.visible = True
        
        # Panel baÅŸlÄ±ÄŸÄ±
        Text(
            parent=self.health_panel,
            text='SaÄŸlÄ±k YÃ¶netimi',
            position=(0, 0.15),
            scale=2,
            color=color.white
        )
        
        # YaÅŸ bilgisi
        y_pos = 0.05
        Text(
            parent=self.health_panel,
            text=f"YaÅŸ: {self.health_system['player_age']}",
            position=(0, y_pos),
            scale=1.2,
            color=color.blue
        )
        y_pos -= 0.05
        
        # Oyun sÃ¼resi
        play_time_minutes = self.health_system['play_time'] / 60
        Text(
            parent=self.health_panel,
            text=f"Oyun SÃ¼resi: {play_time_minutes:.0f} dakika",
            position=(0, y_pos),
            scale=1.2,
            color=color.green
        )
        y_pos -= 0.05
        
        # Mola sÃ¼resi
        break_time_minutes = self.health_system['break_time'] / 60
        Text(
            parent=self.health_panel,
            text=f"Mola SÃ¼resi: {break_time_minutes:.0f} dakika",
            position=(0, y_pos),
            scale=1.2,
            color=color.yellow
        )
        y_pos -= 0.05
        
        # SaÄŸlÄ±k tavsiyeleri
        Text(
            parent=self.health_panel,
            text="SaÄŸlÄ±k Tavsiyeleri:",
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
        """Klavye giriÅŸlerini iÅŸler"""
        # ... existing code ...
        
        # SaÄŸlÄ±k kontrolleri
        if key == 'h':
            self.show_health_panel()
            
    def update(self):
        """Her frame'de Ã§alÄ±ÅŸacak gÃ¼ncelleme fonksiyonu"""
        # ... existing code ...
        
        # SaÄŸlÄ±k sistemi gÃ¼ncellemesi
        self.update_health_system()

    def update_exercise_system(self):
        """Egzersiz sistemini gÃ¼nceller"""
        current_time = time.time()
        
        # Egzersiz hatÄ±rlatmasÄ±
        if current_time - self.exercise_system['last_exercise'] >= self.exercise_system['exercise_interval']:
            self.show_exercise_notification()
            self.exercise_system['last_exercise'] = current_time
            
        # Mevcut egzersizleri gÃ¼ncelle
        if len(self.exercise_system['current_exercises']) < 3:
            self.generate_exercises()
            
    def show_exercise_notification(self):
        """Egzersiz bildirimi gÃ¶sterir"""
        exercises = self.generate_exercises()
        exercise_text = "Egzersiz zamanÄ±! Åžu hareketleri yapÄ±n:\n"
        for i, exercise in enumerate(exercises, 1):
            exercise_text += f"{i}. {exercise}\n"
            
        self.show_notification(
            exercise_text + "\nHer hareketi 30 saniye yapÄ±n ve 10 saniye dinlenin.",
            duration=15
        )
        
    def generate_exercises(self):
        """Yeni egzersizler oluÅŸturur"""
        exercises = []
        # Her kategoriden bir egzersiz seÃ§
        for category in ['stretching', 'strength', 'cardio']:
            exercise = random.choice(self.exercise_system['exercise_types'][category])
            exercises.append(exercise)
            
        self.exercise_system['current_exercises'] = exercises
        return exercises
        
    def show_exercise_panel(self):
        """Egzersiz panelini gÃ¶sterir"""
        self.exercise_panel.visible = True
        
        # Panel baÅŸlÄ±ÄŸÄ±
        Text(
            parent=self.exercise_panel,
            text='Egzersiz ProgramÄ±',
            position=(0, 0.15),
            scale=2,
            color=color.white
        )
        
        # Son egzersiz zamanÄ±
        y_pos = 0.05
        last_exercise_minutes = (time.time() - self.exercise_system['last_exercise']) / 60
        Text(
            parent=self.exercise_panel,
            text=f"Son Egzersiz: {last_exercise_minutes:.0f} dakika Ã¶nce",
            position=(0, y_pos),
            scale=1.2,
            color=color.blue
        )
        y_pos -= 0.05
        
        # GÃ¼nlÃ¼k egzersiz hedefi
        Text(
            parent=self.exercise_panel,
            text="GÃ¼nlÃ¼k Hedef: 30 dakika",
            position=(0, y_pos),
            scale=1.2,
            color=color.green
        )
        y_pos -= 0.05
        
        # Mevcut egzersizler
        Text(
            parent=self.exercise_panel,
            text="GÃ¼ncel Egzersizler:",
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
            
        # Egzersiz Ã¶nerileri
        Text(
            parent=self.exercise_panel,
            text="Ã–neriler:",
            position=(0, y_pos),
            scale=1.2,
            color=color.orange
        )
        y_pos -= 0.05
        
        tips = [
            "Her saat baÅŸÄ± 5 dakika egzersiz yapÄ±n",
            "Egzersiz Ã¶ncesi Ä±sÄ±nma hareketleri yapÄ±n",
            "Egzersiz sonrasÄ± esneme hareketleri yapÄ±n",
            "DÃ¼zenli su tÃ¼ketin",
            "DoÄŸru nefes almayÄ± unutmayÄ±n"
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
        """Klavye giriÅŸlerini iÅŸler"""
        # ... existing code ...
        
        # Egzersiz kontrolleri
        if key == 'e':
            self.show_exercise_panel()
            
    def update(self):
        """Her frame'de Ã§alÄ±ÅŸacak gÃ¼ncelleme fonksiyonu"""
        # ... existing code ...
        
        # Egzersiz sistemi gÃ¼ncellemesi
        self.update_exercise_system()

if __name__ == '__main__':
    app = FinAsisGame(1)
    app.run() 