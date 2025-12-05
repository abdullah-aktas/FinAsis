# Dumpdata Komutu Kullanım Kılavuzu

## Sorun: `ticaretin_izinde_ursinagame` Tablosu Bulunamıyor

Eğer `dumpdata` komutu çalıştırırken şu hatayı alıyorsanız:

```
CommandError: Unable to serialize database: no such table: ticaretin_izinde_ursinagame
```

Bu, `games.ticaretin_izinde` app'indeki modellerin veritabanında tablolarının olmadığı anlamına gelir.

## Çözüm: App'i Exclude Et

### PowerShell'de:

```powershell
python manage.py dumpdata `
  --exclude=contenttypes `
  --exclude=auth.permission `
  --exclude=games.ticaretin_izinde `
  --indent=2 `
  --output=full_data.json
```

### Bash/Linux'ta:

```bash
python manage.py dumpdata \
  --exclude=contenttypes \
  --exclude=auth.permission \
  --exclude=games.ticaretin_izinde \
  --indent=2 \
  --output=full_data.json
```

## Alternatif: Belirli App'leri Dahil Et

Sadece belirli app'lerin verilerini almak için:

```bash
python manage.py dumpdata \
  accounts \
  accounting \
  finance \
  --indent=2 \
  --output=specific_data.json
```

## Tüm App'leri Exclude Et (Sadece Seçilenler)

```bash
python manage.py dumpdata \
  accounts \
  accounting \
  finance \
  --exclude=contenttypes \
  --exclude=auth.permission \
  --indent=2 \
  --output=selected_data.json
```

## Notlar

- `--exclude=contenttypes`: Content types tablosunu exclude eder (genellikle gerekli değildir)
- `--exclude=auth.permission`: Permission'ları exclude eder (genellikle gerekli değildir)
- `--exclude=games.ticaretin_izinde`: Eksik tabloları olan app'i exclude eder
- `--indent=2`: JSON formatını okunabilir yapar
- `--output=`: Çıktı dosyasını belirtir

