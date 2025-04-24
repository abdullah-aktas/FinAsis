from ursina import *
from game_manager import GameManager

class GameIntegration(Entity):
    def __init__(self, player_id, **kwargs):
        super().__init__(**kwargs)
        self.game_manager = GameManager(player_id)
        self.player_data = self.game_manager.get_player_data()
        
    def update(self):
        """Her frame'de çalışacak güncelleme fonksiyonu"""
        # Oyun durumunu kontrol et ve kaydet
        game_state = self.get_current_game_state()
        self.game_manager.save_game_state(game_state)
        
        # Görevleri kontrol et
        self.game_manager.check_challenges(game_state)
        
    def get_current_game_state(self):
        """Mevcut oyun durumunu döndürür"""
        return {
            'player': self.player_data,
            'buildings': self.get_buildings_state(),
            'workers': self.get_workers_state(),
            'inventory': self.get_inventory_state(),
            'economy': self.get_economy_state()
        }
        
    def get_buildings_state(self):
        """Binaların durumunu döndürür"""
        buildings = []
        for entity in scene.entities:
            if hasattr(entity, 'building_type'):
                buildings.append({
                    'type': entity.building_type,
                    'position': [entity.position.x, entity.position.y, entity.position.z],
                    'rotation': [entity.rotation.x, entity.rotation.y, entity.rotation.z],
                    'health': getattr(entity, 'health', 100),
                    'efficiency': getattr(entity, 'efficiency', 1.0)
                })
        return buildings
        
    def get_workers_state(self):
        """Çalışanların durumunu döndürür"""
        workers = []
        for entity in scene.entities:
            if hasattr(entity, 'worker_type'):
                workers.append({
                    'type': entity.worker_type,
                    'position': [entity.position.x, entity.position.y, entity.position.z],
                    'task': getattr(entity, 'current_task', None),
                    'efficiency': getattr(entity, 'efficiency', 1.0)
                })
        return workers
        
    def get_inventory_state(self):
        """Envanter durumunu döndürür"""
        return {
            'materials': getattr(self, 'materials', {}),
            'products': getattr(self, 'products', {}),
            'money': self.player_data['balance']
        }
        
    def get_economy_state(self):
        """Ekonomi durumunu döndürür"""
        return {
            'market_trend': getattr(self, 'market_trend', 'stable'),
            'prices': getattr(self, 'current_prices', {}),
            'demand': getattr(self, 'current_demand', {})
        }
        
    def record_transaction(self, transaction_type, amount, description):
        """İşlem kaydı oluşturur"""
        self.game_manager.record_transaction(transaction_type, amount, description)
        self.player_data = self.game_manager.get_player_data() 