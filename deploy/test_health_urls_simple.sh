#!/bin/bash
# Health check URL'lerini test etmek için basit script
# manage.py shell kullanarak çalışır

cd "$(dirname "$0")/.." || exit 1

echo "🔍 Health Check URL Pattern Test"
echo "======================================"
echo ""

# Python script'i manage.py shell içinde çalıştır
python3 manage.py shell << 'PYTHON_EOF'
import sys
from django.urls import get_resolver, reverse
from django.test import Client
from django.conf import settings

def test_health_urls():
    """Health check URL'lerini test et"""
    print("\n📋 1. Reverse URL Test:")
    print("-" * 40)
    try:
        health_url = reverse('health:health_check')
        print(f"   ✅ /health/ -> {health_url}")
    except Exception as e:
        print(f"   ❌ /health/ reverse hatası: {e}")
        return False
    
    try:
        detailed_url = reverse('health:health_check_detailed')
        print(f"   ✅ /health/detailed/ -> {detailed_url}")
    except Exception as e:
        print(f"   ❌ /health/detailed/ reverse hatası: {e}")
        return False
    
    try:
        status_url = reverse('health:site_status')
        print(f"   ✅ /health/status/ -> {status_url}")
    except Exception as e:
        print(f"   ❌ /health/status/ reverse hatası: {e}")
        return False
    
    print("\n📋 2. HTTP Client Test:")
    print("-" * 40)
    
    # ALLOWED_HOSTS'i geçici olarak genişlet (test için)
    original_allowed_hosts = settings.ALLOWED_HOSTS.copy()
    settings.ALLOWED_HOSTS = list(settings.ALLOWED_HOSTS) + ['testserver', 'localhost', '127.0.0.1']
    
    try:
        client = Client()
        
        test_urls = [
            ('/health/', 'health_check'),
            ('/health/detailed/', 'health_check_detailed'),
            ('/health/status/', 'site_status'),
        ]
        
        all_ok = True
        for url, name in test_urls:
            try:
                response = client.get(url)
                if response.status_code == 200:
                    print(f"   ✅ {url} -> HTTP {response.status_code}")
                    try:
                        import json
                        data = json.loads(response.content)
                        status = data.get('status', data.get('overall_health', 'N/A'))
                        print(f"      Status: {status}")
                    except:
                        print(f"      (Response: {response.content[:100]}...)")
                else:
                    print(f"   ⚠️  {url} -> HTTP {response.status_code}")
                    all_ok = False
            except Exception as e:
                print(f"   ❌ {url} -> Hata: {e}")
                all_ok = False
        
        return all_ok
    finally:
        # ALLOWED_HOSTS'i geri yükle
        settings.ALLOWED_HOSTS = original_allowed_hosts

if __name__ == '__main__' or True:
    success = test_health_urls()
    print("\n" + "=" * 50)
    if success:
        print("✅ Tüm testler başarılı!")
        sys.exit(0)
    else:
        print("⚠️  Bazı testler başarısız!")
        sys.exit(1)

test_health_urls()
PYTHON_EOF

echo ""
echo "======================================"
echo "✅ Test tamamlandı!"

