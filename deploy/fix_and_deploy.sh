#!/bin/bash
# Git sorunlarını çöz ve deploy et

set -e

cd ~/FinAsis || exit 1

echo "🔧 Git Sorunlarını Çözme"
echo "========================"

# Yerel değişiklikleri kontrol et
if git diff --quiet && git diff --cached --quiet; then
    echo "✅ Yerel değişiklik yok"
else
    echo "⚠️  Yerel değişiklikler var, atılıyor..."
    git restore deploy/test_health_urls_simple.sh 2>/dev/null || true
    git restore . 2>/dev/null || true
fi

# Stash yap (eğer hala değişiklik varsa)
git stash 2>/dev/null || true

# Son değişiklikleri al
echo "⬇️  Son değişiklikler alınıyor..."
git pull origin main

echo ""
echo "✅ Git sorunları çözüldü!"
echo ""
echo "📦 Cloud Build ile Deploy"
echo "========================"

# Cloud Build API'sini kontrol et
echo "🔍 Cloud Build API kontrol ediliyor..."
if ! gcloud services list --enabled --filter="name:cloudbuild.googleapis.com" --format="value(name)" | grep -q cloudbuild; then
    echo "⚠️  Cloud Build API etkin değil, etkinleştiriliyor..."
    gcloud services enable cloudbuild.googleapis.com
    echo "⏳ API etkinleştiriliyor, 30 saniye bekleniyor..."
    sleep 30
fi

# Proje kontrolü
PROJECT_ID=$(gcloud config get-value project)
echo "📋 Proje: $PROJECT_ID"

# Cloud Build submit
echo "🚀 Cloud Build başlatılıyor..."
gcloud builds submit --config cloudbuild.yaml

echo ""
echo "✅ Deploy işlemi tamamlandı!"

