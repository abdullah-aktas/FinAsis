from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import photon
import json

class TradeSim:
    def __init__(self):
        self.app = Ursina()
        
        # Photon ağ bağlantısı
        self.network = photon.PUN('your_app_id')
        
        # Oyun modu
        self.game_mode = 'classroom'  # classroom, freeplay
        
        # Oyun durumu
        self.game_state = {
            'players': {},
            'market_data': {},
            'teacher_controls': {}
        }
        
    def start_classroom(self, teacher_id):
        """Sınıf modunu başlat"""
        self.game_mode = 'classroom'
        self.game_state['teacher_controls'] = {
            'teacher_id': teacher_id,
            'paused': False,
            'scenario': None
        }
        
    def setup_world(self):
        """3D dünyayı hazırla"""
        # Temel dünya öğeleri
        ground = Entity(
            model='plane',
            scale=(100,1,100),
            texture='grass',
            collider='box'
        )
        
        # Ticaret merkezi
        trading_center = Entity(
            model='building',
            position=(0,0,0),
            scale=2
        )

if __name__ == '__main__':
    game = TradeSim()
    game.setup_world()
    game.app.run()
