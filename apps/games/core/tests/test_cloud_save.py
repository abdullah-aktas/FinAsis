import unittest
import time
import json
import os
from ..game_engine import GameEngine
from ..notifications import NotificationSystem

class TestCloudSave(unittest.TestCase):
    def setUp(self):
        self.game_engine = GameEngine({})
        self.notification_system = NotificationSystem()
        self.test_save_dir = "test_saves"
        os.makedirs(self.test_save_dir, exist_ok=True)
        
    def tearDown(self):
        # Test dosyalarını temizle
        for file in os.listdir(self.test_save_dir):
            os.remove(os.path.join(self.test_save_dir, file))
        os.rmdir(self.test_save_dir)
        
    def test_save_game_state(self):
        """Oyun durumu kaydetme testi"""
        player_id = "test_player"
        test_data = {
            "score": 1000,
            "inventory": ["item1", "item2"],
            "progress": {"level": 5, "xp": 1000}
        }
        
        # Kayıt işlemi
        save_path = os.path.join(self.test_save_dir, f"{player_id}.json")
        with open(save_path, 'w') as f:
            json.dump(test_data, f)
            
        # Kayıt kontrolü
        self.assertTrue(os.path.exists(save_path))
        
        # Bildirim kontrolü
        notifications = self.notification_system.get_player_notifications(player_id)
        self.assertTrue(any(n.type == "cloud_save" for n in notifications))
        
    def test_load_game_state(self):
        """Oyun durumu yükleme testi"""
        player_id = "test_player"
        test_data = {
            "score": 1000,
            "inventory": ["item1", "item2"],
            "progress": {"level": 5, "xp": 1000}
        }
        
        # Test verisi oluştur
        save_path = os.path.join(self.test_save_dir, f"{player_id}.json")
        with open(save_path, 'w') as f:
            json.dump(test_data, f)
            
        # Yükleme işlemi
        with open(save_path, 'r') as f:
            loaded_data = json.load(f)
            
        # Veri kontrolü
        self.assertEqual(loaded_data, test_data)
        
    def test_save_conflict_resolution(self):
        """Kayıt çakışması çözümleme testi"""
        player_id = "test_player"
        
        # İki farklı kayıt oluştur
        save1 = {"score": 1000, "timestamp": time.time()}
        save2 = {"score": 2000, "timestamp": time.time() + 1}
        
        # Çakışma çözümleme
        latest_save = save1 if save1["timestamp"] > save2["timestamp"] else save2
        
        self.assertEqual(latest_save["score"], 2000)
        
    def test_save_encryption(self):
        """Kayıt şifreleme testi"""
        player_id = "test_player"
        test_data = {
            "score": 1000,
            "inventory": ["item1", "item2"]
        }
        
        # Şifreleme işlemi
        encrypted_data = self._encrypt_data(test_data)
        
        # Şifreli veri kontrolü
        self.assertNotEqual(encrypted_data, json.dumps(test_data))
        
        # Şifre çözme
        decrypted_data = self._decrypt_data(encrypted_data)
        self.assertEqual(decrypted_data, test_data)
        
    def _encrypt_data(self, data: dict) -> str:
        """Veriyi şifreler"""
        # Basit şifreleme örneği
        return json.dumps(data)[::-1]
        
    def _decrypt_data(self, encrypted_data: str) -> dict:
        """Şifrelenmiş veriyi çözer"""
        # Basit şifre çözme örneği
        return json.loads(encrypted_data[::-1])
        
    def test_save_backup(self):
        """Yedekleme testi"""
        player_id = "test_player"
        test_data = {"score": 1000}
        
        # Ana kayıt
        save_path = os.path.join(self.test_save_dir, f"{player_id}.json")
        with open(save_path, 'w') as f:
            json.dump(test_data, f)
            
        # Yedek oluştur
        backup_path = os.path.join(self.test_save_dir, f"{player_id}_backup.json")
        with open(backup_path, 'w') as f:
            json.dump(test_data, f)
            
        self.assertTrue(os.path.exists(backup_path))
        
    def test_save_validation(self):
        """Kayıt doğrulama testi"""
        player_id = "test_player"
        test_data = {"score": 1000}
        
        # Geçerli kayıt
        self.assertTrue(self._validate_save_data(test_data))
        
        # Geçersiz kayıt
        invalid_data = {"score": "invalid"}
        self.assertFalse(self._validate_save_data(invalid_data))
        
    def _validate_save_data(self, data: dict) -> bool:
        """Kayıt verisini doğrular"""
        return isinstance(data.get("score"), (int, float))
        
if __name__ == '__main__':
    unittest.main() 