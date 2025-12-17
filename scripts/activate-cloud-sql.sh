#!/bin/bash
# Cloud SQL instance'ı aktif hale getirme scripti

set -e

PROJECT_ID="finasis-478502"
REGION="europe-west1"
INSTANCE_NAME="finasis-db"

echo "🔧 Cloud SQL Instance Aktifleştirme"
echo "===================================="
echo ""

# Instance durumunu kontrol et
echo "📊 Mevcut durum:"
gcloud sql instances describe "$INSTANCE_NAME" \
  --project="$PROJECT_ID" \
  --format="table(name,state,settings.tier,settings.availabilityType)"

echo ""

# Eğer SUSPENDED ise, aktif hale getir
STATE=$(gcloud sql instances describe "$INSTANCE_NAME" \
  --project="$PROJECT_ID" \
  --format="value(state)")

if [ "$STATE" = "SUSPENDED" ]; then
  echo "⚠️  Instance SUSPENDED durumda. Aktifleştiriliyor..."
  echo "⏳ Bu işlem birkaç dakika sürebilir..."
  
  # Instance'ı patch et (aktif hale getir)
  gcloud sql instances patch "$INSTANCE_NAME" \
    --project="$PROJECT_ID" \
    --activation-policy=ALWAYS \
    --quiet
  
  echo "✅ Instance aktifleştirme komutu gönderildi"
  echo "⏳ Durum kontrol ediliyor..."
  
  # Durum kontrolü (maksimum 5 dakika bekle)
  MAX_WAIT=300
  ELAPSED=0
  
  while [ $ELAPSED -lt $MAX_WAIT ]; do
    CURRENT_STATE=$(gcloud sql instances describe "$INSTANCE_NAME" \
      --project="$PROJECT_ID" \
      --format="value(state)" 2>/dev/null || echo "UNKNOWN")
    
    echo "  Durum: $CURRENT_STATE (${ELAPSED}s/${MAX_WAIT}s)"
    
    if [ "$CURRENT_STATE" = "RUNNABLE" ]; then
      echo "✅ Instance başarıyla aktifleştirildi!"
      break
    fi
    
    sleep 10
    ELAPSED=$((ELAPSED + 10))
  done
  
  if [ $ELAPSED -ge $MAX_WAIT ]; then
    echo "⚠️  Timeout: Instance hala aktifleşmedi. Lütfen manuel kontrol edin."
  fi
else
  echo "ℹ️  Instance zaten aktif durumda: $STATE"
fi

echo ""
echo "📊 Final durum:"
gcloud sql instances describe "$INSTANCE_NAME" \
  --project="$PROJECT_ID" \
  --format="table(name,state,settings.tier,settings.availabilityType)"

