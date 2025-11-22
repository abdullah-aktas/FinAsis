#!/bin/bash
# Build loglarını kontrol etmek için script

BUILD_ID="a2884ce4-868f-4ab5-94bf-1bef5e774671"
REGION="europe-west1"

echo "=========================================="
echo "Build Loglarını Görüntülüyorum..."
echo "=========================================="
echo ""

# Build durumunu kontrol et
echo "1. Build Durumu:"
gcloud builds describe $BUILD_ID --region=$REGION --format="value(status)"

echo ""
echo "2. Build Logları (son 100 satır):"
gcloud builds log $BUILD_ID --region=$REGION | tail -100

echo ""
echo "=========================================="
echo "Detaylı loglar için:"
echo "gcloud builds log $BUILD_ID --region=$REGION"
echo "=========================================="

