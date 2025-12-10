#!/usr/bin/env python3
"""
Django SECRET_KEY oluşturucu
Kullanım: python deploy/generate_secret_key.py
"""
import sys
import os

# Django'yu import etmek için path ekle
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from django.core.management.utils import get_random_secret_key

    secret_key = get_random_secret_key()
    print("=" * 70)
    print("🔐 DJANGO_SECRET_KEY (GitHub Secrets'a ekleyin):")
    print("=" * 70)
    print(secret_key)
    print("=" * 70)
    print(f"✅ Uzunluk: {len(secret_key)} karakter")
    print("=" * 70)
except ImportError:
    # Django yoksa alternatif yöntem
    import secrets
    import string

    chars = string.ascii_letters + string.digits + string.punctuation
    secret_key = "".join(secrets.choice(chars) for _ in range(50))
    print("=" * 70)
    print("🔐 DJANGO_SECRET_KEY (GitHub Secrets'a ekleyin):")
    print("=" * 70)
    print(secret_key)
    print("=" * 70)
    print(f"✅ Uzunluk: {len(secret_key)} karakter")
    print("=" * 70)
    print("⚠️  Not: Django yüklü değil, alternatif yöntem kullanıldı")
    print("=" * 70)
