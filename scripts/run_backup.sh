#!/bin/bash

# Yedekleme dizinine git
cd "$(dirname "$0")/.."

# Log dizinini oluştur
mkdir -p logs

# Ortam değişkenlerini ayarla
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service-account-key.json"
export BACKUP_BUCKET_NAME="finasis-backups"
export DB_HOST="localhost"
export DB_USER="postgres"
export DB_NAME="finasis"
export DB_PASSWORD="your_db_password"

# Tarih ve saat bilgisini al
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")

# Log dosyası
LOG_FILE="logs/cron_backup.log"

# Log fonksiyonu
log() {
    echo "[$TIMESTAMP] $1" >> "$LOG_FILE"
    echo "[$TIMESTAMP] $1"
}

# Hata durumunda çıkış
set -e

# Başlangıç logu
log "Yedekleme işlemi başlatılıyor..."

# Veritabanı yedeği
log "Veritabanı yedeği alınıyor..."
python scripts/backup.py --backup-db
if [ $? -eq 0 ]; then
    log "Veritabanı yedeği başarıyla alındı"
else
    log "HATA: Veritabanı yedeği alınamadı"
    exit 1
fi

# Media dosyaları yedeği
log "Media dosyaları yedeği alınıyor..."
python scripts/backup.py --backup-media
if [ $? -eq 0 ]; then
    log "Media dosyaları yedeği başarıyla alındı"
else
    log "HATA: Media dosyaları yedeği alınamadı"
    exit 1
fi

# Bitiş logu
log "Tüm yedekleme işlemleri başarıyla tamamlandı"

# Eski log dosyalarını temizle (30 günden eski)
find logs -name "cron_backup.log.*" -mtime +30 -delete 