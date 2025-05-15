#!/bin/bash
# FinAsis Otomatik PostgreSQL Yedekleme Scripti
# Her gün çalıştırmak için crontab'a ekleyebilirsiniz.

BACKUP_DIR="/var/backups/finasis"
DATE=$(date +"%Y-%m-%d_%H-%M-%S")
DB_NAME="finasis"
DB_USER="postgres"
DB_HOST="localhost"

mkdir -p $BACKUP_DIR
pg_dump -U $DB_USER -h $DB_HOST $DB_NAME | gzip > $BACKUP_DIR/finasis_backup_$DATE.sql.gz

# 7 günden eski yedekleri sil
find $BACKUP_DIR -type f -name "*.sql.gz" -mtime +7 -exec rm {} \;

echo "Yedekleme tamamlandı: $BACKUP_DIR/finasis_backup_$DATE.sql.gz" 