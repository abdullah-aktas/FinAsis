# Hızlı Encoding Düzeltme - Cloud Shell

## ⚡ Tek Komut Çözümü

Cloud Shell'de şu komutları sırayla çalıştırın:

```bash
cd ~/FinAsis

# 1. Git sorununu çöz ve güncellemeleri al
git stash
git pull origin main

# 2. Encoding düzeltme scriptini çalıştır
chmod +x deploy/fix_fixture_encoding.sh
./deploy/fix_fixture_encoding.sh

# 3. Fixture dosyasını yükle
python3 manage.py loaddata fixtures/users_all.json --verbosity=2
```

## 🔧 Manuel Düzeltme (Script yoksa)

Eğer script hala yoksa, manuel olarak:

```bash
cd ~/FinAsis

# Git güncelle
git stash
git pull origin main

# Encoding'i düzelt
python3 << 'EOF'
import json
import sys

fixture_file = "fixtures/users_all.json"
encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1', 'windows-1252']

data = None
for encoding in encodings:
    try:
        with open(fixture_file, 'r', encoding=encoding, errors='replace') as f:
            data = json.load(f)
        print(f"✅ Okundu: {encoding}")
        break
    except:
        continue

if data:
    with open(fixture_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("✅ UTF-8'e dönüştürüldü")
    
    # Doğrulama
    with open(fixture_file, 'r', encoding='utf-8') as f:
        json.load(f)
    print("✅ JSON doğrulandı")
else:
    print("❌ Dosya okunamadı!")
    sys.exit(1)
EOF

# Yükle
python3 manage.py loaddata fixtures/users_all.json --verbosity=2
```

