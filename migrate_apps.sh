#!/bin/bash
# Bu script, apps/ dizinindeki modülleri ana dizine taşıma işlemini otomatize eder

echo "FinAsis Modül Taşıma Sistemi"
echo "============================"
echo

# Yedek dizini oluştur
BACKUP_DIR="./apps_backup_$(date +%Y%m%d_%H%M%S)"
echo "Apps dizininin yedeği oluşturuluyor: $BACKUP_DIR"
mkdir -p "$BACKUP_DIR"
cp -r ./apps/* "$BACKUP_DIR/"
echo "Yedekleme tamamlandı."
echo

# 1. Modülleri taşı ve içerikleri güncelle
echo "1. Modülleri ana dizine taşıma işlemi başlatılıyor..."
python migrate_modules.py
echo

# 2. settings.py dosyasını güncelle
echo "2. INSTALLED_APPS güncelleniyor..."
python update_settings.py
echo

# 3. URL yapısını güncelle
echo "3. URL patternleri güncelleniyor..."
python update_urls.py
echo

# Başarılı mesajı
echo "İşlem tamamlandı!"
echo "Tüm modüller ana dizine taşındı ve bağlantılar güncellendi."
echo "Projenizi test etmek için Django development sunucusunu başlatabilirsiniz:"
echo "python manage.py runserver"
echo
echo "Not: Herhangi bir sorunda, yedeklediğimiz $BACKUP_DIR dizininden eski modüllere erişebilirsiniz." 