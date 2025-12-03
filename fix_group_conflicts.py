#!/usr/bin/env python
"""Fixture dosyasındaki group çakışmalarını düzelt"""
import json
from collections import defaultdict

# Fixture dosyasını oku
with open('fixtures/users_all.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Group kayıtlarını bul
groups = [x for x in data if x['model'] == 'auth.group']
print(f"📊 Toplam Group kaydı: {len(groups)}")

# Name'e göre grupla
group_by_name = defaultdict(list)
for group in groups:
    name = group['fields']['name']
    group_by_name[name].append(group)

# Aynı isimde birden fazla kayıt var mı kontrol et
conflicts = {name: items for name, items in group_by_name.items() if len(items) > 1}
print(f"⚠️  Aynı isimde birden fazla group: {len(conflicts)}")

if conflicts:
    for name, items in conflicts.items():
        print(f"  - '{name}': {len(items)} adet (PK'lar: {[x['pk'] for x in items]})")
    
    # Her isim için sadece ilk kaydı tut (en düşük PK)
    name_to_keep_pk = {}
    for name, items in conflicts.items():
        # En düşük PK'ya sahip olanı tut
        keep_item = min(items, key=lambda x: x['pk'])
        name_to_keep_pk[name] = keep_item['pk']
        print(f"  ✅ '{name}' için PK {keep_item['pk']} tutulacak")
    
    # Duplicate'leri kaldır
    cleaned_data = []
    removed_pks = set()
    
    for item in data:
        if item['model'] == 'auth.group':
            name = item['fields']['name']
            if name in name_to_keep_pk:
                # Bu isim için tutulacak PK değilse, kaldır
                if item['pk'] != name_to_keep_pk[name]:
                    removed_pks.add(item['pk'])
                    print(f"  🗑️  PK {item['pk']} kaldırıldı (isim: '{name}')")
                    continue
        cleaned_data.append(item)
    
    # CustomUser kayıtlarındaki group referanslarını düzelt
    # Kaldırılan PK'ları, tutulan PK ile değiştir
    pk_mapping = {}
    for name, items in conflicts.items():
        keep_pk = name_to_keep_pk[name]
        for item in items:
            if item['pk'] != keep_pk:
                pk_mapping[item['pk']] = keep_pk
    
    fixed_users = 0
    for item in cleaned_data:
        if item['model'] == 'accounts.customuser' and 'groups' in item['fields']:
            original_groups = item['fields']['groups']
            new_groups = []
            changed = False
            for group_pk in original_groups:
                if group_pk in pk_mapping:
                    new_groups.append(pk_mapping[group_pk])
                    changed = True
                else:
                    new_groups.append(group_pk)
            
            if changed:
                # Duplicate'leri temizle
                item['fields']['groups'] = list(set(new_groups))
                fixed_users += 1
    
    print(f"✅ {fixed_users} kullanıcının group referansları düzeltildi")
    data = cleaned_data
else:
    print("✅ Group çakışması yok")

# UTF-8 olarak kaydet
with open('fixtures/users_all.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"✅ Düzeltilmiş fixture kaydedildi (toplam {len(data)} kayıt)")

# Doğrulama
with open('fixtures/users_all.json', 'r', encoding='utf-8') as f:
    json.load(f)
print("✅ JSON syntax doğrulandı")

