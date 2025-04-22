from ursina import Ursina, Entity, Text, Button, Func, color, camera, mouse, destroy, window, Vec3, Audio, application
from ursina.prefabs.first_person_controller import FirstPersonController
import random
import json
import os
from datetime import datetime

class FinanceEducator:
    def __init__(self):
        # Ursina uygulamasını başlat
        self.app = Ursina()
        
        # Pencere ayarları
        window.title = 'FinAsis - Finansal Eğitim Oyunu'
        window.borderless = False
        window.fullscreen = False
        window.exit_button.visible = True
        window.fps_counter.enabled = True
        
        # Oyuncu verileri
        self.player = {
            'name': 'Oyuncu',
            'age_group': 'adult',  # child, teen, adult, senior
            'character': 'businessman',  # businessman, student, teacher, retiree
            'level': 1,
            'exp': 0,
            'money': 10000,
            'knowledge': {
                'accounting': 1,
                'investing': 1,
                'budgeting': 1,
                'taxes': 1,
                'banking': 1
            },
            'completed_quests': [],
            'inventory': {},
            'tutorial_completed': False
        }
        
        # Oyun durumu
        self.game_state = 'main_menu'  # main_menu, character_select, game, quest, learning, tutorial
        
        # UI elemanları
        self.ui_elements = {}
        
        # Ses efektleri
        self.sounds = {
            'click': Audio('click', autoplay=False, loop=False),
            'success': Audio('success', autoplay=False, loop=False),
            'fail': Audio('fail', autoplay=False, loop=False)
        }
        
        # Ana menüyü oluştur
        self.create_main_menu()
        
        # Oyunu başlat
        self.app.run()
    
    def create_main_menu(self):
        """Ana menüyü oluştur"""
        # Arka plan
        self.background = Entity(
            model='quad',
            scale=(2, 1),
            color=color.rgb(50, 50, 100),
            parent=camera.ui
        )
        
        # Başlık
        self.title = Text(
            text='FinAsis - Finansal Eğitim Oyunu',
            scale=3,
            y=0.4,
            origin=(0, 0),
            parent=camera.ui
        )
        
        # Yaş grubu seçimi
        self.age_group_text = Text(
            text='Yaş grubunuzu seçin:',
            scale=1.5,
            y=0.25,
            origin=(0, 0),
            parent=camera.ui
        )
        
        # Yaş grubu butonları
        self.age_buttons = []
        age_groups = ['Çocuk (5-12)', 'Genç (13-18)', 'Yetişkin (19-65)', 'Yaşlı (65+)']
        age_keys = ['child', 'teen', 'adult', 'senior']
        
        for i, (age_text, age_key) in enumerate(zip(age_groups, age_keys)):
            btn = Button(
                text=age_text,
                scale=(0.3, 0.05),
                position=(0, 0.15 - i*0.06),
                color=color.azure,
                highlight_color=color.light_blue,
                parent=camera.ui,
                on_click=Func(self.select_age_group, age_key)
            )
            self.age_buttons.append(btn)
        
        # Başlat butonu
        self.start_button = Button(
            text='Oyuna Başla',
            scale=(0.3, 0.05),
            position=(0, -0.2),
            color=color.green,
            highlight_color=color.lime,
            parent=camera.ui,
            on_click=Func(self.start_character_selection)
        )
        
        # Çıkış butonu
        self.exit_button = Button(
            text='Çıkış',
            scale=(0.3, 0.05),
            position=(0, -0.3),
            color=color.red,
            highlight_color=color.orange,
            parent=camera.ui,
            on_click=Func(application.quit)
        )
        
        # UI öğelerini kaydet
        self.ui_elements['main_menu'] = [
            self.background, self.title, self.age_group_text,
            *self.age_buttons, self.start_button, self.exit_button
        ]
    
    def select_age_group(self, age_group):
        """Yaş grubunu seç"""
        self.player['age_group'] = age_group
        
        # Butonları güncelle
        for i, (button, key) in enumerate(zip(self.age_buttons, ['child', 'teen', 'adult', 'senior'])):
            if key == age_group:
                button.color = color.green
            else:
                button.color = color.azure
        
        # Ses efekti
        self.sounds['click'].play()
    
    def start_character_selection(self):
        """Karakter seçim ekranına geç"""
        # Ana menüyü temizle
        for element in self.ui_elements['main_menu']:
            destroy(element)
        
        # Oyun durumunu güncelle
        self.game_state = 'character_select'
        
        # Karakter seçim ekranını oluştur
        self.create_character_selection()
    
    def create_character_selection(self):
        """Karakter seçim ekranını oluştur"""
        # Arka plan
        self.background = Entity(
            model='quad',
            scale=(2, 1),
            color=color.rgb(50, 100, 50),
            parent=camera.ui
        )
        
        # Başlık
        self.title = Text(
            text='Karakterinizi Seçin',
            scale=3,
            y=0.4,
            origin=(0, 0),
            parent=camera.ui
        )
        
        # Karakter butonları
        self.character_buttons = []
        characters = [
            ('İş İnsanı', 'businessman', 'İş dünyasını ve yatırımları öğrenin'),
            ('Öğrenci', 'student', 'Temel bütçeleme ve tasarruf öğrenin'),
            ('Öğretmen', 'teacher', 'Finansal bilgileri başkalarına aktarın'),
            ('Emekli', 'retiree', 'Emeklilik planlaması ve servet yönetimi')
        ]
        
        for i, (char_name, char_key, char_desc) in enumerate(characters):
            # Karakter butonu
            btn = Button(
                text=char_name,
                scale=(0.3, 0.05),
                position=(-0.3, 0.2 - i*0.15),
                color=color.azure,
                highlight_color=color.light_blue,
                parent=camera.ui,
                on_click=Func(self.select_character, char_key)
            )
            
            # Karakter açıklaması
            desc = Text(
                text=char_desc,
                scale=1,
                position=(0.1, 0.2 - i*0.15),
                origin=(-0.5, 0),
                parent=camera.ui
            )
            
            self.character_buttons.append((btn, desc))
        
        # Başlat butonu
        self.start_game_button = Button(
            text='Oyunu Başlat',
            scale=(0.3, 0.05),
            position=(0, -0.3),
            color=color.green,
            highlight_color=color.lime,
            parent=camera.ui,
            on_click=Func(self.start_game)
        )
        
        # Geri butonu
        self.back_button = Button(
            text='Geri',
            scale=(0.3, 0.05),
            position=(0, -0.4),
            color=color.red,
            highlight_color=color.orange,
            parent=camera.ui,
            on_click=Func(self.go_back_to_main_menu)
        )
        
        # UI öğelerini kaydet
        self.ui_elements['character_select'] = [
            self.background, self.title,
            *[item for sublist in self.character_buttons for item in sublist],
            self.start_game_button, self.back_button
        ]
    
    def select_character(self, character):
        """Karakteri seç"""
        self.player['character'] = character
        
        # Butonları güncelle
        for btn, desc in self.character_buttons:
            if btn.text.lower() in character:
                btn.color = color.green
            else:
                btn.color = color.azure
        
        # Ses efekti
        self.sounds['click'].play()
    
    def go_back_to_main_menu(self):
        """Ana menüye dön"""
        # Karakter seçim ekranını temizle
        for element in self.ui_elements['character_select']:
            destroy(element)
        
        # Oyun durumunu güncelle
        self.game_state = 'main_menu'
        
        # Ana menüyü tekrar oluştur
        self.create_main_menu()
    
    def start_game(self):
        """Oyunu başlat"""
        # Karakter seçim ekranını temizle
        for element in self.ui_elements['character_select']:
            destroy(element)
        
        # Oyun durumunu güncelle
        self.game_state = 'game'
        
        # Eğer daha önce eğitim tamamlanmadıysa, eğitimi başlat
        if not self.player['tutorial_completed']:
            self.start_tutorial()
        else:
            # Ana oyun dünyasını oluştur
            self.create_game_world()
    
    def start_tutorial(self):
        """Eğitim modunu başlat"""
        # Oyun durumunu güncelle
        self.game_state = 'tutorial'
        
        # Eğitim dünyasını oluştur
        self.create_tutorial_world()
    
    def create_tutorial_world(self):
        """Eğitim dünyasını oluştur"""
        # 3D dünya
        self.ground = Entity(
            model='plane',
            scale=(100, 1, 100),
            color=color.green,
            texture='grass',
            collider='box'
        )
        
        # Duvarlar
        self.walls = [
            Entity(model='cube', scale=(1, 5, 100), position=(-50, 2.5, 0), color=color.light_gray, collider='box'),
            Entity(model='cube', scale=(1, 5, 100), position=(50, 2.5, 0), color=color.light_gray, collider='box'),
            Entity(model='cube', scale=(100, 5, 1), position=(0, 2.5, 50), color=color.light_gray, collider='box'),
            Entity(model='cube', scale=(100, 5, 1), position=(0, 2.5, -50), color=color.light_gray, collider='box')
        ]
        
        # Eğitim noktaları
        self.tutorial_points = [
            Entity(model='sphere', scale=1, position=(10, 1, 10), color=color.red, collider='sphere'),
            Entity(model='sphere', scale=1, position=(-10, 1, -10), color=color.blue, collider='sphere'),
            Entity(model='sphere', scale=1, position=(10, 1, -10), color=color.yellow, collider='sphere'),
            Entity(model='sphere', scale=1, position=(-10, 1, 10), color=color.green, collider='sphere')
        ]
        
        # Eğitim metinleri
        self.tutorial_texts = [
            Text3D(text='Muhasebe', position=(10, 2, 10), scale=2),
            Text3D(text='Yatırım', position=(-10, 2, -10), scale=2),
            Text3D(text='Bütçeleme', position=(10, 2, -10), scale=2),
            Text3D(text='Bankacılık', position=(-10, 2, 10), scale=2)
        ]
        
        # Oyuncu
        self.player_controller = FirstPersonController()
        
        # Eğitim UI'ı
        self.tutorial_panel = Panel(
            scale=(0.6, 0.2),
            position=(0, 0.4),
            parent=camera.ui
        )
        
        self.tutorial_text = Text(
            text="Finansal eğitim dünyasına hoş geldiniz! Renkli kürelere yaklaşarak bilgi noktalarını keşfedin.",
            parent=self.tutorial_panel,
            origin=(0, 0),
            scale=1
        )
        
        # Eğitim tamamlama butonu
        self.finish_tutorial_button = Button(
            text='Eğitimi Geç',
            scale=(0.2, 0.05),
            position=(0, -0.4),
            color=color.azure,
            highlight_color=color.light_blue,
            parent=camera.ui,
            on_click=Func(self.complete_tutorial)
        )
        
        # UI öğelerini kaydet
        self.ui_elements['tutorial'] = [
            self.tutorial_panel, self.tutorial_text, self.finish_tutorial_button
        ]
        
        # Dünya öğelerini kaydet
        self.world_elements = [
            self.ground, *self.walls, *self.tutorial_points, *self.tutorial_texts, self.player_controller
        ]
    
    def complete_tutorial(self):
        """Eğitimi tamamla"""
        # Eğitim tamamlandı olarak işaretle
        self.player['tutorial_completed'] = True
        
        # Ses efekti
        self.sounds['success'].play()
        
        # Dünya ve UI öğelerini temizle
        for element in self.world_elements:
            destroy(element)
        
        for element in self.ui_elements['tutorial']:
            destroy(element)
        
        # Ana oyun dünyasını oluştur
        self.create_game_world()
    
    def create_game_world(self):
        """Ana oyun dünyasını oluştur"""
        # Oyun durumunu güncelle
        self.game_state = 'game'
        
        # 3D dünya
        self.ground = Entity(
            model='plane',
            scale=(100, 1, 100),
            color=color.green,
            texture='grass',
            collider='box'
        )
        
        # Binalar
        self.buildings = [
            Entity(model='cube', scale=(10, 10, 10), position=(20, 5, 20), color=color.light_gray, collider='box', texture='brick'),
            Entity(model='cube', scale=(10, 15, 10), position=(-20, 7.5, -20), color=color.light_gray, collider='box', texture='brick'),
            Entity(model='cube', scale=(10, 8, 10), position=(20, 4, -20), color=color.light_gray, collider='box', texture='brick'),
            Entity(model='cube', scale=(10, 12, 10), position=(-20, 6, 20), color=color.light_gray, collider='box', texture='brick')
        ]
        
        # Bina tabelaları
        self.building_signs = [
            Text3D(text='BANKA', position=(20, 11, 20), scale=2),
            Text3D(text='BORSA', position=(-20, 15.5, -20), scale=2),
            Text3D(text='VERGİ DAİRESİ', position=(20, 9, -20), scale=2),
            Text3D(text='MUHASEBE', position=(-20, 13, 20), scale=2)
        ]
        
        # Oyuncu
        self.player_controller = FirstPersonController()
        
        # Görev UI'ı
        self.quest_panel = Panel(
            scale=(0.3, 0.5),
            position=(0.6, 0),
            parent=camera.ui,
            visible=False
        )
        
        self.quest_title = Text(
            text="GÖREVLER",
            parent=self.quest_panel,
            position=(0, 0.2),
            origin=(0, 0),
            scale=1.5
        )
        
        self.quest_list = []
        
        # Bilgi UI'ı
        self.info_panel = Panel(
            scale=(0.3, 0.2),
            position=(-0.6, 0.3),
            parent=camera.ui
        )
        
        self.player_info = Text(
            text=f"İsim: {self.player['name']}\nSeviye: {self.player['level']}\nPara: {self.player['money']} ₺",
            parent=self.info_panel,
            origin=(0, 0),
            scale=1
        )
        
        # Gösterge UI'ı
        self.hud_panel = Panel(
            scale=(0.3, 0.1),
            position=(0, 0.45),
            parent=camera.ui
        )
        
        self.hud_text = Text(
            text="Binaları keşfedin ve finansal görevleri tamamlayın!",
            parent=self.hud_panel,
            origin=(0, 0),
            scale=0.7
        )
        
        # Görev butonları
        self.quest_button = Button(
            text='Görevler',
            scale=(0.1, 0.05),
            position=(0.6, 0.4),
            color=color.azure,
            highlight_color=color.light_blue,
            parent=camera.ui,
            on_click=Func(self.toggle_quest_panel)
        )
        
        # UI öğelerini kaydet
        self.ui_elements['game'] = [
            self.quest_panel, self.quest_title, self.info_panel, 
            self.player_info, self.hud_panel, self.hud_text, self.quest_button
        ]
        
        # Dünya öğelerini kaydet
        self.world_elements = [
            self.ground, *self.buildings, *self.building_signs, self.player_controller
        ]
        
        # İlk görevi oluştur
        self.create_first_quest()
    
    def toggle_quest_panel(self):
        """Görev panelini aç/kapat"""
        self.quest_panel.visible = not self.quest_panel.visible
        
        # Ses efekti
        self.sounds['click'].play()
    
    def create_first_quest(self):
        """İlk görevi oluştur"""
        # Yaş grubuna göre uygun görev
        if self.player['age_group'] == 'child':
            quest_title = "Para Biriktirme"
            quest_desc = "Bankaya git ve ilk birikim hesabını aç."
            quest_reward = 500
        elif self.player['age_group'] == 'teen':
            quest_title = "Bütçe Planı"
            quest_desc = "Aylık harcama bütçesi oluştur."
            quest_reward = 1000
        elif self.player['age_group'] == 'adult':
            quest_title = "Yatırım"
            quest_desc = "Borsayı ziyaret et ve ilk hisse senedini al."
            quest_reward = 2000
        else:  # senior
            quest_title = "Emeklilik Planı"
            quest_desc = "Emeklilik gelir stratejisini oluştur."
            quest_reward = 3000
        
        # Görev metni
        quest_text = Text(
            text=f"{quest_title}\n{quest_desc}\nÖdül: {quest_reward} ₺",
            parent=self.quest_panel,
            position=(0, 0),
            origin=(0, 0),
            scale=0.8
        )
        
        self.quest_list.append({
            'title': quest_title,
            'description': quest_desc,
            'reward': quest_reward,
            'completed': False,
            'ui_element': quest_text
        })

# Ana karakter sınıfı
class Text3D(Entity):
    def __init__(self, text='', **kwargs):
        super().__init__()
        self.text_entity = Text(parent=self, billboard=True, **kwargs)

# Panel sınıfı
class Panel(Entity):
    def __init__(self, **kwargs):
        super().__init__(
            model='quad',
            color=color.rgba(0, 0, 0, 0.7),
            **kwargs
        )

# Oyunu başlat
if __name__ == '__main__':
    FinanceEducator() 