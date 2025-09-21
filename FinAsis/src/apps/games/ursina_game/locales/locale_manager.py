# -*- coding: utf-8 -*-
import json
import os
from typing import Dict, Optional

class LocaleManager:
    def __init__(self):
        self.current_locale = 'tr'  # Varsayılan dil
        self.locales: Dict[str, Dict] = {}
        self.load_locales()
        
    def load_locales(self):
        """Tüm dil dosyalarını yükle"""
        locales_dir = os.path.join(os.path.dirname(__file__), 'locales')
        for filename in os.listdir(locales_dir):
            if filename.endswith('.json'):
                locale_code = filename.split('.')[0]
                with open(os.path.join(locales_dir, filename), 'r', encoding='utf-8') as f:
                    self.locales[locale_code] = json.load(f)
                    
    def set_locale(self, locale_code: str) -> bool:
        """Dil ayarını değiştir"""
        if locale_code in self.locales:
            self.current_locale = locale_code
            return True
        return False
        
    def get_text(self, key: str, default: Optional[str] = None) -> str:
        """Belirtilen anahtar için metni döndür"""
        try:
            keys = key.split('.')
            value = self.locales[self.current_locale]
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default or key
            
    def get_available_locales(self) -> list:
        """Mevcut dilleri döndür"""
        return list(self.locales.keys())
        
    def get_current_locale(self) -> str:
        """Mevcut dili döndür"""
        return self.current_locale 