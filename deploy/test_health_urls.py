#!/usr/bin/env python
"""
Health check URL pattern'lerini test etmek için script
manage.py üzerinden çalıştırılmalı: python manage.py shell < deploy/test_health_urls.py
VEYA direkt: python manage.py shell -c "$(cat deploy/test_health_urls.py | grep -A 1000 'def test_health_urls')"
"""
import os
import sys

# manage.py'nin bulunduğu dizini bul
script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(script_dir)
sys.path.insert(0, project_dir)

# Django setup - manage.py'yi kullanarak
os.chdir(project_dir)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# manage.py'yi import et ve setup yap
import django  # noqa: E402

# Django setup
django.setup()  # noqa: E402

from django.urls import get_resolver, reverse  # noqa: E402
from django.test import Client  # noqa: E402


def test_health_urls():
    """Health check URL'lerini test et"""
    print("🔍 Health Check URL Pattern Test")
    print("=" * 50)

    # 1. URL resolver kontrolü
    resolver = get_resolver()

    # Health ile ilgili pattern'leri bul
    health_patterns = []

    def find_patterns(url_patterns, prefix=""):
        for pattern in url_patterns:
            pattern_str = str(pattern.pattern)
            full_path = prefix + pattern_str
            if "health" in pattern_str.lower():
                health_patterns.append(full_path)
            if hasattr(pattern, "url_patterns"):
                find_patterns(pattern.url_patterns, full_path + "/")

    find_patterns(resolver.url_patterns)

    print("\n📋 Bulunan Health URL Pattern'leri:")
    if health_patterns:
        for pattern in health_patterns:
            print(f"   ✅ {pattern}")
    else:
        print("   ❌ Health pattern bulunamadı!")

    # 2. Reverse URL test
    print("\n📋 Reverse URL Test:")
    try:
        health_url = reverse("health:health_check")
        print(f"   ✅ /health/ -> {health_url}")
    except Exception as e:
        print(f"   ❌ /health/ reverse hatası: {e}")

    try:
        detailed_url = reverse("health:health_check_detailed")
        print(f"   ✅ /health/detailed/ -> {detailed_url}")
    except Exception as e:
        print(f"   ❌ /health/detailed/ reverse hatası: {e}")

    try:
        status_url = reverse("health:site_status")
        print(f"   ✅ /health/status/ -> {status_url}")
    except Exception as e:
        print(f"   ❌ /health/status/ reverse hatası: {e}")

    # 3. Client test
    print("\n📋 HTTP Client Test:")
    client = Client()

    test_urls = [
        "/health/",
        "/health/detailed/",
        "/health/status/",
    ]

    for url in test_urls:
        try:
            response = client.get(url)
            if response.status_code == 200:
                print(f"   ✅ {url} -> HTTP {response.status_code}")
                # JSON response kontrolü
                try:
                    import json

                    data = json.loads(response.content)
                    print(f"      Status: {data.get('status', 'N/A')}")
                except (json.JSONDecodeError, ValueError, Exception):
                    print("      (JSON parse edilemedi)")
            else:
                print(f"   ⚠️  {url} -> HTTP {response.status_code}")
        except Exception as e:
            print(f"   ❌ {url} -> Hata: {e}")

    print("\n" + "=" * 50)
    print("✅ Test tamamlandı!")


if __name__ == "__main__":
    test_health_urls()
