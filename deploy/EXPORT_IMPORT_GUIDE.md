# 📦 Yerel SQLite → Cloud SQL Veri Taşıma Kılavuzu

Bu kılavuz, yereldeki SQLite veritabanındaki tüm verileri canlı ortama (Cloud SQL / PostgreSQL) taşımak için adım adım talimatlar içerir.

---

## 🟩 **Yöntem 1: Tüm Veriyi Taşıma (Önerilen)**

### Adım 1: Yerelde Export

**PowerShell'de:**
```powershell
python manage.py dumpdata `
  --exclude=contenttypes `
  --exclude=auth.permission `
  --exclude=games.ticaretin_izinde `
  --natural-primary `
  --natural-foreign `
  --indent=2 `
  --output=full_data.json
```

**Bash/Linux'ta:**
```bash
python manage.py dumpdata \
  --exclude=contenttypes \
  --exclude=auth.permission \
  --exclude=games.ticaretin_izinde \
  --natural-primary \
  --natural-foreign \
  --indent=2 \
  --output=full_data.json
```

**Veya script ile:**
```bash
chmod +x deploy/export_local_to_production.sh
./deploy/export_local_to_production.sh
```

### Adım 2: Dosyayı Cloud Shell'e Yükle

1. `full_data.json` dosyasını Cloud Shell'e yükleyin
2. Veya Cloud Shell'de `git clone` yapıp dosyayı manuel olarak yükleyin

### Adım 3: Cloud Shell'de Import

```bash
cd ~/FinAsis

# Script'i çalıştırılabilir yap
chmod +x deploy/import_to_production.sh

# Import script'ini çalıştır
./deploy/import_to_production.sh
```

---

## 🟦 **Yöntem 2: Sadece Kullanıcıları Taşıma**

### Export (Yerelde):
```bash
python manage.py dumpdata accounts.customuser --natural-primary --indent=2 --output=users.json
```

### Import (Cloud Shell'de):
```bash
python3 manage.py loaddata users.json
```

---

## 🟧 **Yöntem 3: Belirli App'leri Taşıma**

### Örnek: Sadece accounting app'i
```bash
python manage.py dumpdata accounting --natural-primary --natural-foreign --indent=2 --output=accounting_data.json
```

### Import:
```bash
python3 manage.py loaddata accounting_data.json
```

---

## ⚠️ **ÖNEMLİ GÜVENLİK NOTLARI**

1. **`full_data.json` dosyasını GitHub'a push ETMEYİN!**
   - İçinde şifre hashleri, kullanıcı bilgileri, hassas veriler olabilir
   - `.gitignore` dosyasına ekleyin: `full_data.json`

2. **Dosyayı kullandıktan sonra silin:**
   ```bash
   rm full_data.json
   ```

3. **Cloud SQL şifresini güvenli tutun**

---

## 🔧 **Sorun Giderme**

### Hata: "no such table: ticaretin_izinde_ursinagame"
**Çözüm:** `--exclude=games.ticaretin_izinde` parametresini ekleyin

### Hata: "UNIQUE constraint failed"
**Çözüm:** `--natural-primary --natural-foreign` parametrelerini kullanın

### Hata: "File too large"
**Çözüm:** App'lere göre bölerek export edin:
```bash
python manage.py dumpdata accounts --output=accounts.json
python manage.py dumpdata accounting --output=accounting.json
# ... vs
```

---

## 📊 **Export Parametreleri Açıklaması**

| Parametre | Açıklama |
|-----------|----------|
| `--exclude=contenttypes` | Content types çakışmalarını önler |
| `--exclude=auth.permission` | Permission çakışmalarını önler |
| `--exclude=games.ticaretin_izinde` | Eksik tabloları olan app'i exclude eder |
| `--natural-primary` | Primary key'leri doğal formatta kullanır |
| `--natural-foreign` | Foreign key'leri doğal formatta kullanır |
| `--indent=2` | JSON formatını okunabilir yapar |
| `--output=full_data.json` | Çıktı dosyasını belirtir |

---

## ✅ **Hızlı Başlangıç**

1. **Yerelde export:**
   ```bash
   ./deploy/export_local_to_production.sh
   ```

2. **Dosyayı Cloud Shell'e yükle**

3. **Cloud Shell'de import:**
   ```bash
   ./deploy/import_to_production.sh
   ```

Bu kadar! 🎉

