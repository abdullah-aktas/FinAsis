#!/bin/bash
# Güvenli fixture yükleme scripti - mevcut kayıtları atlar
# Cloud Shell'de çalıştırın

set -euo pipefail

cd ~/FinAsis || {
    echo "❌ FinAsis dizini bulunamadı!"
    exit 1
}

FIXTURE_FILE="fixtures/users_all.json"

echo "🚀 Güvenli Fixture Yükleme"
echo "=========================="
echo ""

# Fixture dosyasının varlığını kontrol et
if [ ! -f "$FIXTURE_FILE" ]; then
    echo "❌ Fixture dosyası bulunamadı: $FIXTURE_FILE"
    exit 1
fi

# Environment variables'ı ayarla
export DJANGO_SETTINGS_MODULE=config.settings

# Mevcut grupları kontrol et
echo "📊 Mevcut gruplar kontrol ediliyor..."
EXISTING_GROUPS=$(python3 manage.py shell -c "
from django.contrib.auth.models import Group
groups = Group.objects.values_list('name', flat=True)
print(','.join(groups))
" 2>/dev/null || echo "")

if [ -n "$EXISTING_GROUPS" ]; then
    echo "⚠️  Veritabanında zaten gruplar var:"
    echo "$EXISTING_GROUPS" | tr ',' '\n' | sed 's/^/  - /'
    echo ""
    echo "💡 Mevcut grupları atlayarak yüklenecek..."
fi

# Python script ile güvenli yükleme
python3 << 'PYTHON_SCRIPT'
import json
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import Group, Permission
from accounts.models import CustomUser, UserType
from django.core.management import call_command
from django.db import transaction

fixture_file = "fixtures/users_all.json"

# Fixture dosyasını oku
with open(fixture_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Mevcut grupları al
existing_groups = set(Group.objects.values_list('name', flat=True))
existing_permissions = set(Permission.objects.values_list('codename', flat=True))
existing_users = set(CustomUser.objects.values_list('username', flat=True))
existing_user_types = set(UserType.objects.values_list('code', flat=True))

print(f"📊 Mevcut kayıtlar:")
print(f"  - Gruplar: {len(existing_groups)}")
print(f"  - İzinler: {len(existing_permissions)}")
print(f"  - Kullanıcılar: {len(existing_users)}")
print(f"  - UserType'lar: {len(existing_user_types)}")
print("")

# Fixture'tan sadece yeni kayıtları filtrele
filtered_data = []

for item in data:
    model = item['model']
    fields = item['fields']
    
    if model == 'auth.group':
        name = fields.get('name')
        if name and name in existing_groups:
            print(f"  ⏭️  Group '{name}' zaten mevcut, atlanıyor")
            continue
    elif model == 'auth.permission':
        codename = fields.get('codename')
        if codename and codename in existing_permissions:
            print(f"  ⏭️  Permission '{codename}' zaten mevcut, atlanıyor")
            continue
    elif model == 'accounts.customuser':
        username = fields.get('username')
        if username and username in existing_users:
            print(f"  ⏭️  User '{username}' zaten mevcut, atlanıyor")
            continue
    elif model == 'accounts.usertype':
        code = fields.get('code')
        if code and code in existing_user_types:
            print(f"  ⏭️  UserType '{code}' zaten mevcut, atlanıyor")
            continue
    
    filtered_data.append(item)

print(f"")
print(f"📥 Yüklenecek kayıt sayısı: {len(filtered_data)} (toplam {len(data)} kayıttan)")

if len(filtered_data) == 0:
    print("✅ Yüklenecek yeni kayıt yok!")
    exit(0)

# Geçici fixture dosyası oluştur
temp_fixture = "/tmp/users_filtered.json"
with open(temp_fixture, 'w', encoding='utf-8') as f:
    json.dump(filtered_data, f, ensure_ascii=False, indent=2)

print(f"💾 Geçici fixture dosyası oluşturuldu: {temp_fixture}")
print("")

# Loaddata çalıştır
try:
    with transaction.atomic():
        call_command('loaddata', temp_fixture, verbosity=2)
    print("")
    print("✅ Fixture başarıyla yüklendi!")
except Exception as e:
    print(f"")
    print(f"❌ Hata: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
finally:
    # Geçici dosyayı temizle
    if os.path.exists(temp_fixture):
        os.remove(temp_fixture)
        print(f"🧹 Geçici dosya temizlendi")
PYTHON_SCRIPT

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 İşlem başarıyla tamamlandı!"
else
    echo ""
    echo "❌ İşlem başarısız!"
    exit 1
fi

