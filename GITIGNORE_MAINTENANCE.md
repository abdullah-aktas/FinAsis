# .gitignore Bakım Kılavuzu

## Genel Bakış
Bu kılavuz, projemizdeki `.gitignore` dosyalarının düzenli bakımı ve güncellemesi için rehber niteliğindedir.

## Dosya Yapısı
Projemizde üç farklı `.gitignore` seviyesi bulunmaktadır:

1. **Ana .gitignore**: Projenin temel ignore kuralları
2. **.gitignore.local**: Proje özelinde geliştirici ignore kuralları
3. **.gitignore_global**: Takım genelinde geçerli ignore kuralları

## Düzenli Bakım Kontrol Listesi

### Aylık Kontroller
- [ ] Yeni eklenen teknolojiler için ignore kuralları
- [ ] Kullanımdan kaldırılan teknolojilerin kurallarının temizlenmesi
- [ ] Takım üyelerinden gelen önerilerin değerlendirilmesi
- [ ] Güvenlik ile ilgili ignore kurallarının gözden geçirilmesi

### Üç Aylık Kontroller
- [ ] Tüm ignore dosyalarının tutarlılık kontrolü
- [ ] Performans optimizasyonu için kural birleştirme
- [ ] Gereksiz veya tekrar eden kuralların temizlenmesi
- [ ] Yeni güvenlik politikalarına uygunluk kontrolü

### Yıllık Kontroller
- [ ] Tüm ignore yapısının gözden geçirilmesi
- [ ] Endüstri standartlarıyla karşılaştırma
- [ ] Büyük teknoloji güncellemeleri için revizyon
- [ ] Dokümantasyon güncellemesi

## En İyi Uygulamalar

### Kural Ekleme
1. Yeni kural eklerken açıklayıcı yorum satırı ekleyin
2. Kuralın hangi teknoloji/araç için olduğunu belirtin
3. Mümkünse neden gerekli olduğunu açıklayın

### Kural Düzenleme
1. Var olan kuralları silmeden önce takımla görüşün
2. Değişiklikleri commit mesajında detaylı açıklayın
3. Büyük değişiklikleri aşamalı olarak yapın

### Güvenlik Kontrolleri
1. Hassas dosyaların kesinlikle ignore edildiğinden emin olun
2. Güvenlik açığı oluşturabilecek dosyaları kontrol edin
3. Sertifika ve anahtar dosyalarının kurallara dahil olduğunu doğrulayın

## Otomatik Kontroller

### Pre-commit Hook'ları
```bash
#!/bin/bash
# .git/hooks/pre-commit

# .gitignore dosyalarının sözdizimi kontrolü
git check-ignore --no-index * > /dev/null 2>&1

# Hassas dosya kontrolü
git ls-files | grep -i "secret\|password\|key" > /dev/null 2>&1
```

### CI/CD Kontrolleri
```yaml
# .github/workflows/gitignore-check.yml
name: GitIgnore Check
on: [push, pull_request]
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Check .gitignore syntax
        run: git check-ignore --no-index *
      - name: Check for sensitive files
        run: git ls-files | grep -i "secret\|password\|key"
```

## Sorun Giderme

### Sık Karşılaşılan Sorunlar
1. **Kural Çakışmaları**: Farklı seviyelerdeki ignore dosyaları arasındaki çakışmalar
2. **Performans Sorunları**: Çok fazla veya verimsiz kural kullanımı
3. **Eksik Kurallar**: Yeni eklenen teknolojiler için eksik kurallar

### Çözüm Önerileri
1. Düzenli olarak `git status` kontrolü yapın
2. `git check-ignore -v [dosya_adı]` ile kural kaynaklarını kontrol edin
3. Sorunlu kuralları geçici olarak devre dışı bırakıp test edin

## İletişim ve Geri Bildirim
- Yeni kural önerileri için issue açın
- Sorunları takım toplantılarında görüşün
- Düzenli olarak geri bildirim toplayın

## Kaynaklar
- [Git Dokümantasyonu](https://git-scm.com/docs/gitignore)
- [GitHub .gitignore Şablonları](https://github.com/github/gitignore)
- [GitLab .gitignore Kılavuzu](https://docs.gitlab.com/ee/development/gitignore.html) 