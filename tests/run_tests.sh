#!/bin/bash
# FinAsis Test Çalıştırma Betiği
set -e

echo "🧪 FinAsis Test Süreci Başlatılıyor..."

# Django test veritabanını temizle
python manage.py flush --no-input

# 1. Unit Testler
echo "🔍 Unit testler çalıştırılıyor..."
python manage.py test --settings=config.settings.test

# 2. Coverage Raporu
echo "📊 Test coverage hesaplanıyor..."
coverage run manage.py test
coverage report
coverage html

# 3. Entegrasyon Testleri
echo "🔄 Entegrasyon testleri çalıştırılıyor..."
pytest tests/integration/

# 4. Performans Testleri
echo "⚡ Performans testleri çalıştırılıyor..."
python -m pytest tests/test_performance.py -v

# 5. API Testleri
echo "🌐 API testleri çalıştırılıyor..."
python -m pytest tests/test_api.py -v

# 6. Güvenlik Testleri
echo "🔒 Güvenlik kontrolleri yapılıyor..."
python manage.py check --deploy --settings=config.settings.prod

echo "✅ Test süreci tamamlandı!"
