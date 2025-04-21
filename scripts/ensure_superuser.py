#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Superuser'ın varlığını kontrol eden ve yoksa oluşturan script.
Bu script, ortam değişkenlerinden aldığı bilgilerle bir superuser oluşturur.
"""

import os
import sys
import django

# Django ayarlarını yükle
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.db import IntegrityError

def ensure_superuser():
    """
    Superuser kontrol eder ve yoksa oluşturur.
    Ortam değişkenlerinden alınan bilgilerle bir superuser oluşturur.
    """
    User = get_user_model()
    
    # Ortam değişkenlerinden superuser bilgilerini al
    superuser_username = os.getenv('DJANGO_SUPERUSER_USERNAME', 'admin')
    superuser_email = os.getenv('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
    superuser_password = os.getenv('DJANGO_SUPERUSER_PASSWORD', 'admin')
    
    # Superuser varlığını kontrol et
    if User.objects.filter(is_superuser=True).exists():
        print(f"✅ Superuser zaten mevcut.")
        return
    
    try:
        # Superuser oluştur
        user = User.objects.create_superuser(
            username=superuser_username,
            email=superuser_email,
            password=superuser_password
        )
        print(f"✅ Superuser başarıyla oluşturuldu: {superuser_username}")
    except IntegrityError:
        # Kullanıcı adı zaten varsa, ama superuser değilse
        print(f"⚠️ '{superuser_username}' adında bir kullanıcı zaten var, ama superuser değil.")
        
        # Eğer aynı e-posta ile kullanıcı yoksa, farklı bir kullanıcı adıyla tekrar dene
        if not User.objects.filter(email=superuser_email).exists():
            try:
                # Farklı bir kullanıcı adı oluştur
                new_username = f"{superuser_username}_admin"
                user = User.objects.create_superuser(
                    username=new_username,
                    email=superuser_email,
                    password=superuser_password
                )
                print(f"✅ Farklı kullanıcı adıyla superuser oluşturuldu: {new_username}")
            except IntegrityError:
                print(f"❌ Alternatif kullanıcı adı ({new_username}) da zaten kullanımda.")
        else:
            print(f"❌ '{superuser_email}' e-posta adresi zaten kullanımda.")
    except Exception as e:
        print(f"❌ Superuser oluşturulurken hata oluştu: {str(e)}")

if __name__ == "__main__":
    print("🔍 Superuser varlığı kontrol ediliyor...")
    ensure_superuser() 