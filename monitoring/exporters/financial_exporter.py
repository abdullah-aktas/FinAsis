# -*- coding: utf-8 -*-
from prometheus_client import start_http_server, Gauge, Counter, Histogram
import time
import random
import psutil
import requests
from datetime import datetime

# Metrik tanımlamaları
TRANSACTION_VOLUME = Counter('financial_transactions_total', 'Toplam finansal işlem sayısı')
TRANSACTION_ERRORS = Counter('financial_transaction_errors_total', 'Toplam hatalı işlem sayısı')
TRANSACTION_DURATION = Histogram('financial_transaction_duration_seconds', 'İşlem süreleri')
SYSTEM_LOAD = Gauge('system_load_percent', 'Sistem yükü yüzdesi')
MEMORY_USAGE = Gauge('memory_usage_percent', 'Bellek kullanım yüzdesi')
DISK_USAGE = Gauge('disk_usage_percent', 'Disk kullanım yüzdesi')

def collect_metrics():
    while True:
        # Örnek işlem simülasyonu
        duration = random.uniform(0.1, 3.0)
        TRANSACTION_DURATION.observe(duration)
        TRANSACTION_VOLUME.inc()
        
        if random.random() < 0.05:  # %5 hata oranı
            TRANSACTION_ERRORS.inc()
        
        # Sistem metrikleri
        SYSTEM_LOAD.set(psutil.cpu_percent())
        MEMORY_USAGE.set(psutil.virtual_memory().percent)
        DISK_USAGE.set(psutil.disk_usage('/').percent)
        
        time.sleep(1)

if __name__ == '__main__':
    # HTTP sunucusunu başlat
    start_http_server(9091)
    # Metrik toplamayı başlat
    collect_metrics() 