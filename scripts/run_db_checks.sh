#!/bin/bash
set -e

echo "FinAsis Veritabanı Kontrolleri"
echo "==============================="

# Virtual environment'ı aktive et
source venv/bin/activate

# Veritabanı kontrollerini çalıştır
python scripts/db_checker.py

# Yedekleme kontrolü
if [ -f "backup/latest.sql" ]; then
    echo "✓ Son yedekleme mevcut: $(stat -c %y backup/latest.sql)"
else
    echo "✗ Son yedekleme bulunamadı!"
    exit 1
fi

# PostgreSQL servis kontrolü
if systemctl is-active --quiet postgresql; then
    echo "✓ PostgreSQL servisi çalışıyor"
else
    echo "✗ PostgreSQL servisi çalışmıyor!"
    exit 1
fi

echo "\nKontroller tamamlandı."
