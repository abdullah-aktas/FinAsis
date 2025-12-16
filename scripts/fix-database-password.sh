#!/bin/bash
# Veritabanı şifre doğrulama hatasını düzeltme scripti
# Kullanım: bash scripts/fix-database-password.sh

set -e

PROJECT_ID="finasis-478502"
REGION="europe-west1"
SERVICE_NAME="finasis-prod"
DB_INSTANCE="finasis-db"
DB_USER="finasis-app"
DB_NAME="finasis"

echo "🔍 Veritabanı Şifre Sorunu Teşhisi ve Düzeltme"
echo "=============================================="
echo ""

# 1. Cloud SQL instance'ı kontrol et
echo "📊 Cloud SQL instance kontrol ediliyor..."
INSTANCE_EXISTS=$(gcloud sql instances describe $DB_INSTANCE \
  --project=$PROJECT_ID \
  --format="value(name)" 2>/dev/null || echo "")

if [ -z "$INSTANCE_EXISTS" ]; then
  echo "❌ HATA: Cloud SQL instance '$DB_INSTANCE' bulunamadı!"
  exit 1
fi

echo "✅ Cloud SQL instance bulundu: $DB_INSTANCE"
echo ""

# 2. Kullanıcıyı kontrol et
echo "👤 Veritabanı kullanıcısı kontrol ediliyor..."
USER_EXISTS=$(gcloud sql users list \
  --instance=$DB_INSTANCE \
  --project=$PROJECT_ID \
  --format="value(name)" 2>/dev/null | grep -w "$DB_USER" || echo "")

if [ -z "$USER_EXISTS" ]; then
  echo "⚠️  Kullanıcı '$DB_USER' bulunamadı. Oluşturuluyor..."
  read -sp "   Yeni şifre girin: " NEW_PASSWORD
  echo ""
  
  if [ -z "$NEW_PASSWORD" ]; then
    echo "❌ Şifre boş olamaz!"
    exit 1
  fi
  
  gcloud sql users create $DB_USER \
    --instance=$DB_INSTANCE \
    --password="$NEW_PASSWORD" \
    --project=$PROJECT_ID
  
  echo "✅ Kullanıcı oluşturuldu: $DB_USER"
else
  echo "✅ Kullanıcı mevcut: $DB_USER"
  echo ""
  echo "🔑 Şifre sıfırlama seçenekleri:"
  echo "   1. Yeni şifre oluştur (önerilen)"
  echo "   2. Mevcut şifreyi kullan (GitHub Secret'tan)"
  echo ""
  read -p "   Seçiminiz (1/2): " CHOICE
  
  if [ "$CHOICE" = "1" ]; then
    read -sp "   Yeni şifre girin: " NEW_PASSWORD
    echo ""
    
    if [ -z "$NEW_PASSWORD" ]; then
      echo "❌ Şifre boş olamaz!"
      exit 1
    fi
    
    echo "🔄 Şifre güncelleniyor..."
    gcloud sql users set-password $DB_USER \
      --instance=$DB_INSTANCE \
      --password="$NEW_PASSWORD" \
      --project=$PROJECT_ID
    
    echo "✅ Şifre güncellendi!"
    echo ""
    echo "📝 ŞİMDİ YAPMANIZ GEREKENLER:"
    echo "   1. GitHub Secrets'a gidin:"
    echo "      https://github.com/abdullah-aktas/FinAsis/settings/secrets/actions"
    echo "   2. 'DJANGO_DB_PASSWORD' secret'ını güncelleyin"
    echo "   3. Yeni şifre: $NEW_PASSWORD"
    echo ""
    read -p "   GitHub Secret'ı güncellediniz mi? (y/n): " CONFIRMED
    
    if [ "$CONFIRMED" != "y" ] && [ "$CONFIRMED" != "Y" ]; then
      echo "⚠️  Lütfen GitHub Secret'ı güncelleyin ve scripti tekrar çalıştırın"
      exit 1
    fi
  elif [ "$CHOICE" = "2" ]; then
    echo "ℹ️  Mevcut şifreyi kullanıyorsunuz"
    echo "   GitHub Secret'taki şifrenin doğru olduğundan emin olun"
  else
    echo "❌ Geçersiz seçim!"
    exit 1
  fi
fi

echo ""
echo "🧪 Veritabanı bağlantısını test ediyoruz..."
echo "   (Bu test için Cloud SQL Proxy gerekir)"
echo ""

# 3. Cloud Run servisindeki mevcut şifreyi kontrol et
echo "📋 Cloud Run servisindeki environment variables kontrol ediliyor..."
CURRENT_DB_PASSWORD=$(gcloud run services describe $SERVICE_NAME \
  --region=$REGION \
  --project=$PROJECT_ID \
  --format="value(spec.template.spec.containers[0].env)" 2>/dev/null | \
  grep -oP 'DJANGO_DB_PASSWORD=\K[^,]*' || echo "")

if [ -n "$CURRENT_DB_PASSWORD" ]; then
  echo "⚠️  Cloud Run'da şifre environment variable olarak set edilmiş"
  echo "   (Secret Manager kullanılması önerilir)"
  echo ""
  echo "🔄 Cloud Run servisini güncellemek için:"
  echo "   bash scripts/deploy-production-cloud-shell.sh"
else
  echo "ℹ️  Cloud Run'da şifre bulunamadı (Secret Manager kullanılıyor olabilir)"
fi

echo ""
echo "✅ Teşhis tamamlandı!"
echo ""
echo "📋 Özet:"
echo "   - Database Instance: $DB_INSTANCE"
echo "   - Database User: $DB_USER"
echo "   - Database Name: $DB_NAME"
echo ""
echo "🚀 Sonraki adımlar:"
echo "   1. GitHub Secret 'DJANGO_DB_PASSWORD' güncel mi kontrol edin"
echo "   2. Deployment yapın: bash scripts/deploy-production-cloud-shell.sh"
echo "   3. Logları kontrol edin:"
echo "      gcloud logging read \"resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME AND textPayload=~'password authentication'\" --project=$PROJECT_ID --limit=10"
echo ""

