#!/usr/bin/env python
"""Fixture dosyalarını birleştirme scripti"""
import json

# Encoding sorunlarını handle et
encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1', 'windows-1252']

# UserType dosyasını oku
user_types_data = None
for encoding in encodings:
    try:
        with open('fixtures/user_types.json', 'r', encoding=encoding, errors='replace') as f:
            user_types_data = json.load(f)
        print(f"✅ user_types.json okundu (encoding: {encoding})")
        break
    except:
        continue

# Users dosyasını oku
users_data = None
for encoding in encodings:
    try:
        with open('fixtures/users_all.json', 'r', encoding=encoding, errors='replace') as f:
            users_data = json.load(f)
        print(f"✅ users_all.json okundu (encoding: {encoding})")
        break
    except:
        continue

if not user_types_data or not users_data:
    print("❌ Dosyalar okunamadı!")
    exit(1)

# UserType ve SubscriptionType kayıtlarını ayır
user_types = [x for x in user_types_data if x['model'] == 'accounts.usertype']
subscription_types = [x for x in user_types_data if x['model'] == 'accounts.subscriptiontype']

print(f"📊 UserType kayıtları: {len(user_types)}")
print(f"📊 SubscriptionType kayıtları: {len(subscription_types)}")

# Mevcut users_all.json'da zaten var mı kontrol et
existing_models = {x['model'] for x in users_data}
print(f"📊 Mevcut modeller: {', '.join(sorted(existing_models))}")

# Birleştir: Önce SubscriptionType, sonra UserType, sonra diğerleri
combined = []

# 1. SubscriptionType (eğer varsa ve users_all'da yoksa)
if subscription_types and 'accounts.subscriptiontype' not in existing_models:
    combined.extend(subscription_types)
    print("✅ SubscriptionType kayıtları eklendi")

# 2. UserType (eğer users_all'da yoksa)
if user_types and 'accounts.usertype' not in existing_models:
    combined.extend(user_types)
    print("✅ UserType kayıtları eklendi")

# 3. Diğer tüm kayıtlar
combined.extend(users_data)

# UTF-8 olarak kaydet
with open('fixtures/users_all.json', 'w', encoding='utf-8') as f:
    json.dump(combined, f, ensure_ascii=False, indent=2)

print(f"✅ Birleştirilmiş fixture kaydedildi (toplam {len(combined)} kayıt)")

# Doğrulama
with open('fixtures/users_all.json', 'r', encoding='utf-8') as f:
    json.load(f)
print("✅ JSON syntax doğrulandı")

