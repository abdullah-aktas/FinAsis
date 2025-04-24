#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
FinAsis - Ursina Oyun Motoru Test Uygulaması
--------------------------------------------
Bu script, Ursina oyun motorunun temel özelliklerini test eder ve gösterir.
"""

from typing import Optional, Tuple, List
from dataclasses import dataclass
from enum import Enum, auto
import logging
import sys
from pathlib import Path

from ursina import (
    Ursina, Entity, color, Text, Button, 
    camera, window, mouse, time, 
    Vec3, Vec2, distance, 
    Audio, Sequence, Func,
    Sky, EditorCamera,
    load_texture, load_model
)

# Logging yapılandırması
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ursina_test.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class GameState(Enum):
    """Oyun durumlarını temsil eder."""
    MENU = auto()
    PLAYING = auto()
    PAUSED = auto()
    GAME_OVER = auto()

@dataclass
class GameConfig:
    """Oyun yapılandırması."""
    window_title: str = "FinAsis - Ursina Test"
    window_size: Tuple[int, int] = (800, 600)
    window_fullscreen: bool = False
    window_vsync: bool = True
    window_fps_counter: bool = True
    window_editor_ui: bool = True
    window_show_ursina_splash: bool = False

class GameManager:
    """Oyun yöneticisi sınıfı."""
    
    def __init__(self, config: GameConfig):
        self.config = config
        self.app = None
        self.state = GameState.MENU
        self.score = 0
        self.entities: List[Entity] = []
        self.audio = Audio('assets/sounds/background.mp3', loop=True, autoplay=False)
        
        # Oyun nesneleri
        self.player = None
        self.camera = None
        self.sky = None
        self.ui_elements = []
        
        # Performans metrikleri
        self.fps_history: List[float] = []
        self.frame_times: List[float] = []
    
    def setup_window(self):
        """Pencere ayarlarını yapılandırır."""
        window.title = self.config.window_title
        window.size = self.config.window_size
        window.fullscreen = self.config.window_fullscreen
        window.vsync = self.config.window_vsync
        window.fps_counter.enabled = self.config.window_fps_counter
        window.editor_ui.enabled = self.config.window_editor_ui
        window.show_ursina_splash = self.config.window_show_ursina_splash
    
    def create_player(self):
        """Oyuncu nesnesini oluşturur."""
        self.player = Entity(
            model='cube',
            color=color.orange,
            scale=(1, 2, 1),
            position=(0, 0, 0),
            collider='box'
        )
        self.entities.append(self.player)
    
    def create_environment(self):
        """Oyun ortamını oluşturur."""
        # Gökyüzü
        self.sky = Sky(texture='sky_sunset')
        self.entities.append(self.sky)
        
        # Zemin
        ground = Entity(
            model='plane',
            texture='grass',
            scale=(20, 1, 20),
            position=(0, -1, 0),
            collider='box'
        )
        self.entities.append(ground)
        
        # Kamera
        self.camera = EditorCamera()
        self.camera.position = (0, 5, -10)
        self.camera.rotation_x = 20
    
    def create_ui(self):
        """Kullanıcı arayüzünü oluşturur."""
        # Başlık
        title = Text(
            text='FinAsis - Ursina Test',
            origin=(0, 0),
            scale=2,
            position=(0, 0.3, 0)
        )
        self.ui_elements.append(title)
        
        # Skor
        self.score_text = Text(
            text=f'Skor: {self.score}',
            origin=(0, 0),
            scale=1,
            position=(0, -0.3, 0)
        )
        self.ui_elements.append(self.score_text)
        
        # Başlat butonu
        start_button = Button(
            text='Başlat',
            color=color.green,
            scale=(0.2, 0.1),
            position=(0, -0.1, 0),
            on_click=self.start_game
        )
        self.ui_elements.append(start_button)
    
    def start_game(self):
        """Oyunu başlatır."""
        logger.info("Oyun başlatılıyor...")
        self.state = GameState.PLAYING
        self.score = 0
        self.audio.play()
        
        # UI elemanlarını gizle
        for element in self.ui_elements:
            element.enabled = False
    
    def update(self):
        """Oyun güncellemelerini yapar."""
        if self.state != GameState.PLAYING:
            return
        
        # FPS takibi
        self.fps_history.append(window.fps)
        if len(self.fps_history) > 60:
            self.fps_history.pop(0)
        
        # Frame süresi takibi
        self.frame_times.append(time.dt)
        if len(self.frame_times) > 60:
            self.frame_times.pop(0)
        
        # Skor güncelleme
        self.score += 1
        self.score_text.text = f'Skor: {self.score}'
    
    def run(self):
        """Oyunu çalıştırır."""
        try:
            self.app = Ursina()
            self.setup_window()
            self.create_player()
            self.create_environment()
            self.create_ui()
            
            # Ana döngü
            def update():
                self.update()
            
            self.app.run()
            
        except Exception as e:
            logger.error(f"Oyun çalıştırılırken hata oluştu: {e}")
            sys.exit(1)

def main():
    """Ana program."""
    try:
        # Oyun yapılandırması
        config = GameConfig(
            window_title="FinAsis - Ursina Test",
            window_size=(1280, 720),
            window_fullscreen=False,
            window_vsync=True,
            window_fps_counter=True,
            window_editor_ui=True
        )
        
        # Oyun yöneticisini başlat
        game = GameManager(config)
        game.run()
        
    except KeyboardInterrupt:
        logger.info("Oyun kullanıcı tarafından durduruldu")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Beklenmeyen hata: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 