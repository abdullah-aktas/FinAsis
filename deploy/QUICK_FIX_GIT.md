# Git Pull Sorunu Çözümü

Cloud Shell'de şu komutları sırayla çalıştırın:

```bash
cd ~/FinAsis

# 1. Yerel değişiklikleri at
git restore deploy/test_health_urls_simple.sh

# 2. Eğer hala sorun varsa, tüm değişiklikleri at
git restore .

# 3. Stash yap (eğer restore çalışmazsa)
git stash

# 4. Pull yap
git pull origin main

# 5. Deploy et
gcloud builds submit --config cloudbuild.yaml
```

## Tek Komut Çözümü

```bash
cd ~/FinAsis && git restore . && git stash && git pull origin main && gcloud builds submit --config cloudbuild.yaml
```

