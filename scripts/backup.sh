#!/bin/bash

# Yedekleme dizini
BACKUP_DIR="/backups/finasis"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=7

# Dizin oluştur
mkdir -p $BACKUP_DIR

# PostgreSQL yedekleme
echo "PostgreSQL yedekleme başlatılıyor..."
PGPASSWORD=$DB_PASSWORD pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Redis yedekleme
echo "Redis yedekleme başlatılıyor..."
redis-cli -h redis save
cp /data/dump.rdb $BACKUP_DIR/redis_$DATE.rdb

# Media dosyaları yedekleme
echo "Media dosyaları yedekleniyor..."
tar -czf $BACKUP_DIR/media_$DATE.tar.gz /app/media

# Static dosyaları yedekleme
echo "Static dosyaları yedekleniyor..."
tar -czf $BACKUP_DIR/static_$DATE.tar.gz /app/static

# Eski yedekleri temizle
echo "Eski yedekler temizleniyor..."
find $BACKUP_DIR -type f -mtime +$RETENTION_DAYS -delete

# Yedekleme durumunu kontrol et
if [ $? -eq 0 ]; then
    echo "Yedekleme başarıyla tamamlandı: $DATE"
    # Başarılı yedekleme bildirimi
    curl -X POST -H "Content-Type: application/json" \
         -d "{\"text\":\"✅ FinAsis yedekleme başarıyla tamamlandı: $DATE\"}" \
         $SLACK_WEBHOOK_URL
else
    echo "Yedekleme sırasında hata oluştu!"
    # Hata bildirimi
    curl -X POST -H "Content-Type: application/json" \
         -d "{\"text\":\"❌ FinAsis yedekleme hatası: $DATE\"}" \
         $SLACK_WEBHOOK_URL
    exit 1
fi 