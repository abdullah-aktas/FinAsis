# Permissions Modülü

Bu modül, FinAsis projesinde rol tabanlı erişim ve yetkilendirme işlemlerini yönetir. Kullanıcı, rol ve özel yetki ilişkilerini esnek şekilde tanımlar ve yönetir.

## Temel Modeller
- **Permission:** Özel yetki tanımı. Django native Permission ile eşleşebilir.
- **Role:** Roller ve hiyerarşik yapı (parent-child). Rollere birden fazla yetki atanabilir.
- **UserRole:** Kullanıcı ve rol ilişkisi.
- **UserPermission:** Kullanıcıya doğrudan yetki atama (opsiyonel).

## Web Arayüzü
Tüm modeller için CRUD işlemleri (listele, detay, oluştur, güncelle, sil) desteklenir. Template dosyaları Bootstrap uyumludur.

### Örnek URL'ler
- Yetkiler: `/permissions/permissions/`
- Roller: `/permissions/roles/`
- Kullanıcı Rolleri: `/permissions/user-roles/`

## API Endpointleri
REST API ile tüm işlemler yapılabilir. DRF ViewSet yapısı kullanılmıştır.

- Yetkiler: `/permissions/api/permissions/`
- Roller: `/permissions/api/roles/`
- Kullanıcı Rolleri: `/permissions/api/user-roles/`
- Kullanıcı Yetkileri: `/permissions/api/user-permissions/`

### API Örnekleri
- Yetki oluşturma (POST): `/permissions/api/permissions/`
- Rol güncelleme (PUT): `/permissions/api/roles/<id>/`
- Kullanıcıya rol atama (POST): `/permissions/api/user-roles/`

## Yetkilendirme
- Tüm view'lar ve endpoint'ler için uygun Django permission kontrolleri yapılır.
- Sadece yetkili kullanıcılar ilgili işlemleri görebilir/gerçekleştirebilir.

## Sinyaller
- Yetki, rol ve kullanıcı rolü işlemlerinde otomatik güncellemeler ve audit log için signals kullanılır.

## Yönetim Paneli
- Tüm modeller admin paneline eklenmiştir. Sadece aktif olanlar listelenir.

## Geliştirici Notları
- Tüm template dosyaları `templates/permissions/` altında bulunur.
- API için DRF kullanılmıştır.
- Gelişmiş arama, filtreleme ve sıralama desteklenir.

---
Daha fazla bilgi için kodu inceleyebilir veya ilgili view/serializer dosyalarına bakabilirsiniz. 