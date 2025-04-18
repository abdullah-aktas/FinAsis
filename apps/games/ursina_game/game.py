from __future__ import absolute_import, unicode_literals
import os
import random
from datetime import datetime, timedelta
import json
from ursina import Entity, Vec3, color, window, Ursina, Text, Button, Func, camera, destroy, application
from ursina.prefabs.first_person_controller import FirstPersonController

# Django ayarlarını yükle
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'finasis.settings')
import django
django.setup()

from company_management.models import Company, Department, Employee

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

def run_game():
    """Oyunu başlat"""
    # Ursina uygulamasını başlat
    app = Ursina()
    
    # Pencere ayarları
    window.title = 'FinAsis - Finansal Eğitim Simülasyonu'
    window.borderless = False
    window.fullscreen = game_settings['fullscreen']
    window.exit_button.visible = False
    window.fps_counter.enabled = True
    
    # UI oluştur
    create_ui()
    
    # Görev sistemini başlat
    initialize_quest_system()
    
    # Eğitim modunu kontrol et
    if game_settings['tutorial_enabled'] and not player['tutorial_progress']['basic_trading']:
        start_tutorial()
    
    # Ana oyun döngüsünü başlat
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

if __name__ == '__main__':
    run_game() 