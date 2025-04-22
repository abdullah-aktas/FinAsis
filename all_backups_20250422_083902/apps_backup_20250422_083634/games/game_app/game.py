import pygame
import random
import json
from datetime import datetime
import math

# Oyun sabitleri
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

# Renkler
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
LIGHT_BLUE = (100, 149, 237)
DARK_GRAY = (64, 64, 64)

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Ticaretin İzinde")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Oyun durumu
        self.game_state = {
            'player': {
                'money': 10000,  # Başlangıç parası
                'inventory': {},  # Envanter
                'company': {
                    'name': '',
                    'level': 1,
                    'experience': 0,
                    'reputation': 0,
                    'type': '',  # perakende, toptan, üretim
                    'location': '',  # şehir
                    'employees': 0,
                    'storage_capacity': 100
                },
                'skills': {
                    'trading': 1,
                    'accounting': 1,
                    'management': 1
                }
            },
            'market': {
                'products': self.load_products(),
                'prices': {},
                'demand': {}
            },
            'time': {
                'day': 1,
                'month': 1,
                'year': 2024
            }
        }
        
        # UI elemanları
        self.ui_elements = {}
        self.current_screen = 'main_menu'  # main_menu, company_setup, game
        self.init_ui()
        
        # Şirket kurulum değişkenleri
        self.company_name = ''
        self.company_type = ''
        self.company_location = ''
        self.starting_capital = 10000
        self.input_active = False
        self.active_input_field = None
        
    def load_products(self):
        """Ürün veritabanını yükle"""
        return {
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
        
    def init_ui(self):
        """UI elemanlarını başlat"""
        # Ana menü butonları
        self.ui_elements['main_menu'] = {
            'start': pygame.Rect(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 - 50, 200, 50),
            'load': pygame.Rect(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 20, 200, 50),
            'quit': pygame.Rect(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 90, 200, 50)
        }
        
        # Şirket kurulum ekranı
        self.ui_elements['company_setup'] = {
            'title': pygame.Rect(SCREEN_WIDTH//2 - 200, 50, 400, 50),
            'name_label': pygame.Rect(SCREEN_WIDTH//2 - 200, 150, 200, 30),
            'name_input': pygame.Rect(SCREEN_WIDTH//2 - 200, 190, 400, 40),
            'type_label': pygame.Rect(SCREEN_WIDTH//2 - 200, 250, 200, 30),
            'type_perakende': pygame.Rect(SCREEN_WIDTH//2 - 200, 290, 130, 40),
            'type_toptan': pygame.Rect(SCREEN_WIDTH//2 - 50, 290, 130, 40),
            'type_uretim': pygame.Rect(SCREEN_WIDTH//2 + 100, 290, 130, 40),
            'location_label': pygame.Rect(SCREEN_WIDTH//2 - 200, 350, 200, 30),
            'location_input': pygame.Rect(SCREEN_WIDTH//2 - 200, 390, 400, 40),
            'capital_label': pygame.Rect(SCREEN_WIDTH//2 - 200, 450, 200, 30),
            'capital_slider': pygame.Rect(SCREEN_WIDTH//2 - 200, 490, 400, 20),
            'capital_value': pygame.Rect(SCREEN_WIDTH//2 - 200, 520, 400, 30),
            'start_button': pygame.Rect(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT - 100, 200, 50),
            'back_button': pygame.Rect(50, SCREEN_HEIGHT - 100, 100, 50)
        }
        
    def handle_events(self):
        """Oyun olaylarını işle"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_click(event.pos)
            elif event.type == pygame.KEYDOWN and self.input_active:
                self.handle_keydown(event)
                
    def handle_click(self, pos):
        """Tıklama olaylarını işle"""
        if self.current_screen == 'main_menu':
            # Ana menü tıklamaları
            if self.ui_elements['main_menu']['start'].collidepoint(pos):
                self.current_screen = 'company_setup'
            elif self.ui_elements['main_menu']['load'].collidepoint(pos):
                self.load_game()
            elif self.ui_elements['main_menu']['quit'].collidepoint(pos):
                self.running = False
                
        elif self.current_screen == 'company_setup':
            # Şirket kurulum ekranı tıklamaları
            if self.ui_elements['company_setup']['name_input'].collidepoint(pos):
                self.input_active = True
                self.active_input_field = 'name'
            elif self.ui_elements['company_setup']['location_input'].collidepoint(pos):
                self.input_active = True
                self.active_input_field = 'location'
            elif self.ui_elements['company_setup']['type_perakende'].collidepoint(pos):
                self.company_type = 'perakende'
            elif self.ui_elements['company_setup']['type_toptan'].collidepoint(pos):
                self.company_type = 'toptan'
            elif self.ui_elements['company_setup']['type_uretim'].collidepoint(pos):
                self.company_type = 'uretim'
            elif self.ui_elements['company_setup']['capital_slider'].collidepoint(pos):
                # Slider değerini güncelle
                rel_x = pos[0] - self.ui_elements['company_setup']['capital_slider'].x
                self.starting_capital = int(5000 + (rel_x / 400) * 45000)  # 5000-50000 arası
            elif self.ui_elements['company_setup']['start_button'].collidepoint(pos):
                if self.validate_company_setup():
                    self.start_game()
            elif self.ui_elements['company_setup']['back_button'].collidepoint(pos):
                self.current_screen = 'main_menu'
            else:
                self.input_active = False
                self.active_input_field = None
                
        elif self.current_screen == 'game':
            # Oyun ekranı tıklamaları
            for product in self.game_state['market']['prices'].keys():
                # Alım butonu kontrolü
                if f'buy_{product}' in self.ui_elements and self.ui_elements[f'buy_{product}'].collidepoint(pos):
                    self.buy_product(product)
                # Satım butonu kontrolü
                elif f'sell_{product}' in self.ui_elements and self.ui_elements[f'sell_{product}'].collidepoint(pos):
                    self.sell_product(product)
                
    def handle_keydown(self, event):
        """Klavye girişlerini işle"""
        if self.active_input_field == 'name':
            if event.key == pygame.K_RETURN:
                self.input_active = False
                self.active_input_field = None
            elif event.key == pygame.K_BACKSPACE:
                self.company_name = self.company_name[:-1]
            else:
                if len(self.company_name) < 20:  # Maksimum 20 karakter
                    self.company_name += event.unicode
                    
        elif self.active_input_field == 'location':
            if event.key == pygame.K_RETURN:
                self.input_active = False
                self.active_input_field = None
            elif event.key == pygame.K_BACKSPACE:
                self.company_location = self.company_location[:-1]
            else:
                if len(self.company_location) < 20:  # Maksimum 20 karakter
                    self.company_location += event.unicode
                    
    def validate_company_setup(self):
        """Şirket kurulum bilgilerini doğrula"""
        if not self.company_name:
            print("Şirket adı boş olamaz!")
            return False
        if not self.company_type:
            print("Şirket türü seçilmedi!")
            return False
        if not self.company_location:
            print("Şirket konumu boş olamaz!")
            return False
        return True
        
    def start_game(self):
        """Yeni oyun başlat"""
        # Şirket bilgilerini kaydet
        self.game_state['player']['company']['name'] = self.company_name
        self.game_state['player']['company']['type'] = self.company_type
        self.game_state['player']['company']['location'] = self.company_location
        self.game_state['player']['money'] = self.starting_capital
        
        # Oyun ekranına geç
        self.current_screen = 'game'
        
    def load_game(self):
        """Kayıtlı oyunu yükle"""
        try:
            with open('save_game.json', 'r') as f:
                self.game_state = json.load(f)
            self.current_screen = 'game'
        except FileNotFoundError:
            print("Kayıtlı oyun bulunamadı!")
            
    def save_game(self):
        """Oyunu kaydet"""
        with open('save_game.json', 'w') as f:
            json.dump(self.game_state, f)
            
    def update(self):
        """Oyun durumunu güncelle"""
        if self.current_screen == 'game':
            # Pazar fiyatlarını güncelle
            self.update_market_prices()
            
            # Zamanı ilerlet
            self.update_time()
        
    def update_market_prices(self):
        """Pazar fiyatlarını güncelle"""
        for category, products in self.game_state['market']['products'].items():
            for product, data in products.items():
                # Temel fiyat üzerine rastgele değişim
                change = random.uniform(-0.1, 0.1)
                current_price = data['base_price'] * (1 + change)
                self.game_state['market']['prices'][product] = current_price
                
    def update_time(self):
        """Oyun zamanını güncelle"""
        self.game_state['time']['day'] += 1
        if self.game_state['time']['day'] > 30:
            self.game_state['time']['day'] = 1
            self.game_state['time']['month'] += 1
            if self.game_state['time']['month'] > 12:
                self.game_state['time']['month'] = 1
                self.game_state['time']['year'] += 1
                
    def draw(self):
        """Oyun ekranını çiz"""
        self.screen.fill(WHITE)
        
        if self.current_screen == 'main_menu':
            self.draw_main_menu()
        elif self.current_screen == 'company_setup':
            self.draw_company_setup()
        elif self.current_screen == 'game':
            self.draw_game()
            
        pygame.display.flip()
        
    def draw_main_menu(self):
        """Ana menüyü çiz"""
        # Başlık
        font = pygame.font.Font(None, 72)
        title = font.render("Ticaretin İzinde", True, BLACK)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 150))
        self.screen.blit(title, title_rect)
        
        # Ana menü butonları
        for button_name, button_rect in self.ui_elements['main_menu'].items():
            pygame.draw.rect(self.screen, BLUE, button_rect)
            font = pygame.font.Font(None, 36)
            text = font.render(button_name.capitalize(), True, WHITE)
            text_rect = text.get_rect(center=button_rect.center)
            self.screen.blit(text, text_rect)
            
    def draw_company_setup(self):
        """Şirket kurulum ekranını çiz"""
        # Başlık
        font = pygame.font.Font(None, 48)
        title = font.render("Şirket Kurulumu", True, BLACK)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 75))
        self.screen.blit(title, title_rect)
        
        # Şirket adı
        font = pygame.font.Font(None, 24)
        name_label = font.render("Şirket Adı:", True, BLACK)
        self.screen.blit(name_label, (SCREEN_WIDTH//2 - 200, 150))
        
        pygame.draw.rect(self.screen, LIGHT_BLUE if self.active_input_field == 'name' else GRAY, 
                        self.ui_elements['company_setup']['name_input'])
        name_text = font.render(self.company_name, True, BLACK)
        self.screen.blit(name_text, (SCREEN_WIDTH//2 - 190, 200))
        
        # Şirket türü
        type_label = font.render("Şirket Türü:", True, BLACK)
        self.screen.blit(type_label, (SCREEN_WIDTH//2 - 200, 250))
        
        # Şirket türü butonları
        type_colors = {
            'perakende': GREEN if self.company_type == 'perakende' else GRAY,
            'toptan': GREEN if self.company_type == 'toptan' else GRAY,
            'uretim': GREEN if self.company_type == 'uretim' else GRAY
        }
        
        pygame.draw.rect(self.screen, type_colors['perakende'], 
                        self.ui_elements['company_setup']['type_perakende'])
        pygame.draw.rect(self.screen, type_colors['toptan'], 
                        self.ui_elements['company_setup']['type_toptan'])
        pygame.draw.rect(self.screen, type_colors['uretim'], 
                        self.ui_elements['company_setup']['type_uretim'])
        
        type_texts = ['Perakende', 'Toptan', 'Üretim']
        type_rects = ['type_perakende', 'type_toptan', 'type_uretim']
        
        for i, (text, rect_name) in enumerate(zip(type_texts, type_rects)):
            rect = self.ui_elements['company_setup'][rect_name]
            text_surface = font.render(text, True, BLACK)
            text_rect = text_surface.get_rect(center=rect.center)
            self.screen.blit(text_surface, text_rect)
            
        # Şirket konumu
        location_label = font.render("Şirket Konumu:", True, BLACK)
        self.screen.blit(location_label, (SCREEN_WIDTH//2 - 200, 350))
        
        pygame.draw.rect(self.screen, LIGHT_BLUE if self.active_input_field == 'location' else GRAY, 
                        self.ui_elements['company_setup']['location_input'])
        location_text = font.render(self.company_location, True, BLACK)
        self.screen.blit(location_text, (SCREEN_WIDTH//2 - 190, 400))
        
        # Başlangıç sermayesi
        capital_label = font.render("Başlangıç Sermayesi:", True, BLACK)
        self.screen.blit(capital_label, (SCREEN_WIDTH//2 - 200, 450))
        
        pygame.draw.rect(self.screen, GRAY, self.ui_elements['company_setup']['capital_slider'])
        slider_pos = ((self.starting_capital - 5000) / 45000) * 400
        pygame.draw.rect(self.screen, BLUE, 
                        (SCREEN_WIDTH//2 - 200 + slider_pos - 5, 485, 10, 30))
        
        capital_text = font.render(f"{self.starting_capital:,} TL", True, BLACK)
        self.screen.blit(capital_text, (SCREEN_WIDTH//2 - 50, 520))
        
        # Başlat ve Geri butonları
        pygame.draw.rect(self.screen, GREEN, self.ui_elements['company_setup']['start_button'])
        start_text = font.render("Oyunu Başlat", True, BLACK)
        start_rect = start_text.get_rect(center=self.ui_elements['company_setup']['start_button'].center)
        self.screen.blit(start_text, start_rect)
        
        pygame.draw.rect(self.screen, RED, self.ui_elements['company_setup']['back_button'])
        back_text = font.render("Geri", True, BLACK)
        back_rect = back_text.get_rect(center=self.ui_elements['company_setup']['back_button'].center)
        self.screen.blit(back_text, back_rect)
        
    def draw_game(self):
        """Oyun ekranını çiz"""
        # Arka plan
        self.screen.fill(WHITE)
        
        # Üst bilgi çubuğu
        pygame.draw.rect(self.screen, BLUE, (0, 0, SCREEN_WIDTH, 60))
        
        # Şirket bilgileri
        font = pygame.font.Font(None, 24)
        company_info = [
            f"Şirket: {self.game_state['player']['company']['name']}",
            f"Tür: {self.game_state['player']['company']['type']}",
            f"Konum: {self.game_state['player']['company']['location']}",
            f"Para: {self.game_state['player']['money']:,} TL",
            f"Seviye: {self.game_state['player']['company']['level']}"
        ]
        
        for i, info in enumerate(company_info):
            text = font.render(info, True, WHITE)
            self.screen.blit(text, (20 + i * 250, 20))
        
        # Tarih bilgisi
        date_text = font.render(
            f"Gün: {self.game_state['time']['day']} " +
            f"Ay: {self.game_state['time']['month']} " +
            f"Yıl: {self.game_state['time']['year']}", 
            True, WHITE
        )
        self.screen.blit(date_text, (SCREEN_WIDTH - 300, 20))
        
        # Ana oyun alanı
        # Sol panel - Envanter
        pygame.draw.rect(self.screen, LIGHT_BLUE, (20, 80, 300, SCREEN_HEIGHT - 100))
        inventory_title = font.render("ENVANTER", True, BLACK)
        self.screen.blit(inventory_title, (30, 90))
        
        # Envanter listesi
        y_pos = 120
        for item, amount in self.game_state['player']['inventory'].items():
            item_text = font.render(f"{item}: {amount}", True, BLACK)
            self.screen.blit(item_text, (30, y_pos))
            y_pos += 30
        
        # Orta panel - Market
        pygame.draw.rect(self.screen, LIGHT_BLUE, (340, 80, 600, SCREEN_HEIGHT - 100))
        market_title = font.render("MARKET", True, BLACK)
        self.screen.blit(market_title, (350, 90))
        
        # Market ürünleri
        y_pos = 120
        for category, products in self.game_state['market']['products'].items():
            category_text = font.render(f"--- {category.upper()} ---", True, BLACK)
            self.screen.blit(category_text, (350, y_pos))
            y_pos += 30
            
            for product, data in products.items():
                current_price = self.game_state['market']['prices'].get(product, data['base_price'])
                product_text = font.render(
                    f"{product}: {current_price:,.0f} TL", 
                    True, BLACK
                )
                self.screen.blit(product_text, (370, y_pos))
                
                # Alım-satım butonları
                buy_rect = pygame.Rect(600, y_pos, 60, 20)
                sell_rect = pygame.Rect(670, y_pos, 60, 20)
                
                pygame.draw.rect(self.screen, GREEN, buy_rect)
                pygame.draw.rect(self.screen, RED, sell_rect)
                
                button_font = pygame.font.Font(None, 20)
                buy_text = button_font.render("AL", True, BLACK)
                sell_text = button_font.render("SAT", True, BLACK)
                
                self.screen.blit(buy_text, (620, y_pos + 2))
                self.screen.blit(sell_text, (690, y_pos + 2))
                
                # Butonları kaydet
                self.ui_elements[f'buy_{product}'] = buy_rect
                self.ui_elements[f'sell_{product}'] = sell_rect
                
                y_pos += 30
        
        # Sağ panel - İstatistikler
        pygame.draw.rect(self.screen, LIGHT_BLUE, (960, 80, 300, SCREEN_HEIGHT - 100))
        stats_title = font.render("İSTATİSTİKLER", True, BLACK)
        self.screen.blit(stats_title, (970, 90))
        
        # Beceriler
        y_pos = 120
        skills_text = font.render("Beceriler:", True, BLACK)
        self.screen.blit(skills_text, (970, y_pos))
        y_pos += 30
        
        for skill, level in self.game_state['player']['skills'].items():
            skill_text = font.render(f"{skill}: {level}", True, BLACK)
            self.screen.blit(skill_text, (990, y_pos))
            y_pos += 30
        
        # Şirket istatistikleri
        y_pos += 20
        company_stats_text = font.render("Şirket Durumu:", True, BLACK)
        self.screen.blit(company_stats_text, (970, y_pos))
        y_pos += 30
        
        stats = [
            f"Deneyim: {self.game_state['player']['company']['experience']}",
            f"İtibar: {self.game_state['player']['company']['reputation']}",
            f"Çalışan: {self.game_state['player']['company']['employees']}",
            f"Depo Kapasitesi: {self.game_state['player']['company']['storage_capacity']}"
        ]
        
        for stat in stats:
            stat_text = font.render(stat, True, BLACK)
            self.screen.blit(stat_text, (990, y_pos))
            y_pos += 30

    def buy_product(self, product):
        """Ürün satın al"""
        price = self.game_state['market']['prices'].get(product)
        if not price:
            return
        
        if self.game_state['player']['money'] >= price:
            # Parayı düş
            self.game_state['player']['money'] -= price
            
            # Envanteri güncelle
            if product not in self.game_state['player']['inventory']:
                self.game_state['player']['inventory'][product] = 0
            self.game_state['player']['inventory'][product] += 1
            
            # Deneyim ve beceri puanı ekle
            self.game_state['player']['company']['experience'] += 10
            self.game_state['player']['skills']['trading'] += 0.1
            
        else:
            print("Yeterli paranız yok!")

    def sell_product(self, product):
        """Ürün sat"""
        if product not in self.game_state['player']['inventory'] or self.game_state['player']['inventory'][product] <= 0:
            print("Bu üründen envanterinizde yok!")
            return
        
        price = self.game_state['market']['prices'].get(product)
        if not price:
            return
        
        # Parayı ekle
        self.game_state['player']['money'] += price
        
        # Envanteri güncelle
        self.game_state['player']['inventory'][product] -= 1
        
        # Deneyim ve beceri puanı ekle
        self.game_state['player']['company']['experience'] += 10
        self.game_state['player']['skills']['trading'] += 0.1

    def run(self):
        """Ana oyun döngüsü"""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
            
        pygame.quit()

if __name__ == '__main__':
    game = Game()
    game.run() 