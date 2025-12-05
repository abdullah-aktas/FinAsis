#!/bin/bash
# full_data.json dosyasını Cloud SQL'e yükle
# Cloud Shell'de çalıştırılmalı

set -e

PROJECT_ID="finasis-478502"
REGION="europe-west1"
INSTANCE_NAME="finasis-db"
DB_NAME="finasis"
DB_USER="postgres"

echo "🚀 Cloud SQL'e Veri Yükleme"
echo "==========================="
echo ""

# 1. full_data.json dosyasının varlığını kontrol et
if [ ! -f "full_data.json" ]; then
    echo "❌ full_data.json dosyası bulunamadı!"
    echo "   Önce ./deploy/export_local_to_production.sh çalıştırın"
    exit 1
fi

echo "📋 1. Cloud SQL Proxy başlatılıyor..."
echo "   (Arka planda çalışacak, Ctrl+C ile durdurabilirsiniz)"
echo ""

# Cloud SQL Proxy'yi başlat (arka planda)
gcloud sql connect "$INSTANCE_NAME" \
  --user="$DB_USER" \
  --database="$DB_NAME" \
  --quiet &

PROXY_PID=$!
echo "   Cloud SQL Proxy başlatıldı (PID: $PROXY_PID)"
echo "   ⏳ 5 saniye bekleniyor (bağlantı kurulması için)..."
sleep 5

# 2. Django settings'i Cloud SQL'e yönlendir
echo ""
echo "📋 2. Django ayarları kontrol ediliyor..."

# Geçici olarak Cloud SQL bağlantısı için environment variable
export DJANGO_DB_ENGINE="django.db.backends.postgresql"
export DJANGO_DB_NAME="$DB_NAME"
export DJANGO_DB_USER="$DB_USER"
# Şifre için kullanıcıdan iste
read -sp "Cloud SQL şifresini girin: " DB_PASSWORD
echo ""
export DJANGO_DB_PASSWORD="$DB_PASSWORD"
export DJANGO_DB_HOST="127.0.0.1"
export DJANGO_DB_PORT="5432"

# 3. Migration kontrolü
echo ""
echo "📋 3. Migration'lar kontrol ediliyor..."
python3 manage.py migrate --noinput || {
    echo "⚠️  Migration hatası, devam ediliyor..."
}

# 4. Veri yükleme
echo ""
echo "📋 4. Veri yükleniyor..."
echo "   Bu işlem birkaç dakika sürebilir..."
echo ""

if python3 manage.py loaddata full_data.json --verbosity=2; then
    echo ""
    echo "✅ Veri yükleme başarılı!"
    echo ""
    echo "📊 Yüklenen kayıt sayısı:"
    python3 manage.py shell << 'PYTHON_EOF'
from django.contrib.auth import get_user_model
from accounting.models import Company
User = get_user_model()
print(f"   Kullanıcılar: {User.objects.count()}")
print(f"   Şirketler: {Company.objects.count()}")
PYTHON_EOF
else
    echo ""
    echo "❌ Veri yükleme başarısız!"
    echo "   Hata detayları için: python3 manage.py loaddata full_data.json --verbosity=2 --traceback"
    kill $PROXY_PID 2>/dev/null || true
    exit 1
fi

# 5. Proxy'yi kapat
echo ""
echo "📋 5. Cloud SQL Proxy kapatılıyor..."
kill $PROXY_PID 2>/dev/null || true

echo ""
echo "==========================="
echo "✅ İşlem tamamlandı!"
echo ""
echo "🔐 Güvenlik: full_data.json dosyasını silebilirsiniz:"
echo "   rm full_data.json"

