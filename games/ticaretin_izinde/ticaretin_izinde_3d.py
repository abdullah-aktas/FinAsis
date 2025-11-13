# -*- coding: utf-8 -*-
from ursina import Ursina, Entity, Text, Button, window, camera, color, mouse, Vec3, Func, destroy, application, Sky, Tooltip, invoke, held_keys
from typing import Any, cast, Optional
from ursina.prefabs.first_person_controller import FirstPersonController
import random
import json
import os
import sys
from datetime import datetime, timedelta
from ..base_game import BaseGame

# Helpers modülünü import et (renk hatasını çözen)
sys.path.append(os.path.dirname(__file__))
from helpers import get_age_group_colors, get_financial_status_color

class TicaretinIzinde3D(BaseGame):
    def __init__(self):
        super().__init__()
        self.app = Ursina()
        
        # Pencere ayarları
        window.title = 'FinQuest 3D - FinAsis'
        window.borderless = False
        window.fullscreen = False
        window.exit_button.visible = True
        window.fps_counter.enabled = True
        
        # Oyun verileri
        self.game_state = {
            'player': {
                'name': 'Oyuncu',
                'age_group': 'adult',  # child, teen, adult, senior
                'character': 'businessman',  # businessman, student, teacher, retiree
                'money': 10000,
                'inventory': {},
                'level': 1,
                'exp': 0,
                'company': {
                    'name': '',
                    'type': '',  # perakende, toptan, üretim
                    'location': '',
                    'employees': 0,
                    'storage_capacity': 100
                },
                'knowledge': {
                    'accounting': 1,
                    'trading': 1,
                    'management': 1
                }
            },
            'market': {
                'products': {}
            },
            'time': {
                'day': 1,
                'month': 1,
                'year': 2025
            },
            'locations': {},
            'tutorial_completed': False,
            'active_quests': [],
            'completed_quests': []
        }
        
        # Ürünleri yükle
        self.load_products()
        
        # UI elemanları
        self.ui_elements = {}
        
        # UI öznitelik yer tutucuları (finquest.ui tarafından oluşturulacak)
        self.info_panel: Optional[Entity] = None
        self.player_name: Optional[Text] = None
        self.player_money: Optional[Text] = None
        self.player_level: Optional[Text] = None
        self.date_panel: Optional[Entity] = None
        self.date_text: Optional[Text] = None
        self.quest_panel: Optional[Entity] = None
        self.quest_title: Optional[Text] = None
        self.quest_list_entity: Optional[Entity] = None
        self.interaction_prompt: Optional[Text] = None
        
        # Dünya elemanları
        self.world_elements = {}
        
        # Oyuncu kontrolcüsü
        self.player_controller = None
        
        # Görünüm ve tema için renk şeması (yaş grubuna göre)
        self.color_scheme = get_age_group_colors(self.game_state['player']['age_group'])
        
        # Oyun durumları
        self.current_screen = 'main_menu'  # main_menu, character_select, game, store, bank, office, tutorial
        
        # Görevleri yükle
        self.quests = self.create_quests()
        
        # İpuçları
        self.financial_tips = self.load_financial_tips()
        
        # Etkileşim hedefi
        self.interaction_target = None
        
        # Ana menüyü oluştur
        self.create_main_menu()
        
        # Ursina'yı çalıştır
        self.app.run()
    
    def load_products(self):
        """Ürün veritabanını yükle"""
        products = {
            'elektronik': {
                'telefon': {'base_price': 5000, 'weight': 0.2},
                'laptop': {'base_price': 15000, 'weight': 2.0},
                'tablet': {'base_price': 3000, 'weight': 0.5}
            },
            'gıda': {
                'ekmek': {'base_price': 5, 'weight': 0.5},
                'süt': {'base_price': 15, 'weight': 1.0},
                'peynir': {'base_price': 50, 'weight': 0.5}
            },
            'tekstil': {
                'tişört': {'base_price': 100, 'weight': 0.2},
                'pantolon': {'base_price': 200, 'weight': 0.5},
                'ayakkabı': {'base_price': 300, 'weight': 0.8}
            }
        }
        
        # Ürünleri market fiyatlarına ekle
        for category, items in products.items():
            for product_name, product_data in items.items():
                # Her ürün için rastgele talep oluştur (0.1 - 0.9 arası)
                demand = random.uniform(0.1, 0.9)
                # Ürünü markete ekle
                self.game_state['market']['products'][product_name] = {
                    'price': product_data['base_price'],
                    'base_price': product_data['base_price'],
                    'weight': product_data['weight'],
                    'category': category,
                    'demand': demand
                }
    
    def create_quests(self):
        """Oyun görevlerini finquest modülünden oluştur"""
        try:
            from games.finquest.quests import create_quests as _create_quests
        except Exception:
            # Alternatif bağıl import (geliştirme sırasında)
            from ...games.finquest.quests import create_quests as _create_quests  # type: ignore
        return _create_quests(self)
    
    def load_financial_tips(self):
        """Finansal ipuçlarını finquest modülünden yükle"""
        try:
            from games.finquest.tips import load_financial_tips as _load
        except Exception:
            from ...games.finquest.tips import load_financial_tips as _load  # type: ignore
        return _load()
    
    def check_diverse_inventory(self):
        """Envanterde farklı kategorilerden ürün olup olmadığını kontrol et"""
        try:
            from games.finquest.inventory import has_diverse_inventory
        except Exception:
            from ...games.finquest.inventory import has_diverse_inventory  # type: ignore
        return has_diverse_inventory(self, 3)
    
    def create_main_menu(self):
        """Ana menüyü oluştur"""
        # Arka plan
        self.background = Entity(
            model='quad',
            scale=Vec3(2, 1, 1),
            color=self.color_scheme['background'],
            parent=camera.ui
        )
        
        # Başlık
        self.title = Text(
            text='FinQuest 3D',
            scale=3,
            position=(0, 0.4),
            origin=(0, 0),
            color=self.color_scheme['primary'],
            parent=camera.ui
        )
        
        # Alt başlık
        self.subtitle = Text(
            text='Finansal Eğitim Simülasyonu',
            scale=1.5,
            position=(0, 0.3),
            origin=(0, 0),
            color=self.color_scheme['secondary'],
            parent=camera.ui
        )
        
        # Yaş grubu seçimi
        self.age_group_text = Text(
            text='Yaş grubunuzu seçin:',
            scale=1.5,
            position=(0, 0.2),
            origin=(0, 0),
            color=self.color_scheme['text'],
            parent=camera.ui
        )
        
        # Yaş grubu butonları
        self.age_buttons = []
        age_groups = [
            ('Çocuk (5-12)', 'child'),
            ('Genç (13-18)', 'teen'),
            ('Yetişkin (19-65)', 'adult'),
            ('Yaşlı (65+)', 'senior')
        ]
        
        for i, (age_text, age_key) in enumerate(age_groups):
            btn = Button(
                text=age_text,
                scale=(0.3, 0.05),
                position=(0, 0.15 - i*0.06),
                parent=camera.ui,
                on_click=Func(self.select_age_group, age_key)
            )
            btn.color = self.color_scheme['primary'] if age_key == self.game_state['player']['age_group'] else color.gray
            btn.highlight_color = self.color_scheme['accent']
            self.age_buttons.append((btn, age_key))
        
        # Başlat butonu
        self.start_button = Button(
            text='Karakter Seçimine Geç',
            scale=(0.4, 0.06),
            position=(0, -0.2),
            parent=camera.ui,
            on_click=Func(self.start_character_selection)
        )
        self.start_button.color = self.color_scheme['secondary']
        self.start_button.highlight_color = self.color_scheme['accent']
        
        # Çıkış butonu
        self.exit_button = Button(
            text='Çıkış',
            scale=(0.2, 0.05),
            position=(0, -0.3),
            parent=camera.ui,
            on_click=Func(application.quit)
        )
        self.exit_button.color = color.red
        self.exit_button.highlight_color = color.red.tint(0.2)
        
        # UI elemanlarını kaydet
        self.ui_elements['main_menu'] = [
            self.background, self.title, self.subtitle,
            self.age_group_text, *[btn for btn, _ in self.age_buttons],
            self.start_button, self.exit_button
        ]
    
    def select_age_group(self, age_group):
        """Yaş grubunu seç ve temayı güncelle"""
        # Yaş grubunu değiştir
        self.game_state['player']['age_group'] = age_group
        
        # Renk şemasını güncelle
        self.color_scheme = get_age_group_colors(age_group)
        
        # Butonları güncelle
        for button, key in self.age_buttons:
            button.color = self.color_scheme['primary'] if key == age_group else color.gray
        
        # Ana ekran renklerini güncelle
        self.background.color = self.color_scheme['background']
        self.title.color = self.color_scheme['primary']
        self.subtitle.color = self.color_scheme['secondary']
        self.start_button.color = self.color_scheme['secondary']
        
        # Görevleri yeniden yükle (yaş grubuna göre)
        self.quests = self.create_quests()
    
    def start_character_selection(self):
        """Karakter seçim ekranına geç"""
        # Ana menüyü temizle
        for element in self.ui_elements['main_menu']:
            destroy(element)
        
        # Karakter seçim ekranını oluştur
        self.create_character_selection()
    
    def create_character_selection(self):
        """Karakter seçim ekranını oluştur"""
        # Oyun durumunu güncelle
        self.current_screen = 'character_select'
        
        # Arka plan
        self.background = Entity(
            model='quad',
            scale=Vec3(2, 1, 1),
            color=self.color_scheme['background'],
            parent=camera.ui
        )
        
        # Başlık
        self.title = Text(
            text='Karakter Seçimi',
            scale=3,
            position=(0, 0.4),
            origin=(0, 0),
            color=self.color_scheme['primary'],
            parent=camera.ui
        )
        
        # Karakter açıklaması
        self.character_description = Text(
            text='',
            scale=1.2,
            position=(0.3, 0),
            origin=(0, 0),
            color=self.color_scheme['text'],
            parent=camera.ui
        )
        
        # Karakter butonları
        self.character_buttons = []
        characters = [
            ('İş İnsanı', 'businessman', 'İş dünyasında deneyimli bir girişimci. Ticaret ve yatırım konusunda avantajlı başlar.'),
            ('Öğrenci', 'student', 'Yeni mezun olmuş bir öğrenci. Düşük sermaye ama yüksek öğrenme kapasitesi.'),
            ('Öğretmen', 'teacher', 'Bilgi ve eğitim odaklı. Finansal okuryazarlık ve planlama avantajı.'),
            ('Emekli', 'retiree', 'Deneyimli bir emekli. Başlangıçta daha yüksek sermaye ama daha düşük enerji.')
        ]
        
        for i, (char_name, char_key, char_desc) in enumerate(characters):
            btn = Button(
                text=char_name,
                scale=(0.3, 0.05),
                position=(-0.3, 0.2 - i*0.1),
                parent=camera.ui,
                on_click=Func(self.select_character, char_key, char_desc)
            )
            btn.color = color.gray
            btn.highlight_color = self.color_scheme['accent']
            self.character_buttons.append((btn, char_key))
        
        # Şirket kuruluş bilgileri
        self.company_name_text = Text(
            text='Şirket İsmi:',
            scale=1.2,
            position=(-0.3, -0.2),
            origin=(0, 0),
            color=self.color_scheme['text'],
            parent=camera.ui
        )
        
        self.company_name_field = Button(
            text='Şirketim A.Ş.',
            scale=(0.3, 0.05),
            position=(-0.3, -0.25),
            parent=camera.ui
        )
        self.company_name_field.color = color.gray.tint(0.2)
        self.company_name_field.highlight_color = color.light_gray
        
        self.company_type_text = Text(
            text='Şirket Türü:',
            scale=1.2,
            position=(-0.3, -0.35),
            origin=(0, 0),
            color=self.color_scheme['text'],
            parent=camera.ui
        )
        
        # Şirket türü butonları
        self.company_type_buttons = []
        company_types = [
            ('Perakende', 'perakende'),
            ('Toptan', 'toptan'),
            ('Üretim', 'uretim')
        ]
        
        for i, (type_name, type_key) in enumerate(company_types):
            btn = Button(
                text=type_name,
                scale=(0.15, 0.05),
                position=(-0.45 + i*0.15, -0.4),
                parent=camera.ui,
                on_click=Func(self.select_company_type, type_key)
            )
            btn.color = color.gray
            btn.highlight_color = self.color_scheme['accent']
            self.company_type_buttons.append((btn, type_key))
        
        # Başlat butonu
        self.start_game_button = Button(
            text='Oyunu Başlat',
            scale=(0.3, 0.06),
            position=(0, -0.6),
            parent=camera.ui,
            on_click=Func(self.start_game)
        )
        self.start_game_button.color = self.color_scheme['secondary']
        self.start_game_button.highlight_color = self.color_scheme['accent']
        
        # Geri butonu
        self.back_button = Button(
            text='Geri',
            scale=(0.2, 0.05),
            position=(-0.4, -0.6),
            parent=camera.ui,
            on_click=Func(self.go_back_to_main_menu)
        )
        self.back_button.color = color.red
        self.back_button.highlight_color = color.red.tint(0.2)
        
        # UI elemanlarını kaydet
        self.ui_elements['character_select'] = [
            self.background, self.title, self.character_description,
            *[btn for btn, _ in self.character_buttons],
            self.company_name_text, self.company_name_field,
            self.company_type_text, *[btn for btn, _ in self.company_type_buttons],
            self.start_game_button, self.back_button
        ]
    
    def select_character(self, character, description):
        """Karakteri seç"""
        # Karakteri kaydet
        self.game_state['player']['character'] = character
        
        # Butonları güncelle
        for button, key in self.character_buttons:
            button.color = self.color_scheme['primary'] if key == character else color.gray
        
        # Açıklamayı güncelle
        self.character_description.text = description
        
        # Karakter türüne göre başlangıç parası ve bilgilerini ayarla
        if character == 'businessman':
            self.game_state['player']['money'] = 15000
            self.game_state['player']['knowledge']['trading'] = 2
        elif character == 'student':
            self.game_state['player']['money'] = 5000
            self.game_state['player']['knowledge']['accounting'] = 2
        elif character == 'teacher':
            self.game_state['player']['money'] = 10000
            self.game_state['player']['knowledge']['management'] = 2
        elif character == 'retiree':
            self.game_state['player']['money'] = 20000
            self.game_state['player']['knowledge']['trading'] = 1
    
    def select_company_type(self, company_type):
        """Şirket türünü seç"""
        # Şirket türünü kaydet
        self.game_state['player']['company']['type'] = company_type
        
        # Butonları güncelle
        for button, key in self.company_type_buttons:
            button.color = self.color_scheme['primary'] if key == company_type else color.gray
    
    def go_back_to_main_menu(self):
        """Ana menüye dön"""
        # Karakter seçim ekranını temizle
        for element in self.ui_elements['character_select']:
            destroy(element)
        
        # Ana menüyü tekrar oluştur
        self.create_main_menu()
    
    def start_game(self):
        """Oyunu başlat"""
        # Şirket ismini kaydet
        self.game_state['player']['company']['name'] = self.company_name_field.text
        
        # Karakter seçim ekranını temizle
        for element in self.ui_elements['character_select']:
            destroy(element)
        
        # Eğitim tamamlanmadıysa eğitimi başlat, aksi halde oyunu başlat
        if not self.game_state['tutorial_completed']:
            self.start_tutorial()
        else:
            self.create_game_world()
    
    def start_tutorial(self):
        """Eğitim modunu başlat"""
        # Oyun durumunu güncelle
        self.current_screen = 'tutorial'
        
        # Eğitim dünyasını oluştur
        self.create_tutorial_world()
    
    def create_tutorial_world(self):
        """Eğitim dünyasını oluştur (finquest.world'e delege)"""
        try:
            from games.finquest.world import create_tutorial_world as _create_tutorial_world
        except Exception:
            from ...games.finquest.world import create_tutorial_world as _create_tutorial_world  # type: ignore
        _create_tutorial_world(self)
    
    def complete_tutorial(self):
        """Eğitimi tamamla"""
        # Eğitimi tamamlandı olarak işaretle
        self.game_state['tutorial_completed'] = True
        
        # Dünya öğelerini temizle
        for category, elements in self.world_elements.items():
            if isinstance(elements, list):
                for element in elements:
                    destroy(element)
            else:
                destroy(elements)
        
        # UI elemanlarını temizle
        for child in camera.ui.children:
            destroy(child)
        
        # Ana oyun dünyasını oluştur
        self.create_game_world()
    
    def create_game_world(self):
        """Ana oyun dünyasını oluştur (finquest.world'e delege)"""
        try:
            from games.finquest.world import create_game_world as _create_game_world
        except Exception:
            from ...games.finquest.world import create_game_world as _create_game_world  # type: ignore
        _create_game_world(self)
    
    def create_city_center(self):
        """Şehir merkezi oluştur (finquest.world'e delege)"""
        try:
            from games.finquest.world import create_city_center as _create_city_center
        except Exception:
            from ...games.finquest.world import create_city_center as _create_city_center  # type: ignore
        _create_city_center(self)
    
    def create_game_ui(self):
        """Oyun içi UI oluştur (finquest.ui'e delege)"""
        try:
            from games.finquest.ui import create_game_ui as _create_ui
        except Exception:
            from ...games.finquest.ui import create_game_ui as _create_ui  # type: ignore
        _create_ui(self)
    
    def update_quest_list(self):
        """Görev listesini güncelle (finquest.ui'e delege)"""
        try:
            from games.finquest.ui import update_quest_list as _update_ql
        except Exception:
            from ...games.finquest.ui import update_quest_list as _update_ql  # type: ignore
        _update_ql(self)
    
    def assign_default_quests(self):
        """Varsayılan görevleri ata"""
        # Eğitim görevlerini ekle
        for quest in self.quests['tutorial']:
            if quest['id'] not in self.game_state['active_quests'] and quest['id'] not in self.game_state['completed_quests']:
                self.game_state['active_quests'].append(quest['id'])
        
        # Yaş grubuna göre özel görevleri ekle
        if 'special' in self.quests:
            for quest in self.quests['special']:
                if quest['id'] not in self.game_state['active_quests'] and quest['id'] not in self.game_state['completed_quests']:
                    self.game_state['active_quests'].append(quest['id'])
        
        # Görev listesini güncelle
        self.update_quest_list()
    
    def show_interaction_prompt(self, text):
        """Etkileşim prompt'unu göster (finquest.ui'e delege)"""
        try:
            from games.finquest.ui import show_interaction_prompt as _show_ip
        except Exception:
            from ...games.finquest.ui import show_interaction_prompt as _show_ip  # type: ignore
        _show_ip(self, text)
    
    def hide_interaction_prompt(self):
        """Etkileşim prompt'unu gizle (finquest.ui'e delege)"""
        try:
            from games.finquest.ui import hide_interaction_prompt as _hide_ip
        except Exception:
            from ...games.finquest.ui import hide_interaction_prompt as _hide_ip  # type: ignore
        _hide_ip(self)
    
    def update(self):
        """Oyun güncelleme fonksiyonu"""
        if self.current_screen == 'game':
            # Tuş basışlarını kontrol et
            if cast(Any, held_keys)['e'] and self.interaction_target:
                self.enter_building(self.interaction_target)
            
            # Görevleri kontrol et
            self.check_quests()
    
    def enter_building(self, building_type):
        """Binaya gir"""
        if building_type == 'market':
            self.enter_market()
        elif building_type == 'bank':
            self.enter_bank()
        elif building_type == 'office':
            self.enter_office()
        elif building_type == 'education':
            self.enter_education_center()
    
    def enter_market(self):
        """Markete gir"""
        # Pazar ziyareti görevi için işaretle
        self.game_state['marketi_ziyaret_etti'] = True
        
        # Market UI'sını göster
        # (Bu kısım daha sonra eklenecek)
    
    def enter_bank(self):
        """Bankaya gir"""
        # Banka ziyareti görevi için işaretle
        self.game_state['bankayi_ziyaret_etti'] = True
        
        # Banka UI'sını göster
        # (Bu kısım daha sonra eklenecek)
    
    def enter_office(self):
        """Ofise gir"""
        # Ofis UI'sını göster
        # (Bu kısım daha sonra eklenecek)
    
    def enter_education_center(self):
        """Eğitim merkezine gir"""
        # Eğitim merkezi UI'sını göster
        # (Bu kısım daha sonra eklenecek)
    
    def check_quests(self):
        """Görevleri kontrol et ve tamamlananları güncelle"""
        completed_quests = []
        
        for quest_id in self.game_state['active_quests']:
            # Görev verilerini bul
            quest_data = None
            for category, quests in self.quests.items():
                for quest in quests:
                    if quest['id'] == quest_id:
                        quest_data = quest
                        break
                if quest_data:
                    break
            
            if quest_data and quest_data['completion_criteria']():
                # Görevi tamamla
                completed_quests.append(quest_id)
                
                # Ödülü ver
                self.game_state['player']['money'] += quest_data['reward'].get('money', 0)
                self.game_state['player']['exp'] += quest_data['reward'].get('exp', 0)
                
                # Görev tamamlandı bildirimi göster
                self.show_quest_completion(quest_data)
        
        # Tamamlanan görevleri aktif listeden kaldır ve tamamlanan listeye ekle
        for quest_id in completed_quests:
            self.game_state['active_quests'].remove(quest_id)
            self.game_state['completed_quests'].append(quest_id)
        
        # Görev listesini güncelle
        if completed_quests:
            self.update_quest_list()
            self.check_level_up()
    
    def show_quest_completion(self, quest_data):
        """Görev tamamlandı bildirimi göster (finquest.ui'e delege)"""
        try:
            from games.finquest.ui import show_quest_completion as _show_qc
        except Exception:
            from ...games.finquest.ui import show_quest_completion as _show_qc  # type: ignore
        _show_qc(self, quest_data)
    
    def check_level_up(self):
        """Seviye atlama kontrolü"""
        exp = self.game_state['player']['exp']
        current_level = self.game_state['player']['level']
        next_level_exp = current_level * 100  # Her seviye için 100 XP
        
        if exp >= next_level_exp:
            # Seviye atla
            self.game_state['player']['level'] += 1
            self.game_state['player']['exp'] -= next_level_exp
            
            # Seviye atlama bildirimi göster
            self.show_level_up()
            
            # Oyuncu bilgilerini güncelle
            if self.player_level is not None:
                self.player_level.text = f"Seviye: {self.game_state['player']['level']}"
    
    def show_level_up(self):
        """Seviye atlama bildirimi göster (finquest.ui'e delege)"""
        try:
            from games.finquest.ui import show_level_up as _show_lu
        except Exception:
            from ...games.finquest.ui import show_level_up as _show_lu  # type: ignore
        _show_lu(self)

# Eğer doğrudan çalıştırılıyorsa oyunu başlat
if __name__ == '__main__':
    game = TicaretinIzinde3D() 