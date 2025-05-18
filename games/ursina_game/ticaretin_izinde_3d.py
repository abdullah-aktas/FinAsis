# -*- coding: utf-8 -*-
from ursina import Ursina, Entity, Text, Button, window, camera, color, mouse, Vec3, Func, destroy, application, Sky, Tooltip
from ursina.prefabs.first_person_controller import FirstPersonController
import random
import json
import os
import sys
from datetime import datetime, timedelta

# Helpers modülünü import et (renk hatasını çözen)
sys.path.append(os.path.dirname(__file__))
from helpers import get_age_group_colors, get_financial_status_color

class TicaretinIzinde3D:
    def __init__(self):
        # Ursina uygulamasını başlat
        self.app = Ursina()
        
        # Pencere ayarları
        window.title = 'Ticaretin İzinde 3D - FinAsis'
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
        """Oyun görevlerini oluştur"""
        quests = {
            'tutorial': [
                {
                    'id': 'market_visit',
                    'title': 'Market Ziyareti',
                    'description': 'Marketi ziyaret edin ve bir ürün satın alın.',
                    'reward': {'money': 100, 'exp': 10},
                    'completion_criteria': lambda: 'marketi_ziyaret_etti' in self.game_state
                },
                {
                    'id': 'bank_visit',
                    'title': 'Banka Ziyareti',
                    'description': 'Bankayı ziyaret edin ve hesap bilgilerinizi kontrol edin.',
                    'reward': {'money': 50, 'exp': 10},
                    'completion_criteria': lambda: 'bankayi_ziyaret_etti' in self.game_state
                }
            ],
            'trading': [
                {
                    'id': 'first_sale',
                    'title': 'İlk Satış',
                    'description': 'Bir ürün satın alın ve kârla satın.',
                    'reward': {'money': 200, 'exp': 20},
                    'completion_criteria': lambda: 'ilk_satisi_yapti' in self.game_state
                },
                {
                    'id': 'diverse_inventory',
                    'title': 'Çeşitli Envanter',
                    'description': 'En az 3 farklı kategoriden ürün satın alın.',
                    'reward': {'money': 300, 'exp': 30},
                    'completion_criteria': lambda: self.check_diverse_inventory()
                }
            ],
            'accounting': [
                {
                    'id': 'income_statement',
                    'title': 'Gelir Tablosu',
                    'description': 'Gelir tablosunu oluşturun ve 1 haftalık kâr-zarar durumunuzu görün.',
                    'reward': {'money': 500, 'exp': 50},
                    'completion_criteria': lambda: 'gelir_tablosu_olusturuldu' in self.game_state
                },
                {
                    'id': 'balance_sheet',
                    'title': 'Bilanço',
                    'description': 'Şirketinizin bilançosunu oluşturun.',
                    'reward': {'money': 500, 'exp': 50},
                    'completion_criteria': lambda: 'bilanco_olusturuldu' in self.game_state
                }
            ]
        }
        
        # Yaş grubuna göre farklı görevler ekle
        age_group = self.game_state['player']['age_group']
        if age_group == 'child':
            quests['special'] = [
                {
                    'id': 'piggy_bank',
                    'title': 'Kumbara',
                    'description': 'Para biriktirmeyi öğrenin, 1000 TL biriktirin.',
                    'reward': {'money': 100, 'exp': 10},
                    'completion_criteria': lambda: self.game_state['player']['money'] >= 1000
                }
            ]
        elif age_group == 'teen':
            quests['special'] = [
                {
                    'id': 'budget_plan',
                    'title': 'Bütçe Planı',
                    'description': 'Haftalık bütçe planı oluşturun ve ona bağlı kalın.',
                    'reward': {'money': 200, 'exp': 20},
                    'completion_criteria': lambda: 'butce_plani_olusturuldu' in self.game_state
                }
            ]
        elif age_group == 'adult':
            quests['special'] = [
                {
                    'id': 'investment',
                    'title': 'Yatırım',
                    'description': 'Bir yatırım aracına yatırım yapın.',
                    'reward': {'money': 500, 'exp': 50},
                    'completion_criteria': lambda: 'yatirim_yapti' in self.game_state
                }
            ]
        elif age_group == 'senior':
            quests['special'] = [
                {
                    'id': 'retirement_plan',
                    'title': 'Emeklilik Planı',
                    'description': 'Emeklilik gelir stratejisi oluşturun.',
                    'reward': {'money': 1000, 'exp': 100},
                    'completion_criteria': lambda: 'emeklilik_plani_olusturuldu' in self.game_state
                }
            ]
        
        return quests
    
    def load_financial_tips(self):
        """Finansal ipuçlarını yükle"""
        return {
            'accounting': [
                "Muhasebe, işletmenin finansal işlemlerini kaydetme, sınıflandırma ve raporlama sürecidir.",
                "Bilanço, işletmenin varlıklarını ve bu varlıkların kaynaklarını gösteren finansal tablodur.",
                "Gelir tablosu, işletmenin belirli bir dönemdeki gelir ve giderlerini gösteren finansal tablodur.",
                "Çift taraflı kayıt sistemi, her işlem için en az iki hesabı etkiler (borç ve alacak)."
            ],
            'trading': [
                "Alış fiyatına kâr marjı ekleyerek satış fiyatını belirlemelisiniz.",
                "Talep yüksekken satın alıp, talep düşükken satmak zarar etmenize neden olabilir.",
                "Stok devir hızı, envanterinizin ne kadar hızlı satıldığını gösterir.",
                "Nakit akışı yönetimi, işletmenizin hayatta kalması için kritik öneme sahiptir."
            ],
            'banking': [
                "Bileşik faiz, paranızın zaman içinde büyümesini sağlar.",
                "Kredi, işletme sermayenizi artırmanın bir yoludur, ancak geri ödeme planını dikkatlice değerlendirin.",
                "Yatırım çeşitlendirmesi, riski azaltmanın ve potansiyel getiriyi artırmanın bir yoludur.",
                "Banka kredisi kullanırken faiz oranları ve vade süresi önemli faktörlerdir."
            ]
        }
    
    def check_diverse_inventory(self):
        """Envanterde farklı kategorilerden ürün olup olmadığını kontrol et"""
        categories = set()
        for product_name in self.game_state['player']['inventory']:
            if product_name in self.game_state['market']['products']:
                category = self.game_state['market']['products'][product_name]['category']
                categories.add(category)
        
        return len(categories) >= 3
    
    def create_main_menu(self):
        """Ana menüyü oluştur"""
        # Arka plan
        self.background = Entity(
            model='quad',
            scale=(2, 1),
            color=self.color_scheme['background'],
            parent=camera.ui
        )
        
        # Başlık
        self.title = Text(
            text='Ticaretin İzinde 3D',
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
                color=self.color_scheme['primary'] if age_key == self.game_state['player']['age_group'] else color.gray,
                highlight_color=self.color_scheme['accent'],
                parent=camera.ui,
                on_click=Func(self.select_age_group, age_key)
            )
            self.age_buttons.append((btn, age_key))
        
        # Başlat butonu
        self.start_button = Button(
            text='Karakter Seçimine Geç',
            scale=(0.4, 0.06),
            position=(0, -0.2),
            color=self.color_scheme['secondary'],
            highlight_color=self.color_scheme['accent'],
            parent=camera.ui,
            on_click=Func(self.start_character_selection)
        )
        
        # Çıkış butonu
        self.exit_button = Button(
            text='Çıkış',
            scale=(0.2, 0.05),
            position=(0, -0.3),
            color=color.red,
            highlight_color=color.red.tint(0.2),
            parent=camera.ui,
            on_click=Func(application.quit)
        )
        
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
            scale=(2, 1),
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
                color=color.gray,
                highlight_color=self.color_scheme['accent'],
                parent=camera.ui,
                on_click=Func(self.select_character, char_key, char_desc)
            )
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
            color=color.gray.tint(0.2),
            highlight_color=color.light_gray,
            parent=camera.ui
        )
        
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
                color=color.gray,
                highlight_color=self.color_scheme['accent'],
                parent=camera.ui,
                on_click=Func(self.select_company_type, type_key)
            )
            self.company_type_buttons.append((btn, type_key))
        
        # Başlat butonu
        self.start_game_button = Button(
            text='Oyunu Başlat',
            scale=(0.3, 0.06),
            position=(0, -0.6),
            color=self.color_scheme['secondary'],
            highlight_color=self.color_scheme['accent'],
            parent=camera.ui,
            on_click=Func(self.start_game)
        )
        
        # Geri butonu
        self.back_button = Button(
            text='Geri',
            scale=(0.2, 0.05),
            position=(-0.4, -0.6),
            color=color.red,
            highlight_color=color.red.tint(0.2),
            parent=camera.ui,
            on_click=Func(self.go_back_to_main_menu)
        )
        
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
        """Eğitim dünyasını oluştur"""
        # Gökyüzü oluştur
        self.sky = Sky()
        
        # Zemin oluştur
        self.ground = Entity(
            model='plane',
            scale=(100, 1, 100),
            color=color.green,
            texture='grass',
            collider='box'
        )
        
        # Duvarlar
        self.walls = [
            Entity(model='cube', scale=(1, 5, 100), position=(-50, 2.5, 0), color=color.gray, texture='brick', collider='box'),
            Entity(model='cube', scale=(1, 5, 100), position=(50, 2.5, 0), color=color.gray, texture='brick', collider='box'),
            Entity(model='cube', scale=(100, 5, 1), position=(0, 2.5, 50), color=color.gray, texture='brick', collider='box'),
            Entity(model='cube', scale=(100, 5, 1), position=(0, 2.5, -50), color=color.gray, texture='brick', collider='box')
        ]
        
        # Eğitim binaları
        self.tutorial_buildings = [
            Entity(model='cube', scale=(10, 5, 10), position=(20, 2.5, 20), color=color.azure, texture='brick', collider='box'),
            Entity(model='cube', scale=(10, 7, 10), position=(-20, 3.5, -20), color=color.orange, texture='brick', collider='box'),
            Entity(model='cube', scale=(10, 4, 10), position=(20, 2, -20), color=color.green, texture='brick', collider='box'),
            Entity(model='cube', scale=(10, 6, 10), position=(-20, 3, 20), color=color.yellow, texture='brick', collider='box')
        ]
        
        # Bina tabelaları
        self.building_signs = [
            Entity(text='MARKET', scale=2, position=(20, 6, 20), color=color.blue, billboard=True),
            Entity(text='BANKA', scale=2, position=(-20, 8, -20), color=color.gold, billboard=True),
            Entity(text='OFİS', scale=2, position=(20, 5, -20), color=color.lime, billboard=True),
            Entity(text='EĞİTİM MERKEZİ', scale=2, position=(-20, 6.5, 20), color=color.red, billboard=True)
        ]
        
        # Oyuncu kontrolcüsü
        self.player_controller = FirstPersonController(
            position=(0, 1, 0),
            speed=10
        )
        
        # Eğitim başlangıç paneli
        Entity(
            model='quad',
            scale=(0.6, 0.3),
            position=(0, 0.3),
            color=color.rgba(0, 0, 0, 0.8),
            parent=camera.ui
        )
        
        Text(
            text='Ticaretin İzinde - Eğitim Modu',
            scale=2,
            position=(0, 0.4),
            origin=(0, 0),
            color=color.yellow,
            parent=camera.ui
        )
        
        Text(
            text='Etrafınızdaki binaları ziyaret ederek ticaret dünyasını öğrenin.\nMarkette alım-satım yapın, bankada kredi çekin, ofiste işletmenizi yönetin.',
            scale=1.2,
            position=(0, 0.3),
            origin=(0, 0),
            color=color.white,
            parent=camera.ui
        )
        
        # Eğitimi atlama butonu
        Button(
            text='Eğitimi Atla',
            scale=(0.2, 0.05),
            position=(0, 0.2),
            color=color.orange,
            highlight_color=color.yellow,
            parent=camera.ui,
            on_click=Func(self.complete_tutorial)
        )
        
        # Dünya öğelerini kaydet
        self.world_elements = {
            'sky': self.sky,
            'ground': self.ground,
            'walls': self.walls,
            'buildings': self.tutorial_buildings,
            'signs': self.building_signs,
            'player': self.player_controller
        }
    
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
        """Ana oyun dünyasını oluştur"""
        # Oyun durumunu güncelle
        self.current_screen = 'game'
        
        # Gökyüzü
        self.sky = Sky()
        
        # Zemin
        self.ground = Entity(
            model='plane',
            scale=(1000, 1, 1000),
            color=color.green,
            texture='grass',
            collider='box'
        )
        
        # Şehir merkezi oluştur
        self.create_city_center()
        
        # Oyuncu kontrolcüsü
        self.player_controller = FirstPersonController(
            position=(0, 2, 0),
            speed=10
        )
        
        # Oyun UI'sını oluştur
        self.create_game_ui()
        
        # Varsayılan görevleri ekle
        self.assign_default_quests()
    
    def create_city_center(self):
        """Şehir merkezi oluştur"""
        # Ana yollar
        roads = [
            Entity(model='cube', scale=(100, 0.1, 10), position=(0, 0.05, 0), color=color.gray, texture='asphalt'),
            Entity(model='cube', scale=(10, 0.1, 100), position=(0, 0.05, 0), color=color.gray, texture='asphalt')
        ]
        
        # Binalar
        buildings = []
        building_positions = [
            # Market
            {'position': (20, 0, 20), 'scale': (15, 10, 15), 'color': color.azure, 'name': 'MARKET', 'type': 'market'},
            # Banka
            {'position': (-20, 0, -20), 'scale': (15, 12, 15), 'color': color.gold, 'name': 'BANKA', 'type': 'bank'},
            # Ofis
            {'position': (20, 0, -20), 'scale': (15, 8, 15), 'color': color.green, 'name': 'OFİS', 'type': 'office'},
            # Eğitim merkezi
            {'position': (-20, 0, 20), 'scale': (15, 14, 15), 'color': color.orange, 'name': 'EĞİTİM MERKEZİ', 'type': 'education'}
        ]
        
        # Binaları oluştur
        for building_data in building_positions:
            # Bina
            building = Entity(
                model='cube',
                position=(building_data['position'][0], building_data['scale'][1]/2, building_data['position'][2]),
                scale=building_data['scale'],
                color=building_data['color'],
                texture='brick',
                collider='box'
            )
            
            # Tabela
            sign = Entity(
                model='billboard',
                parent=building,
                position=(0, building_data['scale'][1]/2 + 1, 0),
                scale=3,
                color=color.white,
                billboard=True
            )
            
            Text(
                text=building_data['name'],
                parent=sign,
                scale=10,
                origin=(0, 0),
                color=color.black
            )
            
            # Kapı
            door = Entity(
                model='cube',
                parent=building,
                position=(0, -building_data['scale'][1]/2 + 1, building_data['scale'][2]/2 + 0.1),
                scale=(3, 5, 0.2),
                color=color.brown,
                collider='box'
            )
            
            # Giriş noktası
            entry_point = Entity(
                model='sphere',
                parent=building,
                position=(0, -building_data['scale'][1]/2 + 1, building_data['scale'][2]/2 + 2),
                scale=0.5,
                color=color.black,
                visible=False
            )
            
            # Binanın türünü ve giriş noktasını kaydet
            entry_point.building_type = building_data['type']
            
            # Etkileşim algılama için collider ekle
            trigger = Entity(
                parent=building,
                position=(0, -building_data['scale'][1]/2 + 1, building_data['scale'][2]/2 + 3),
                scale=(5, 5, 5),
                collider='box',
                visible=False
            )
            trigger.building_type = building_data['type']
            
            # Etkileşim için callback ekle
            def on_trigger_enter(trigger=trigger):
                self.interaction_target = trigger.building_type
                self.show_interaction_prompt(f"'{trigger.building_type.capitalize()}' binasına girmek için E tuşuna basın")
            
            def on_trigger_exit(trigger=trigger):
                if self.interaction_target == trigger.building_type:
                    self.interaction_target = None
                    self.hide_interaction_prompt()
            
            trigger.on_click = Func(on_trigger_enter)
            
            buildings.append({
                'entity': building,
                'sign': sign,
                'door': door,
                'entry_point': entry_point,
                'trigger': trigger,
                'type': building_data['type']
            })
        
        # Dekoratif ögeler
        decorations = []
        
        # Ağaçlar
        for _ in range(50):
            x = random.uniform(-100, 100)
            z = random.uniform(-100, 100)
            
            # Binaların yakınına ağaç koyma
            too_close = False
            for building in buildings:
                bx, _, bz = building['entity'].position
                if abs(x - bx) < 20 and abs(z - bz) < 20:
                    too_close = True
                    break
            
            if not too_close:
                tree = Entity(
                    model='cube',
                    position=(x, 2, z),
                    scale=(1, 4, 1),
                    color=color.brown
                )
                
                leaves = Entity(
                    model='sphere',
                    parent=tree,
                    position=(0, 2, 0),
                    scale=(3, 3, 3),
                    color=color.green
                )
                
                decorations.append((tree, leaves))
        
        # Banklar
        for _ in range(10):
            x = random.uniform(-50, 50)
            z = random.uniform(-50, 50)
            
            bench = Entity(
                model='cube',
                position=(x, 0.5, z),
                scale=(2, 0.5, 0.5),
                color=color.brown
            )
            
            decorations.append(bench)
        
        # Dünya öğelerini kaydet
        self.world_elements = {
            'sky': self.sky,
            'ground': self.ground,
            'roads': roads,
            'buildings': buildings,
            'decorations': decorations,
            'player': self.player_controller
        }
    
    def create_game_ui(self):
        """Oyun içi UI oluştur"""
        # Oyuncu bilgi paneli
        self.info_panel = Entity(
            model='quad',
            scale=(0.3, 0.15),
            position=(-0.6, 0.4),
            color=color.rgba(0, 0, 0, 0.7),
            parent=camera.ui
        )
        
        # Oyuncu bilgileri
        self.player_name = Text(
            text=f"İsim: {self.game_state['player']['company']['name']}",
            position=(-0.6, 0.45),
            origin=(0, 0),
            color=color.white,
            parent=camera.ui
        )
        
        self.player_money = Text(
            text=f"Para: {self.game_state['player']['money']} ₺",
            position=(-0.6, 0.4),
            origin=(0, 0),
            color=color.white,
            parent=camera.ui
        )
        
        self.player_level = Text(
            text=f"Seviye: {self.game_state['player']['level']}",
            position=(-0.6, 0.35),
            origin=(0, 0),
            color=color.white,
            parent=camera.ui
        )
        
        # Tarih bilgisi
        self.date_panel = Entity(
            model='quad',
            scale=(0.2, 0.05),
            position=(0, 0.45),
            color=color.rgba(0, 0, 0, 0.7),
            parent=camera.ui
        )
        
        self.date_text = Text(
            text=f"Gün: {self.game_state['time']['day']} | Ay: {self.game_state['time']['month']} | Yıl: {self.game_state['time']['year']}",
            position=(0, 0.45),
            origin=(0, 0),
            color=color.white,
            parent=camera.ui
        )
        
        # Görev paneli
        self.quest_panel = Entity(
            model='quad',
            scale=(0.3, 0.25),
            position=(0.6, 0.35),
            color=color.rgba(0, 0, 0, 0.7),
            parent=camera.ui
        )
        
        self.quest_title = Text(
            text="GÖREVLER",
            position=(0.6, 0.45),
            origin=(0, 0),
            color=color.gold,
            parent=camera.ui
        )
        
        self.quest_list_entity = Entity(
            parent=camera.ui,
            position=(0.6, 0.4)
        )
        
        # Etkileşim prompt'u
        self.interaction_prompt = Text(
            text="",
            position=(0, -0.4),
            origin=(0, 0),
            color=color.white,
            parent=camera.ui,
            visible=False
        )
        
        # UI elemanlarını kaydet
        self.ui_elements['game'] = [
            self.info_panel, self.player_name, self.player_money, self.player_level,
            self.date_panel, self.date_text,
            self.quest_panel, self.quest_title, self.quest_list_entity,
            self.interaction_prompt
        ]
        
        # Görev listesini güncelle
        self.update_quest_list()
    
    def update_quest_list(self):
        """Görev listesini güncelle"""
        # Önceki görev metinlerini temizle
        for child in self.quest_list_entity.children:
            destroy(child)
        
        # Aktif görevleri göster
        y_position = 0
        for i, quest_id in enumerate(self.game_state['active_quests']):
            quest_category = None
            quest_data = None
            
            # Görev kategorisini ve verisini bul
            for category, quests in self.quests.items():
                for quest in quests:
                    if quest['id'] == quest_id:
                        quest_category = category
                        quest_data = quest
                        break
                if quest_data:
                    break
            
            if quest_data:
                quest_text = Text(
                    text=f"{quest_data['title']}: {quest_data['description']}",
                    position=(0, y_position),
                    origin=(0, 0),
                    color=color.white,
                    parent=self.quest_list_entity,
                    scale=0.7
                )
                y_position -= 0.05
    
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
        """Etkileşim prompt'unu göster"""
        self.interaction_prompt.text = text
        self.interaction_prompt.visible = True
    
    def hide_interaction_prompt(self):
        """Etkileşim prompt'unu gizle"""
        self.interaction_prompt.visible = False
    
    def update(self):
        """Oyun güncelleme fonksiyonu"""
        if self.current_screen == 'game':
            # Tuş basışlarını kontrol et
            if held_keys['e'] and self.interaction_target:
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
        """Görev tamamlandı bildirimi göster"""
        # Bildirim paneli
        panel = Entity(
            model='quad',
            scale=(0.5, 0.3),
            position=(0, 0),
            color=color.rgba(0, 0, 0, 0.8),
            parent=camera.ui
        )
        
        # Başlık
        title = Text(
            text="GÖREV TAMAMLANDI!",
            position=(0, 0.1),
            origin=(0, 0),
            color=color.gold,
            parent=panel
        )
        
        # Görev bilgisi
        quest_text = Text(
            text=f"{quest_data['title']}\n{quest_data['description']}",
            position=(0, 0),
            origin=(0, 0),
            color=color.white,
            parent=panel
        )
        
        # Ödül bilgisi
        reward_text = Text(
            text=f"Ödül: {quest_data['reward'].get('money', 0)} ₺ | {quest_data['reward'].get('exp', 0)} XP",
            position=(0, -0.1),
            origin=(0, 0),
            color=color.green,
            parent=panel
        )
        
        # 3 saniye sonra bildirim panelini kapat
        def close_panel():
            destroy(panel)
        
        invoke(close_panel, delay=3)
    
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
            self.player_level.text = f"Seviye: {self.game_state['player']['level']}"
    
    def show_level_up(self):
        """Seviye atlama bildirimi göster"""
        # Bildirim paneli
        panel = Entity(
            model='quad',
            scale=(0.5, 0.3),
            position=(0, 0),
            color=color.rgba(0, 0, 0, 0.8),
            parent=camera.ui
        )
        
        # Başlık
        title = Text(
            text="SEVİYE ATLAMA!",
            position=(0, 0.1),
            origin=(0, 0),
            color=color.gold,
            parent=panel
        )
        
        # Seviye bilgisi
        level_text = Text(
            text=f"Tebrikler! Seviye {self.game_state['player']['level']} oldunuz.",
            position=(0, 0),
            origin=(0, 0),
            color=color.white,
            parent=panel
        )
        
        # Avantaj bilgisi
        advantage_text = Text(
            text="Yeni seviyede ticaret kabiliyetiniz ve ürün çeşitliliğiniz arttı!",
            position=(0, -0.1),
            origin=(0, 0),
            color=color.green,
            parent=panel
        )
        
        # 3 saniye sonra bildirim panelini kapat
        def close_panel():
            destroy(panel)
        
        invoke(close_panel, delay=3)

# Eğer doğrudan çalıştırılıyorsa oyunu başlat
if __name__ == '__main__':
    game = TicaretinIzinde3D() 