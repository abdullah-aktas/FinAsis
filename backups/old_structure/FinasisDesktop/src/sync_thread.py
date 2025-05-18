# -*- coding: utf-8 -*-
from PyQt5.QtCore import QThread, pyqtSignal
import sqlite3
import requests
import json
from datetime import datetime

class SyncThread(QThread):
    """Senkronizasyon işlemlerini yürüten thread sınıfı"""
    finished = pyqtSignal()  # Senkronizasyon tamamlandığında sinyal gönderir
    error = pyqtSignal(str)  # Hata durumunda sinyal gönderir
    
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.api_url = "https://finasis-api.example.com"  # API URL'sini güncelleyin
        
    def run(self):
        """Thread çalıştığında bu metod çağrılır"""
        try:
            # Yerel değişiklikleri al
            local_changes = self.get_local_changes()
            
            # Sunucuya gönder
            self.send_to_server(local_changes)
            
            # Sunucudan değişiklikleri al
            server_changes = self.get_from_server()
            
            # Yerel veritabanını güncelle
            self.update_local_db(server_changes)
            
            # Son senkronizasyon zamanını güncelle
            self.update_sync_time()
            
            self.finished.emit()
            
        except Exception as e:
            self.error.emit(str(e))
            
    def get_local_changes(self):
        """Yerel veritabanındaki değişiklikleri alır"""
        cursor = self.db.cursor()
        # Son senkronizasyondan sonra değişen kayıtları al
        cursor.execute("""
            SELECT * FROM changes 
            WHERE change_date > (
                SELECT last_sync 
                FROM sync_info 
                WHERE id = 1
            )
        """)
        return cursor.fetchall()
        
    def send_to_server(self, changes):
        """Değişiklikleri sunucuya gönderir"""
        if not changes:
            return
            
        response = requests.post(
            f"{self.api_url}/sync",
            json={"changes": changes}
        )
        response.raise_for_status()
        
    def get_from_server(self):
        """Sunucudaki değişiklikleri alır"""
        last_sync = self.get_last_sync_time()
        response = requests.get(
            f"{self.api_url}/sync",
            params={"since": last_sync}
        )
        response.raise_for_status()
        return response.json()["changes"]
        
    def update_local_db(self, changes):
        """Yerel veritabanını günceller"""
        if not changes:
            return
            
        cursor = self.db.cursor()
        for change in changes:
            table = change["table"]
            operation = change["operation"]
            data = change["data"]
            
            if operation == "INSERT":
                placeholders = ",".join(["?"] * len(data))
                columns = ",".join(data.keys())
                cursor.execute(
                    f"INSERT INTO {table} ({columns}) VALUES ({placeholders})",
                    list(data.values())
                )
            elif operation == "UPDATE":
                set_clause = ",".join([f"{k}=?" for k in data.keys()])
                cursor.execute(
                    f"UPDATE {table} SET {set_clause} WHERE id=?",
                    list(data.values()) + [data["id"]]
                )
            elif operation == "DELETE":
                cursor.execute(
                    f"DELETE FROM {table} WHERE id=?",
                    [data["id"]]
                )
                
        self.db.commit()
        
    def get_last_sync_time(self):
        """Son senkronizasyon zamanını alır"""
        cursor = self.db.cursor()
        cursor.execute("SELECT last_sync FROM sync_info WHERE id = 1")
        result = cursor.fetchone()
        return result[0] if result else None
        
    def update_sync_time(self):
        """Son senkronizasyon zamanını günceller"""
        cursor = self.db.cursor()
        now = datetime.now().isoformat()
        cursor.execute("""
            INSERT OR REPLACE INTO sync_info (id, last_sync) 
            VALUES (1, ?)
        """, [now])
        self.db.commit() 