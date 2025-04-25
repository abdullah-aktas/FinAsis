import unittest
import time
import psutil
import pygame
from ..game_engine import GameEngine
from ..notifications import NotificationSystem

class TestPerformance(unittest.TestCase):
    def setUp(self):
        self.game_engine = GameEngine({})
        self.notification_system = NotificationSystem()
        
    def test_fps_performance(self):
        """FPS performans testi"""
        pygame.init()
        screen = pygame.display.set_mode((800, 600))
        clock = pygame.time.Clock()
        
        fps_values = []
        for _ in range(100):  # 100 frame test
            start_time = time.time()
            
            # Oyun döngüsü
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                    
            screen.fill((0, 0, 0))
            pygame.display.flip()
            
            end_time = time.time()
            fps = 1.0 / (end_time - start_time)
            fps_values.append(fps)
            
            clock.tick(60)
            
        avg_fps = sum(fps_values) / len(fps_values)
        min_fps = min(fps_values)
        
        self.assertGreaterEqual(avg_fps, 55, "Ortalama FPS 55'in altında")
        self.assertGreaterEqual(min_fps, 30, "Minimum FPS 30'un altında")
        
    def test_memory_usage(self):
        """Bellek kullanımı testi"""
        initial_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
        # Bellek yoğun işlemler
        test_data = []
        for _ in range(1000):
            test_data.append([i for i in range(1000)])
            
        final_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        self.assertLessEqual(memory_increase, 100, "Bellek kullanımı 100MB'dan fazla arttı")
        
    def test_network_performance(self):
        """Ağ performansı testi"""
        start_time = time.time()
        
        # Bulut kayıt testi
        self.game_engine.save_game_state("test_player")
        
        end_time = time.time()
        save_duration = end_time - start_time
        
        self.assertLessEqual(save_duration, 2.0, "Bulut kayıt 2 saniyeden uzun sürdü")
        
    def test_cross_platform_performance(self):
        """Çoklu platform performans testi"""
        # Platform özel optimizasyonların testi
        platform = pygame.get_sdl_version()
        if platform[0] == 2:  # Windows
            self._test_windows_optimizations()
        elif platform[0] == 1:  # Linux
            self._test_linux_optimizations()
        else:
            self._test_mac_optimizations()
            
    def _test_windows_optimizations(self):
        """Windows optimizasyon testleri"""
        # DirectX performans testi
        # Windows özel bellek yönetimi
        pass
        
    def _test_linux_optimizations(self):
        """Linux optimizasyon testleri"""
        # OpenGL performans testi
        # Linux özel bellek yönetimi
        pass
        
    def _test_mac_optimizations(self):
        """macOS optimizasyon testleri"""
        # Metal performans testi
        # macOS özel bellek yönetimi
        pass
        
    def test_notification_performance(self):
        """Bildirim sistemi performans testi"""
        start_time = time.time()
        
        # Çoklu bildirim gönderme
        for _ in range(100):
            self.notification_system.send_notification(
                "test_player",
                "system",
                "Test",
                "Test mesajı"
            )
            
        end_time = time.time()
        notification_duration = end_time - start_time
        
        self.assertLessEqual(notification_duration, 1.0, "100 bildirim 1 saniyeden uzun sürdü")
        
if __name__ == '__main__':
    unittest.main() 