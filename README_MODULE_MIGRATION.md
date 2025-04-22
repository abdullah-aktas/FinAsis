# FinAsis Modül Taşıma Projesi

Bu proje, FinAsis uygulamasındaki modülleri `apps/` dizininden ana dizine taşımak için oluşturulmuştur. Bu belge, taşıma sürecini ve yapılan değişiklikleri açıklar.

## Genel Bakış

FinAsis projesi, Django tabanlı bir web uygulamasıdır. Bu taşıma işlemi, modülleri daha bağımsız ve yönetilebilir hale getirmek amacıyla gerçekleştirilmiştir.

## Mevcut Durum

Taşıma işlemi kısmen tamamlanmıştır:

- **Ana dizine taşınan modüller**: 45 modül
- **Hala apps/ dizininde kalan modüller**: 22 modül

## Tamamlanan İşlemler

1. Çoğu modül apps/ dizininden ana dizine taşınmıştır
2. settings.py dosyasındaki INSTALLED_APPS listesi güncellenmiştir
3. URL pattern'leri güncellenmiştir
4. Bazı modüllerin apps.py dosyalarındaki name değerleri güncellenmiştir

## Yapılması Gereken İşlemler

1. Kalan 22 modülün apps/ dizininden ana dizine taşınması:
   - `python migrate_modules.py` komutunu yeniden çalıştırın
   - Ya da her bir modülü manuel olarak taşıyın

2. INSTALLED_APPS listesindeki tüm uygulamaların kontrol edilmesi:
   - `python update_settings.py` komutunu yeniden çalıştırın

3. URL pattern'lerinin güncellenmesi:
   - `python update_urls.py` komutunu yeniden çalıştırın

4. Tüm import ifadelerinin güncellenmesi:
   - Sorunlu dosyaları tespit etmek için uygulamayı çalıştırın
   - Hata veren import ifadelerini manuel olarak düzeltin

## Taşıma Araçları

Bu projede kullanılan taşıma araçları şunlardır:

- **migrate_modules.py**: Modülleri taşır ve import ifadelerini günceller
- **update_settings.py**: settings.py dosyasını günceller
- **update_urls.py**: URL pattern'lerini günceller
- **generate_summary.py**: Taşıma işlemi sonrası bir özet rapor oluşturur

## Geri Dönüş Planı

Sorun yaşanması durumunda aşağıdaki adımları izleyin:

1. `apps_backup_XXXXXXXX` dizinindeki yedek dosyaları kullanarak eski yapıya dönün
2. Değişiklikleri revert edin veya başka bir branch'e geçin

## Test

Taşıma işlemi tamamlandıktan sonra:

1. Veritabanı migrasyonlarının çalıştığından emin olun:
   ```
   python manage.py migrate --check
   ```

2. Development sunucusunu başlatın:
   ```
   python manage.py runserver
   ```

3. Admin paneline erişilebildiğini kontrol edin

4. Temel işlevleri test edin

## Notlar

- Modüller arası bağımlılıklar sorun çıkarabilir, dikkatle test edin
- Taşıma işlemi sırasında bazı Python dosyaları `'utf-8' codec can't decode byte 0xfd in position 9: invalid start byte` hatası verdi, bu dosyalar için manuel müdahale gerekebilir
- Bazı __init__.py dosyaları yeniden oluşturulmalı

## İletişim

Sorun yaşarsanız geliştirici ekibine başvurun. 