import unittest
import tkinter as tk
from unittest.mock import patch, MagicMock
from desktop_app import FinasisDesktopApp

class TestFinasisDesktopApp(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.app = FinasisDesktopApp(self.root)
    
    def tearDown(self):
        self.root.destroy()
    
    def test_initialization(self):
        """Uygulama başlatma testi"""
        self.assertEqual(self.app.current_version, "1.0.0")
        self.assertIsNone(self.app.latest_version)
        self.assertFalse(self.app.is_server_running)
    
    @patch('requests.get')
    def test_check_for_updates(self, mock_get):
        """Güncelleme kontrolü testi"""
        # Güncel versiyon testi
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {'version': '1.0.0'}
        self.app.check_for_updates()
        self.assertEqual(self.app.update_label.cget('text'), "Uygulama güncel")
        
        # Yeni versiyon testi
        mock_get.return_value.json.return_value = {'version': '1.1.0'}
        self.app.check_for_updates()
        self.assertTrue("Yeni güncelleme mevcut" in self.app.update_label.cget('text'))
    
    def test_show_settings(self):
        """Ayarlar penceresi testi"""
        self.app.show_settings()
        self.assertTrue(any(isinstance(w, tk.Toplevel) for w in self.root.winfo_children()))
    
    def test_show_about(self):
        """Hakkında penceresi testi"""
        self.app.show_about()
        self.assertTrue(any(isinstance(w, tk.Toplevel) for w in self.root.winfo_children()))
    
    @patch('webbrowser.open')
    def test_show_user_guide(self, mock_open):
        """Kullanıcı kılavuzu testi"""
        self.app.show_user_guide()
        mock_open.assert_called_once_with("https://docs.finasis.com/user-guide")
    
    def test_server_controls(self):
        """Sunucu kontrol butonları testi"""
        # Başlangıç durumu
        self.assertEqual(self.app.start_button['state'], tk.NORMAL)
        self.assertEqual(self.app.stop_button['state'], tk.DISABLED)
        self.assertEqual(self.app.browser_button['state'], tk.DISABLED)
        
        # Sunucu çalışır durum
        self.app.update_ui_server_running()
        self.assertEqual(self.app.start_button['state'], tk.DISABLED)
        self.assertEqual(self.app.stop_button['state'], tk.NORMAL)
        self.assertEqual(self.app.browser_button['state'], tk.NORMAL)
        
        # Sunucu durdurulmuş durum
        self.app.update_ui_server_stopped()
        self.assertEqual(self.app.start_button['state'], tk.NORMAL)
        self.assertEqual(self.app.stop_button['state'], tk.DISABLED)
        self.assertEqual(self.app.browser_button['state'], tk.DISABLED)
    
    @patch('subprocess.Popen')
    def test_start_server(self, mock_popen):
        """Sunucu başlatma testi"""
        mock_process = MagicMock()
        mock_popen.return_value = mock_process
        self.app.start_server()
        mock_popen.assert_called_once()
        self.assertIsNotNone(self.app.server_process)
    
    @patch('subprocess.Popen')
    def test_stop_server(self, mock_popen):
        """Sunucu durdurma testi"""
        mock_process = MagicMock()
        mock_popen.return_value = mock_process
        self.app.start_server()
        self.app.stop_server()
        mock_process.terminate.assert_called_once()
    
    @patch('webbrowser.open')
    def test_open_browser(self, mock_open):
        """Tarayıcı açma testi"""
        self.app.open_browser()
        mock_open.assert_called_once_with("http://127.0.0.1:8000")

if __name__ == '__main__':
    unittest.main() 