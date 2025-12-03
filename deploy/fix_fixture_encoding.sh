#!/bin/bash
# Fixture dosyasını UTF-8'e dönüştürme scripti
# Cloud Shell'de çalıştırın

set -euo pipefail

cd ~/FinAsis || {
    echo "❌ FinAsis dizini bulunamadı!"
    exit 1
}

FIXTURE_FILE="fixtures/users_all.json"

echo "🔧 Fixture Dosyası Encoding Düzeltmesi"
echo "======================================"
echo ""

# Git sorununu çöz
echo "📦 Git durumu düzeltiliyor..."
if git diff --quiet "$FIXTURE_FILE" 2>/dev/null; then
    echo "✅ Git durumu temiz"
else
    echo "⚠️  Yerel değişiklikler var, stash yapılıyor..."
    git stash push -m "Temporary stash for fixture fix" || true
fi

# GitHub'dan güncellemeleri al
echo "⬇️  GitHub'dan güncellemeler alınıyor..."
git pull origin main || {
    echo "⚠️  Git pull başarısız, devam ediliyor..."
}

# Fixture dosyasının varlığını kontrol et
if [ ! -f "$FIXTURE_FILE" ]; then
    echo "❌ Fixture dosyası bulunamadı: $FIXTURE_FILE"
    exit 1
fi

echo ""
echo "🔍 JSON dosyası encoding kontrolü yapılıyor..."

# Python ile encoding'i düzelt
python3 << 'PYTHON_SCRIPT'
import json
import sys
import os

fixture_file = "fixtures/users_all.json"

# Farklı encoding'leri dene
encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1', 'windows-1252']

data = None
used_encoding = None

for encoding in encodings:
    try:
        with open(fixture_file, 'r', encoding=encoding, errors='replace') as f:
            data = json.load(f)
        used_encoding = encoding
        print(f"✅ Dosya okundu (encoding: {encoding})")
        break
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        continue
    except Exception as e:
        print(f"⚠️  Encoding {encoding} denendi: {e}")
        continue

if data is None:
    print("❌ Dosya hiçbir encoding ile okunamadı!")
    sys.exit(1)

# UTF-8 olarak kaydet
try:
    with open(fixture_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ Dosya UTF-8'e dönüştürüldü ve kaydedildi")
except Exception as e:
    print(f"❌ Dosya kaydedilemedi: {e}")
    sys.exit(1)

# Doğrulama
try:
    with open(fixture_file, 'r', encoding='utf-8') as f:
        json.load(f)
    print("✅ JSON syntax doğrulandı")
except Exception as e:
    print(f"❌ JSON syntax hatası: {e}")
    sys.exit(1)
PYTHON_SCRIPT

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Encoding düzeltmesi tamamlandı!"
    echo ""
    echo "📊 Dosya bilgileri:"
    ls -lh "$FIXTURE_FILE"
    echo ""
    echo "🧪 JSON doğrulama:"
    python3 -m json.tool "$FIXTURE_FILE" > /dev/null && echo "✅ JSON geçerli" || echo "❌ JSON hatası"
    echo ""
    echo "🚀 Artık loaddata çalıştırabilirsiniz:"
    echo "   python3 manage.py loaddata $FIXTURE_FILE --verbosity=2"
else
    echo ""
    echo "❌ Encoding düzeltmesi başarısız!"
    exit 1
fi

