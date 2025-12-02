#!/bin/bash
# Fixture dosyasını canlı ortama yükleme scripti
# Cloud Shell'de çalıştırın

set -euo pipefail

PROJECT_ID="finasis-478502"
REGION="europe-west1"
SERVICE_NAME="finasis-prod"
FIXTURE_FILE="fixtures/users_all.json"

echo "🚀 Fixture Dosyasını Canlıya Yükleme"
echo "======================================"
echo "Proje: $PROJECT_ID"
echo "Bölge: $REGION"
echo "Servis: $SERVICE_NAME"
echo "Fixture: $FIXTURE_FILE"
echo ""

# Proje dizinine geç
cd ~/FinAsis || {
    echo "❌ FinAsis dizini bulunamadı!"
    echo "💡 Önce projeyi klonlayın: git clone https://github.com/abdullah-aktas/FinAsis.git"
    exit 1
}

# Git durumunu kontrol et
echo "📊 Git durumu kontrol ediliyor..."
if ! git diff --quiet HEAD; then
    echo "⚠️  Yerel değişiklikler var. Önce commit edin veya stash yapın."
    read -p "Devam etmek istiyor musunuz? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 0
    fi
fi

# Son değişiklikleri al
echo "⬇️  Son değişiklikler alınıyor..."
git pull origin main || {
    echo "⚠️  Git pull başarısız. Devam ediliyor..."
}

# Fixture dosyasının varlığını kontrol et
if [ ! -f "$FIXTURE_FILE" ]; then
    echo "❌ Fixture dosyası bulunamadı: $FIXTURE_FILE"
    echo "💡 Önce dosyayı GitHub'dan çekin: git pull origin main"
    exit 1
fi

# JSON syntax kontrolü
echo "🔍 JSON syntax kontrolü yapılıyor..."
python3 -m json.tool "$FIXTURE_FILE" > /dev/null || {
    echo "❌ JSON syntax hatası!"
    exit 1
}
echo "✅ JSON geçerli"

# Yedek al
echo ""
echo "💾 Mevcut veriler yedekleniyor..."
BACKUP_FILE="fixtures/users_backup_$(date +%Y%m%d_%H%M%S).json"
python3 manage.py dumpdata accounts.customuser auth.group auth.permission \
    --indent 2 --output "$BACKUP_FILE" 2>/dev/null || {
    echo "⚠️  Yedek alınamadı (normal olabilir, veritabanı boş olabilir)"
}
if [ -f "$BACKUP_FILE" ]; then
    echo "✅ Yedek alındı: $BACKUP_FILE"
fi

# Environment variables'ı ayarla
echo ""
echo "🔧 Environment variables ayarlanıyor..."

# Secret Manager'dan şifreleri al
export DJANGO_DB_PASSWORD=$(gcloud secrets versions access latest --secret="finasis-db-pass" --project="$PROJECT_ID" 2>/dev/null || echo "")
export DJANGO_SECRET_KEY=$(gcloud secrets versions access latest --secret="finasis-django-secret" --project="$PROJECT_ID" 2>/dev/null || echo "")

# Cloud SQL instance adını bul
CLOUD_SQL_INSTANCE=$(gcloud sql instances list --project="$PROJECT_ID" --format="value(connectionName)" --filter="region:$REGION" | head -n 1)

if [ -z "$CLOUD_SQL_INSTANCE" ]; then
    echo "⚠️  Cloud SQL instance bulunamadı. Manuel olarak girin:"
    read -p "Cloud SQL Connection Name (PROJECT:REGION:INSTANCE): " CLOUD_SQL_INSTANCE
fi

# Database ayarları
export DJANGO_SETTINGS_MODULE=config.settings
export DJANGO_DB_ENGINE=django.db.backends.postgresql
export DJANGO_DB_NAME=finasis
export DJANGO_DB_USER=finasis-app
export DJANGO_DB_HOST="/cloudsql/$CLOUD_SQL_INSTANCE"
export DJANGO_DB_PORT=""
export DJANGO_DEBUG=False

# Cloud SQL Proxy'yi başlat (arka planda)
echo ""
echo "🔌 Cloud SQL Proxy başlatılıyor..."
if ! pgrep -f cloud_sql_proxy > /dev/null; then
    cloud_sql_proxy -instances="$CLOUD_SQL_INSTANCE=tcp:5432" > /tmp/cloud_sql_proxy.log 2>&1 &
    PROXY_PID=$!
    sleep 3
    
    # Proxy'nin çalıştığını kontrol et
    if ! ps -p $PROXY_PID > /dev/null; then
        echo "❌ Cloud SQL Proxy başlatılamadı!"
        exit 1
    fi
    echo "✅ Cloud SQL Proxy başlatıldı (PID: $PROXY_PID)"
    
    # Cleanup function
    cleanup() {
        echo ""
        echo "🧹 Cloud SQL Proxy kapatılıyor..."
        kill $PROXY_PID 2>/dev/null || true
    }
    trap cleanup EXIT
else
    echo "✅ Cloud SQL Proxy zaten çalışıyor"
    export DJANGO_DB_HOST="127.0.0.1"
    export DJANGO_DB_PORT="5432"
fi

# Migration kontrolü
echo ""
echo "🗄️  Migration durumu kontrol ediliyor..."
python3 manage.py migrate --check > /dev/null 2>&1 || {
    echo "⚠️  Uygulanmamış migration'lar var. Uygulanıyor..."
    python3 manage.py migrate --noinput
}

# Dry-run (test)
echo ""
echo "🧪 Dry-run yapılıyor (test modu)..."
python3 manage.py loaddata "$FIXTURE_FILE" --verbosity=0 --dry-run 2>/dev/null || {
    echo "⚠️  Dry-run başarısız (normal olabilir, devam ediliyor...)"
}

# Onay iste
echo ""
echo "⚠️  DİKKAT: Bu işlem veritabanına veri yükleyecek!"
echo "📋 Fixture dosyası: $FIXTURE_FILE"
read -p "Devam etmek istiyor musunuz? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ İptal edildi"
    exit 0
fi

# Loaddata çalıştır
echo ""
echo "📥 Fixture dosyası yükleniyor..."
python3 manage.py loaddata "$FIXTURE_FILE" --verbosity=2

# Sonuç kontrolü
echo ""
echo "✅ Yükleme tamamlandı!"
echo ""
echo "📊 Kontrol ediliyor..."
python3 manage.py shell << EOF
from accounts.models import CustomUser
from django.contrib.auth.models import Group, Permission
print(f"✅ Toplam kullanıcı: {CustomUser.objects.count()}")
print(f"✅ Toplam grup: {Group.objects.count()}")
print(f"✅ Toplam izin: {Permission.objects.count()}")
EOF

echo ""
echo "🎉 İşlem başarıyla tamamlandı!"
echo "💾 Yedek dosyası: $BACKUP_FILE"

