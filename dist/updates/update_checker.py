# -*- coding: utf-8 -*-
import requests
import json
import logging
import os
import sys
import hashlib
from pathlib import Path
from datetime import datetime

class UpdateChecker:
    def __init__(self, config_path):
        self.config = self._load_config(config_path)
        self.logger = self._setup_logger()
        self.current_version = self.config['application']['version']
        
    def _load_config(self, config_path):
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Yapılandırma dosyası yüklenemedi: {str(e)}")
            sys.exit(1)
            
    def _setup_logger(self):
        logger = logging.getLogger('update_checker')
        logger.setLevel(logging.INFO)
        
        handler = logging.FileHandler('update.log')
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
        
    def check_for_updates(self):
        try:
            response = requests.get(
                f"{self.config['updates']['update_server']}/version",
                timeout=10
            )
            response.raise_for_status()
            
            latest_version = response.json()['version']
            
            if self._compare_versions(latest_version, self.current_version) > 0:
                self.logger.info(f"Yeni versiyon bulundu: {latest_version}")
                return True, latest_version
                
            return False, None
            
        except Exception as e:
            self.logger.error(f"Güncelleme kontrolü sırasında hata: {str(e)}")
            return False, None
            
    def download_update(self, version):
        try:
            response = requests.get(
                f"{self.config['updates']['update_server']}/download/{version}",
                timeout=30
            )
            response.raise_for_status()
            
            update_path = Path('updates') / f"finasis_{version}.exe"
            update_path.parent.mkdir(exist_ok=True)
            
            with open(update_path, 'wb') as f:
                f.write(response.content)
                
            if self._verify_update(update_path):
                self.logger.info(f"Güncelleme indirildi: {version}")
                return update_path
                
            return None
            
        except Exception as e:
            self.logger.error(f"Güncelleme indirme sırasında hata: {str(e)}")
            return None
            
    def _verify_update(self, update_path):
        try:
            response = requests.get(
                f"{self.config['updates']['update_server']}/checksum/{update_path.name}",
                timeout=10
            )
            response.raise_for_status()
            
            expected_checksum = response.json()['checksum']
            actual_checksum = self._calculate_checksum(update_path)
            
            return expected_checksum == actual_checksum
            
        except Exception as e:
            self.logger.error(f"Güncelleme doğrulama sırasında hata: {str(e)}")
            return False
            
    def _calculate_checksum(self, file_path):
        sha256_hash = hashlib.sha256()
        
        with open(file_path, 'rb') as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
                
        return sha256_hash.hexdigest()
        
    def _compare_versions(self, v1, v2):
        v1_parts = list(map(int, v1.split('.')))
        v2_parts = list(map(int, v2.split('.')))
        
        for v1_part, v2_part in zip(v1_parts, v2_parts):
            if v1_part > v2_part:
                return 1
            elif v1_part < v2_part:
                return -1
                
        return 0
        
    def install_update(self, update_path):
        try:
            # Yedekleme
            backup_path = Path('backup') / f"finasis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.exe"
            backup_path.parent.mkdir(exist_ok=True)
            
            current_exe = Path(sys.executable)
            current_exe.rename(backup_path)
            
            # Güncelleme
            update_path.rename(current_exe)
            
            self.logger.info("Güncelleme başarıyla yüklendi")
            return True
            
        except Exception as e:
            self.logger.error(f"Güncelleme yükleme sırasında hata: {str(e)}")
            return False 