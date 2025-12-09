#!/bin/bash
# Cloud Shell'de çalıştırın: bash deploy/fix_and_check_secrets.sh
# Git pull sorununu çözer ve secret'ları kontrol eder

set -euo pipefail

PROJECT_ID="finasis-478502"

echo "🔧 Git pull sorununu çözüyoruz..."
cd ~/FinAsis || { echo "❌ FinAsis dizini bulunamadı!"; exit 1; }

# Yerel değişiklikleri kontrol et
if [ -n "$(git status --porcelain 2>/dev/null)" ]; then
    echo "⚠️  Yerel değişiklikler bulundu, stash ediliyor..."
    git stash push -m "Auto-stash before pull $(date +%Y%m%d_%H%M%S)" || {
        echo "⚠️  Stash başarısız, yerel değişiklikler restore ediliyor..."
        git restore . || echo "⚠️  Restore başarısız, devam ediliyor..."
    }
fi

# Git pull yap
echo "📥 Git pull yapılıyor..."
git pull origin main || {
    echo "❌ Git pull başarısız!"
    exit 1
}

echo "✅ Git pull tamamlandı"
echo ""

# Secret kontrol script'ini çalıştır
if [ -f "deploy/check_secrets.sh" ]; then
    echo "🔍 Secret'lar kontrol ediliyor..."
    bash deploy/check_secrets.sh
else
    echo "⚠️  deploy/check_secrets.sh bulunamadı, manuel kontrol yapılıyor..."
    
    echo "🔍 Secret Manager kontrolü..."
    echo "Proje: $PROJECT_ID"
    echo ""
    
    # Gerekli secret'lar
    REQUIRED_SECRETS=(
        "DJANGO_SECRET_KEY"
        "DJANGO_DB_PASSWORD"
    )
    
    for SECRET_NAME in "${REQUIRED_SECRETS[@]}"; do
        echo "📋 Kontrol ediliyor: $SECRET_NAME"
        
        if gcloud secrets describe "$SECRET_NAME" --project="$PROJECT_ID" >/dev/null 2>&1; then
            echo "   ✅ $SECRET_NAME mevcut"
        else
            echo "   ❌ $SECRET_NAME bulunamadı!"
            echo ""
            echo "   🔧 Oluşturmak için:"
            echo "   echo 'your-secret-value' | gcloud secrets create $SECRET_NAME --data-file=- --project=$PROJECT_ID"
            echo "   echo 'your-secret-value' | gcloud secrets versions add $SECRET_NAME --data-file=- --project=$PROJECT_ID"
            echo ""
        fi
    done
    
    echo ""
    echo "📊 Tüm secret'ları listelemek için:"
    echo "   gcloud secrets list --project=$PROJECT_ID"
    echo ""
    echo "💡 Secret değerini görmek için (dikkatli kullanın!):"
    echo "   gcloud secrets versions access latest --secret=SECRET_NAME --project=$PROJECT_ID"
fi

