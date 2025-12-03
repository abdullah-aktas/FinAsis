#!/usr/bin/env python
"""Company kayıtlarını fixture dosyasına ekle"""
import json

# Encoding sorunlarını handle et
encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1', 'windows-1252']

# Company dosyasını oku
companies_data = None
for encoding in encodings:
    try:
        with open('fixtures/companies.json', 'r', encoding=encoding, errors='replace') as f:
            companies_data = json.load(f)
        print(f"✅ companies.json okundu (encoding: {encoding})")
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

if not companies_data or not users_data:
    print("❌ Dosyalar okunamadı!")
    exit(1)

# Company kayıtlarını ayır
companies = [x for x in companies_data if x['model'] == 'accounting.company']

print(f"📊 Company kayıtları: {len(companies)}")

# Mevcut users_all.json'da zaten var mı kontrol et
existing_models = {x['model'] for x in users_data}
print(f"📊 Mevcut modeller: {', '.join(sorted(existing_models))}")

# Birleştir: Önce Company, sonra diğerleri
combined = []

# 1. Company (eğer varsa ve users_all'da yoksa)
if companies and 'accounting.company' not in existing_models:
    combined.extend(companies)
    print("✅ Company kayıtları eklendi")

# 2. Diğer tüm kayıtlar
combined.extend(users_data)

# UTF-8 olarak kaydet
with open('fixtures/users_all.json', 'w', encoding='utf-8') as f:
    json.dump(combined, f, ensure_ascii=False, indent=2)

print(f"✅ Birleştirilmiş fixture kaydedildi (toplam {len(combined)} kayıt)")

# Doğrulama
with open('fixtures/users_all.json', 'r', encoding='utf-8') as f:
    json.load(f)
print("✅ JSON syntax doğrulandı")

