# Canlı Ortama Değişiklik Aktarma Kılavuzu

## 🚀 Hızlı Deploy Komutu (Tek Komut)

Cloud Shell'de çalıştırın:

```bash
cd ~/FinAsis && git pull origin main && echo "✅ Değişiklikler alındı!"
```

## 📋 Adım Adım Deploy Süreci

### 1. Cloud Shell'e Bağlanın

```bash
# Google Cloud Shell'i açın
# Otomatik olarak proje dizinine gideceksiniz
```

### 2. Proje Dizinine Geçin

```bash
cd ~/FinAsis
```

### 3. Son Değişiklikleri Alın

```bash
# Ana branch'ten son değişiklikleri çek
git pull origin main
```

### 4. (Opsiyonel) Değişiklikleri Kontrol Edin

```bash
# Son commit'leri göster
git log --oneline -5

# Değişen dosyaları göster
git diff HEAD~1 HEAD --name-only
```

### 5. (Opsiyonel) Migration Gerekirse

```bash
# Veritabanı migration'ları uygula
python manage.py migrate

# Yeni static dosyalar varsa
python manage.py collectstatic --noinput
```

## 🔄 Tam Deploy Script'i

Aşağıdaki script'i `deploy.sh` olarak kaydedip kullanabilirsiniz:

```bash
#!/bin/bash
# FinAsis Canlı Ortam Deploy Script

set -e  # Hata durumunda dur

echo "🚀 FinAsis Deploy Başlatılıyor..."

# Proje dizinine geç
cd ~/FinAsis || { echo "❌ FinAsis dizini bulunamadı!"; exit 1; }

# Git durumunu kontrol et
echo "📊 Git durumu kontrol ediliyor..."
git status

# Son değişiklikleri al
echo "⬇️  Son değişiklikler alınıyor..."
git pull origin main

# Migration kontrolü
echo "🗄️  Migration'lar kontrol ediliyor..."
python manage.py migrate --check || python manage.py migrate

# Static dosyalar (eğer varsa)
echo "📦 Static dosyalar toplanıyor..."
python manage.py collectstatic --noinput || echo "⚠️  Static dosyalar toplanamadı (normal olabilir)"

echo "✅ Deploy tamamlandı!"
echo "📝 Son commit: $(git log -1 --oneline)"
```

## 📝 Kullanım

### Script'i Çalıştırılabilir Yapın

```bash
chmod +x deploy.sh
```

### Script'i Çalıştırın

```bash
./deploy.sh
```

## 🎯 En Basit Yöntem (Önerilen)

Her zaman kullanabileceğiniz tek komut:

```bash
cd ~/FinAsis && git pull origin main
```

## ⚠️ Önemli Notlar

1. **Migration'lar**: Eğer yeni migration dosyaları varsa, `python manage.py migrate` çalıştırmanız gerekebilir.

2. **Static Dosyalar**: Yeni CSS/JS dosyaları eklendiyse, `python manage.py collectstatic` çalıştırmanız gerekebilir.

3. **Servis Yeniden Başlatma**: Cloud Run kullanıyorsanız, genellikle otomatik yeniden başlar. Manuel kontrol için:
   ```bash
   gcloud run services list
   ```

4. **Hata Durumunda**: Eğer bir hata alırsanız:
   ```bash
   # Son commit'i geri al
   git reset --hard HEAD~1
   
   # Veya belirli bir commit'e dön
   git reset --hard <commit-hash>
   ```

## 🔍 Değişiklikleri Kontrol Etme

```bash
# Son 5 commit'i göster
git log --oneline -5

# Belirli bir dosyanın değişikliklerini göster
git diff HEAD~1 HEAD -- path/to/file.py

# Tüm değişen dosyaları listele
git diff --name-only HEAD~1 HEAD
```

## 📌 Hızlı Referans

| İşlem | Komut |
|-------|-------|
| Son değişiklikleri al | `cd ~/FinAsis && git pull origin main` |
| Migration uygula | `python manage.py migrate` |
| Static dosyaları topla | `python manage.py collectstatic --noinput` |
| Son commit'leri gör | `git log --oneline -5` |
| Değişen dosyaları gör | `git diff --name-only HEAD~1 HEAD` |

---

**Son Güncelleme**: 2025-01-15

