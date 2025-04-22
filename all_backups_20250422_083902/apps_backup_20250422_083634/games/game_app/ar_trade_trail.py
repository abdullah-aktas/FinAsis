import pygame
import cv2
import numpy as np
import time
import os
import random
import json
from datetime import datetime
from pygame.locals import *

# Artırılmış Gerçeklik ve Ticaret Oyunu
class ARTradeTrail:
    def __init__(self):
        pygame.init()
        
        # Kamera ayarları
        self.capture = cv2.VideoCapture(0)
        ret, frame = self.capture.read()
        if not ret:
            print("Kamera bulunamadı!")
            exit()
        
        # Ekran ayarları
        self.frame_h, self.frame_w = frame.shape[:2]
        self.screen = pygame.display.set_mode((self.frame_w, self.frame_h))
        pygame.display.set_caption("Ticaretin İzinde - AR Modu")
        
        # Font
        self.font = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        
        # Saat
        self.clock = pygame.time.Clock()
        self.FPS = 30
        
        # Oyun verileri
        self.game_state = {
            'player': {
                'money': 10000,
                'inventory': {},
                'business_level': 1,
                'experience': 0,
                'knowledge': {
                    'finance': 1,
                    'accounting': 1,
                    'marketing': 1,
                    'management': 1
                }
            },
            'market': {
                'products': {
                    'ekmek': {'price': 5, 'demand': 0.8},
                    'süt': {'price': 10, 'demand': 0.7},
                    'peynir': {'price': 50, 'demand': 0.5},
                    'elma': {'price': 8, 'demand': 0.6},
                    'telefon': {'price': 5000, 'demand': 0.2},
                    'bilgisayar': {'price': 15000, 'demand': 0.1}
                }
            },
            'locations': {},
            'current_day': 1,
            'education_complete': False
        }
        
        # AR işaretçileri (gerçek uygulamada bu değerler ArUco işaretçilerden gelir)
        self.markers = {
            'market': {'id': 1, 'position': (100, 100), 'detected': False},
            'bank': {'id': 2, 'position': (300, 100), 'detected': False},
            'office': {'id': 3, 'position': (500, 100), 'detected': False},
            'warehouse': {'id': 4, 'position': (700, 100), 'detected': False}
        }
        
        # UI elementleri
        self.ui_elements = {}
        
        # Oyun durumu
        self.running = True
        self.current_screen = 'main_menu'  # main_menu, game, education, market, bank
        
        # Eğitim notları (muhasebe ve finans bilgileri)
        self.education_notes = {
            'temel_muhasebe': [
                'Muhasebe, işletmelerin finansal işlemlerini kaydetme, sınıflandırma ve raporlama sürecidir.',
                'Bilanço = Varlıklar = Kaynaklar (Borçlar + Özsermaye)',
                'Gelir Tablosu = Gelirler - Giderler = Kâr/Zarar',
                'Çift taraflı kayıt: Her işlem en az iki hesabı etkiler (borç ve alacak)'
            ],
            'finans_temelleri': [
                'Paranın Zaman Değeri: Bugünkü 1 TL, gelecekteki 1 TL\'den daha değerlidir.',
                'Risk ve Getiri: Yüksek getiri genellikle yüksek risk içerir.',
                'Çeşitlendirme: Yatırımlarınızı farklı varlık sınıflarına dağıtın.',
                'Bileşik Faiz: Kazançlarınız üzerinden kazanç elde etmenin gücü.'
            ],
            'vergi_bilgisi': [
                'KDV (Katma Değer Vergisi): Mal ve hizmet alışverişi üzerinden alınan vergi.',
                'Gelir Vergisi: Kişisel kazançlar üzerinden alınan vergi.',
                'Kurumlar Vergisi: Şirket kârları üzerinden alınan vergi.',
                'Vergi Beyannamesi: Vergi mükelleflerinin vergi matrahlarını bildirdiği form.'
            ]
        }
    
    def detect_markers(self, frame):
        """
        AR işaretçilerini tespit et (basitleştirilmiş örnek)
        
        Not: Gerçek uygulamada burada OpenCV'nin ArUco işaretçi tespiti kullanılır
        """
        # Bu örnek için işaretçileri rastgele görünür kıl
        for marker_name, marker_data in self.markers.items():
            if random.random() < 0.2:  # %20 şans ile işaretçi görünür olur
                self.markers[marker_name]['detected'] = True
                # Rastgele bir pozisyon ata
                self.markers[marker_name]['position'] = (
                    random.randint(50, self.frame_w - 50),
                    random.randint(50, self.frame_h - 50)
                )
            else:
                self.markers[marker_name]['detected'] = False
    
    def process_frame(self, frame):
        """Kamera görüntüsünü işle ve AR içeriğini ekle"""
        # Görüntüyü pygame formatına dönüştür
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = np.rot90(frame)
        frame = pygame.surfarray.make_surface(frame)
        
        return frame
    
    def render_ui(self, surface):
        """Kullanıcı arayüzünü oluştur"""
        if self.current_screen == 'main_menu':
            self.render_main_menu(surface)
        elif self.current_screen == 'game':
            self.render_game_ui(surface)
        elif self.current_screen == 'education':
            self.render_education_ui(surface)
        elif self.current_screen == 'market':
            self.render_market_ui(surface)
        elif self.current_screen == 'bank':
            self.render_bank_ui(surface)
    
    def render_main_menu(self, surface):
        """Ana menü ekranını oluştur"""
        # Yarı saydam arka plan
        menu_surface = pygame.Surface((400, 300))
        menu_surface.fill((0, 0, 100))
        menu_surface.set_alpha(200)
        surface.blit(menu_surface, (self.frame_w//2 - 200, self.frame_h//2 - 150))
        
        # Başlık
        title = self.font.render("Ticaretin İzinde - AR", True, (255, 255, 255))
        surface.blit(title, (self.frame_w//2 - 150, self.frame_h//2 - 120))
        
        # Butonlar
        self.ui_elements['start_button'] = pygame.Rect(self.frame_w//2 - 100, self.frame_h//2 - 50, 200, 50)
        pygame.draw.rect(surface, (0, 200, 0), self.ui_elements['start_button'])
        start_text = self.font.render("Oyunu Başlat", True, (255, 255, 255))
        surface.blit(start_text, (self.frame_w//2 - 80, self.frame_h//2 - 40))
        
        self.ui_elements['education_button'] = pygame.Rect(self.frame_w//2 - 100, self.frame_h//2 + 20, 200, 50)
        pygame.draw.rect(surface, (0, 100, 200), self.ui_elements['education_button'])
        education_text = self.font.render("Finansal Eğitim", True, (255, 255, 255))
        surface.blit(education_text, (self.frame_w//2 - 90, self.frame_h//2 + 30))
        
        self.ui_elements['exit_button'] = pygame.Rect(self.frame_w//2 - 100, self.frame_h//2 + 90, 200, 50)
        pygame.draw.rect(surface, (200, 0, 0), self.ui_elements['exit_button'])
        exit_text = self.font.render("Çıkış", True, (255, 255, 255))
        surface.blit(exit_text, (self.frame_w//2 - 40, self.frame_h//2 + 100))
    
    def render_game_ui(self, surface):
        """Oyun arayüzünü oluştur"""
        # Oyuncu bilgileri
        info_surface = pygame.Surface((300, 100))
        info_surface.fill((0, 0, 0))
        info_surface.set_alpha(180)
        surface.blit(info_surface, (10, 10))
        
        money_text = self.font.render(f"Para: {self.game_state['player']['money']} ₺", True, (255, 255, 255))
        surface.blit(money_text, (20, 15))
        
        level_text = self.font.render(f"Seviye: {self.game_state['player']['business_level']}", True, (255, 255, 255))
        surface.blit(level_text, (20, 50))
        
        day_text = self.font.render(f"Gün: {self.game_state['current_day']}", True, (255, 255, 255))
        surface.blit(day_text, (20, 85))
        
        # Tespit edilen işaretçileri görselleştir
        for marker_name, marker_data in self.markers.items():
            if marker_data['detected']:
                # İşaretçi çerçevesi
                pygame.draw.rect(surface, (0, 255, 0), 
                                (marker_data['position'][0] - 40, marker_data['position'][1] - 40, 80, 80), 3)
                
                # İşaretçi adı
                marker_text = self.font_small.render(marker_name.upper(), True, (255, 255, 0))
                surface.blit(marker_text, (marker_data['position'][0] - 30, marker_data['position'][1] - 60))
                
                # İşaretçi etkileşim butonu
                interact_button = pygame.Rect(marker_data['position'][0] - 45, marker_data['position'][1] + 50, 90, 30)
                pygame.draw.rect(surface, (0, 100, 200), interact_button)
                interact_text = self.font_small.render("ETKİLEŞİM", True, (255, 255, 255))
                surface.blit(interact_text, (marker_data['position'][0] - 40, marker_data['position'][1] + 55))
                
                self.ui_elements[f"interact_{marker_name}"] = interact_button
        
        # Menü butonu
        menu_button = pygame.Rect(self.frame_w - 110, 10, 100, 40)
        pygame.draw.rect(surface, (100, 100, 100), menu_button)
        menu_text = self.font_small.render("MENÜ", True, (255, 255, 255))
        surface.blit(menu_text, (self.frame_w - 80, 20))
        self.ui_elements['menu_button'] = menu_button
    
    def render_education_ui(self, surface):
        """Eğitim arayüzünü oluştur"""
        # Arka plan
        education_surface = pygame.Surface((self.frame_w - 100, self.frame_h - 100))
        education_surface.fill((50, 50, 80))
        education_surface.set_alpha(230)
        surface.blit(education_surface, (50, 50))
        
        # Başlık
        title = self.font.render("Finansal Eğitim", True, (255, 255, 255))
        surface.blit(title, (self.frame_w//2 - 100, 70))
        
        # Eğitim içeriği
        topics = list(self.education_notes.keys())
        current_topic = topics[self.game_state['current_day'] % len(topics)]
        notes = self.education_notes[current_topic]
        
        topic_title = self.font.render(current_topic.replace('_', ' ').upper(), True, (255, 220, 0))
        surface.blit(topic_title, (self.frame_w//2 - 150, 120))
        
        y_pos = 180
        for note in notes:
            note_text = self.font_small.render(note, True, (255, 255, 255))
            surface.blit(note_text, (80, y_pos))
            y_pos += 40
        
        # Çıkış butonu
        exit_button = pygame.Rect(self.frame_w//2 - 50, self.frame_h - 100, 100, 40)
        pygame.draw.rect(surface, (200, 0, 0), exit_button)
        exit_text = self.font_small.render("GERİ", True, (255, 255, 255))
        surface.blit(exit_text, (self.frame_w//2 - 30, self.frame_h - 95))
        self.ui_elements['education_exit_button'] = exit_button
        
        # Eğitim sınav butonu
        if not self.game_state['education_complete']:
            quiz_button = pygame.Rect(self.frame_w//2 - 80, self.frame_h - 150, 160, 40)
            pygame.draw.rect(surface, (0, 150, 0), quiz_button)
            quiz_text = self.font_small.render("BİLGİYİ TEST ET", True, (255, 255, 255))
            surface.blit(quiz_text, (self.frame_w//2 - 75, self.frame_h - 145))
            self.ui_elements['quiz_button'] = quiz_button
    
    def render_market_ui(self, surface):
        """Market arayüzünü oluştur"""
        # Arka plan
        market_surface = pygame.Surface((self.frame_w - 100, self.frame_h - 100))
        market_surface.fill((50, 80, 50))
        market_surface.set_alpha(230)
        surface.blit(market_surface, (50, 50))
        
        # Başlık
        title = self.font.render("MARKET", True, (255, 255, 255))
        surface.blit(title, (self.frame_w//2 - 50, 70))
        
        # Ürünler
        y_pos = 120
        for product, data in self.game_state['market']['products'].items():
            # Ürün adı ve fiyatı
            product_text = self.font.render(f"{product}: {data['price']} ₺", True, (255, 255, 255))
            surface.blit(product_text, (100, y_pos))
            
            # Al butonu
            buy_button = pygame.Rect(400, y_pos, 80, 30)
            pygame.draw.rect(surface, (0, 200, 0), buy_button)
            buy_text = self.font_small.render("AL", True, (255, 255, 255))
            surface.blit(buy_text, (430, y_pos + 5))
            self.ui_elements[f"buy_{product}"] = buy_button
            
            # Sat butonu
            sell_button = pygame.Rect(500, y_pos, 80, 30)
            pygame.draw.rect(surface, (200, 0, 0), sell_button)
            sell_text = self.font_small.render("SAT", True, (255, 255, 255))
            surface.blit(sell_text, (525, y_pos + 5))
            self.ui_elements[f"sell_{product}"] = sell_button
            
            # Envanterdeki miktar
            count = self.game_state['player']['inventory'].get(product, 0)
            count_text = self.font_small.render(f"Envanter: {count}", True, (255, 255, 0))
            surface.blit(count_text, (600, y_pos + 5))
            
            # Talep göstergesi
            demand_width = int(data['demand'] * 100)
            pygame.draw.rect(surface, (150, 150, 150), (700, y_pos + 5, 100, 15))  # Arka plan
            pygame.draw.rect(surface, (0, 0, 200), (700, y_pos + 5, demand_width, 15))  # Talep çubuğu
            
            y_pos += 50
        
        # Çıkış butonu
        exit_button = pygame.Rect(self.frame_w//2 - 50, self.frame_h - 100, 100, 40)
        pygame.draw.rect(surface, (200, 0, 0), exit_button)
        exit_text = self.font_small.render("GERİ", True, (255, 255, 255))
        surface.blit(exit_text, (self.frame_w//2 - 30, self.frame_h - 95))
        self.ui_elements['market_exit_button'] = exit_button
    
    def render_bank_ui(self, surface):
        """Banka arayüzünü oluştur"""
        # Arka plan
        bank_surface = pygame.Surface((self.frame_w - 100, self.frame_h - 100))
        bank_surface.fill((50, 50, 80))
        bank_surface.set_alpha(230)
        surface.blit(bank_surface, (50, 50))
        
        # Başlık
        title = self.font.render("BANKA", True, (255, 255, 255))
        surface.blit(title, (self.frame_w//2 - 50, 70))
        
        # Banka bilgileri
        info_text = [
            f"Mevcut Bakiye: {self.game_state['player']['money']} ₺",
            "Faiz Oranı: %5",
            "Kredi Limiti: 50,000 ₺"
        ]
        
        y_pos = 150
        for info in info_text:
            text = self.font.render(info, True, (255, 255, 255))
            surface.blit(text, (100, y_pos))
            y_pos += 50
        
        # Banka işlemleri
        actions = ["Mevduat Yatır", "Kredi Çek", "Yatırım Yap"]
        y_pos = 300
        
        for i, action in enumerate(actions):
            action_button = pygame.Rect(self.frame_w//2 - 100, y_pos, 200, 50)
            pygame.draw.rect(surface, (0, 100, 150), action_button)
            action_text = self.font.render(action, True, (255, 255, 255))
            surface.blit(action_text, (self.frame_w//2 - 80, y_pos + 10))
            self.ui_elements[f"bank_action_{i}"] = action_button
            y_pos += 70
        
        # Çıkış butonu
        exit_button = pygame.Rect(self.frame_w//2 - 50, self.frame_h - 100, 100, 40)
        pygame.draw.rect(surface, (200, 0, 0), exit_button)
        exit_text = self.font_small.render("GERİ", True, (255, 255, 255))
        surface.blit(exit_text, (self.frame_w//2 - 30, self.frame_h - 95))
        self.ui_elements['bank_exit_button'] = exit_button
    
    def handle_events(self):
        """Oyun olaylarını yönet"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Ana menü ekranı
                if self.current_screen == 'main_menu':
                    if self.ui_elements.get('start_button') and self.ui_elements['start_button'].collidepoint(event.pos):
                        self.current_screen = 'game'
                    elif self.ui_elements.get('education_button') and self.ui_elements['education_button'].collidepoint(event.pos):
                        self.current_screen = 'education'
                    elif self.ui_elements.get('exit_button') and self.ui_elements['exit_button'].collidepoint(event.pos):
                        self.running = False
                
                # Oyun ekranı
                elif self.current_screen == 'game':
                    if self.ui_elements.get('menu_button') and self.ui_elements['menu_button'].collidepoint(event.pos):
                        self.current_screen = 'main_menu'
                    
                    # İşaretçi etkileşimleri
                    for marker_name in self.markers:
                        if self.ui_elements.get(f"interact_{marker_name}") and self.ui_elements[f"interact_{marker_name}"].collidepoint(event.pos):
                            if marker_name == 'market':
                                self.current_screen = 'market'
                            elif marker_name == 'bank':
                                self.current_screen = 'bank'
                
                # Eğitim ekranı
                elif self.current_screen == 'education':
                    if self.ui_elements.get('education_exit_button') and self.ui_elements['education_exit_button'].collidepoint(event.pos):
                        self.current_screen = 'main_menu'
                    elif self.ui_elements.get('quiz_button') and self.ui_elements['quiz_button'].collidepoint(event.pos):
                        # Eğitim tamamlandı olarak işaretle
                        self.game_state['education_complete'] = True
                        # Para ve tecrübe ödülü
                        self.game_state['player']['money'] += 1000
                        self.game_state['player']['experience'] += 100
                
                # Market ekranı
                elif self.current_screen == 'market':
                    if self.ui_elements.get('market_exit_button') and self.ui_elements['market_exit_button'].collidepoint(event.pos):
                        self.current_screen = 'game'
                    
                    # Alış-satış işlemleri
                    for product in self.game_state['market']['products']:
                        # Alış
                        if self.ui_elements.get(f"buy_{product}") and self.ui_elements[f"buy_{product}"].collidepoint(event.pos):
                            self.buy_product(product)
                        # Satış
                        elif self.ui_elements.get(f"sell_{product}") and self.ui_elements[f"sell_{product}"].collidepoint(event.pos):
                            self.sell_product(product)
                
                # Banka ekranı
                elif self.current_screen == 'bank':
                    if self.ui_elements.get('bank_exit_button') and self.ui_elements['bank_exit_button'].collidepoint(event.pos):
                        self.current_screen = 'game'
                    
                    # Banka işlemleri
                    for i in range(3):  # 3 banka işlemi için
                        if self.ui_elements.get(f"bank_action_{i}") and self.ui_elements[f"bank_action_{i}"].collidepoint(event.pos):
                            self.handle_bank_action(i)
    
    def buy_product(self, product):
        """Ürün satın al"""
        price = self.game_state['market']['products'][product]['price']
        if self.game_state['player']['money'] >= price:
            # Parayı düş
            self.game_state['player']['money'] -= price
            
            # Envanteri güncelle
            if product not in self.game_state['player']['inventory']:
                self.game_state['player']['inventory'][product] = 0
            self.game_state['player']['inventory'][product] += 1
            
            # Tecrübe kazanç
            self.game_state['player']['experience'] += 10
            
            # Muhasebe ve finans bilgisi (neden böyle yapıldığının açıklaması)
            self.show_education_tip("Alış İşlemi", [
                f"{product} satın aldınız ve bu bir BORÇ kaydıdır.",
                f"Muhasebede: Mal Hesabı (+) | Kasa Hesabı (-)",
                f"Bu işlem envanterinizi arttırır ve nakit paranızı azaltır."
            ])
        else:
            self.show_education_tip("Yetersiz Bakiye", [
                "Yeterli paranız bulunmuyor!",
                "İşletme sermayesi: İşletmenin günlük faaliyetlerini sürdürebilmesi için",
                "gerekli olan nakit ve benzeri varlıklardır."
            ])
    
    def sell_product(self, product):
        """Ürün sat"""
        # Envanterde ürün var mı kontrol et
        if product in self.game_state['player']['inventory'] and self.game_state['player']['inventory'][product] > 0:
            # Fiyatı belirle (talebe göre +/- %10 değişim)
            base_price = self.game_state['market']['products'][product]['price']
            demand = self.game_state['market']['products'][product]['demand']
            sell_price = int(base_price * (0.9 + demand * 0.2))
            
            # Parayı ekle
            self.game_state['player']['money'] += sell_price
            
            # Envanteri güncelle
            self.game_state['player']['inventory'][product] -= 1
            
            # Tecrübe kazanç
            self.game_state['player']['experience'] += 15
            
            # Muhasebe ve finans bilgisi
            self.show_education_tip("Satış İşlemi", [
                f"{product} sattınız ve bu bir ALACAK kaydıdır.",
                f"Muhasebede: Kasa Hesabı (+) | Satılan Mal Maliyeti (-)",
                f"Bu işlem nakit paranızı arttırır ve envanterinizi azaltır.",
                f"Satış Kârı = Satış Fiyatı - Mal Maliyeti = {sell_price - base_price} ₺"
            ])
        else:
            self.show_education_tip("Envanter Hatası", [
                "Bu üründen envanterinizde bulunmuyor!",
                "Stok takibi: İşletmelerin mal ve hizmet üretiminde kullanılmak",
                "üzere elde tutulan varlıkların takip edilmesi işlemidir."
            ])
    
    def handle_bank_action(self, action_index):
        """Banka işlemlerini yönet"""
        if action_index == 0:  # Mevduat Yatır
            self.show_education_tip("Mevduat İşlemi", [
                "Mevduat hesabı %5 faiz oranı ile paranızı değerlendirir.",
                "Bileşik Faiz: A = P(1 + r)^t",
                "A: Son tutar, P: Anapara, r: Faiz oranı, t: Süre"
            ])
        elif action_index == 1:  # Kredi Çek
            self.show_education_tip("Kredi İşlemi", [
                "Krediler işletme sermayenizi arttırmanın bir yoludur.",
                "Borç/Özkaynak Oranı = Toplam Borç / Özkaynak",
                "Bu oran yükseldikçe finansal riskiniz artar."
            ])
        elif action_index == 2:  # Yatırım Yap
            self.show_education_tip("Yatırım İşlemi", [
                "Yatırımlar uzun vadeli büyümenin anahtarıdır.",
                "Yatırım Getiri Oranı (ROI) = (Kazanç - Maliyet) / Maliyet",
                "ROI ne kadar yüksekse, yatırımınız o kadar verimlidir."
            ])
    
    def show_education_tip(self, title, messages):
        """Eğitim ipucu göster"""
        # Arka plan
        tip_surface = pygame.Surface((600, 200))
        tip_surface.fill((0, 50, 100))
        tip_surface.set_alpha(230)
        self.screen.blit(tip_surface, (self.frame_w//2 - 300, self.frame_h//2 - 100))
        
        # Başlık
        title_text = self.font.render(title, True, (255, 255, 0))
        self.screen.blit(title_text, (self.frame_w//2 - 280, self.frame_h//2 - 90))
        
        # Mesajlar
        y_pos = self.frame_h//2 - 50
        for msg in messages:
            msg_text = self.font_small.render(msg, True, (255, 255, 255))
            self.screen.blit(msg_text, (self.frame_w//2 - 280, y_pos))
            y_pos += 25
        
        # Tamam butonu
        ok_button = pygame.Rect(self.frame_w//2 - 50, self.frame_h//2 + 70, 100, 30)
        pygame.draw.rect(self.screen, (0, 200, 0), ok_button)
        ok_text = self.font_small.render("TAMAM", True, (255, 255, 255))
        self.screen.blit(ok_text, (self.frame_w//2 - 35, self.frame_h//2 + 75))
        
        # Ekranı güncelle
        pygame.display.flip()
        
        # Kullanıcının TAMAM butonuna tıklamasını bekle
        waiting_for_ok = True
        while waiting_for_ok:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting_for_ok = False
                    self.running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if ok_button.collidepoint(event.pos):
                        waiting_for_ok = False
    
    def update_game_state(self):
        """Oyun durumunu güncelle"""
        # İşaretçi tespiti
        ret, frame = self.capture.read()
        if ret:
            self.detect_markers(frame)
        
        # Level kontrolü
        exp = self.game_state['player']['experience']
        current_level = self.game_state['player']['business_level']
        
        # Her 100 deneyim puanı için 1 seviye
        new_level = 1 + exp // 100
        if new_level > current_level:
            self.game_state['player']['business_level'] = new_level
            self.show_education_tip("Seviye Atlama!", [
                f"Tebrikler! Seviye {new_level} oldunuz.",
                "Yeni iş fırsatları ve daha yüksek kâr marjları açıldı.",
                "İşletme büyüdükçe; Ciro, FAVÖK ve Net Kâr gibi finansal",
                "metrikleriniz de yükselir."
            ])
    
    def run(self):
        """Ana oyun döngüsü"""
        while self.running:
            # Kamera görüntüsünü al
            ret, frame = self.capture.read()
            if not ret:
                print("Kamera hatası!")
                break
            
            # Oyun durumunu güncelle
            self.update_game_state()
            
            # Olayları işle
            self.handle_events()
            
            # Görüntüyü işle
            processed_frame = self.process_frame(frame)
            
            # Ekranı temizle
            self.screen.blit(processed_frame, (0, 0))
            
            # UI oluştur
            self.render_ui(self.screen)
            
            # Ekranı güncelle
            pygame.display.flip()
            
            # FPS sınırı
            self.clock.tick(self.FPS)
        
        # Kamera ve Pygame'i kapat
        self.capture.release()
        pygame.quit()

# Ana program
if __name__ == "__main__":
    game = ARTradeTrail()
    game.run() 