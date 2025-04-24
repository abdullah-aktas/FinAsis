# FinAsis Canlı Ortam Kontrol Listesi

Bu belge, FinAsis projesinin canlı ortama alınmadan önce kontrol edilmesi gereken konuları içerir.

## 1. MVT Yapısı Kontrolleri

*Bu bölümde, Model-View-Template (MVT) yapısına ilişkin kontroller bulunur.*

- [ ] Tüm modül `AppConfig` sınıfları kontrol edildi ve düzeltildi (`name` değerleri doğru ayarlandı)
  - Düzeltilmesi gereken modüller: `assets`, `checks`, `hr_management`, `integrations`, `seo`, `stock_management`
- [ ] Tüm modül URL tanımları kontrol edildi ve dosyaları oluşturuldu
  - Eksik URL modülleri: `hr_management`, `stock_management`
- [ ] Tüm modüllerin template dizinleri kontrol edildi ve eksikler tamamlandı 
  - Eksik Template dizinleri: `assets`, `checks`, `hr_management`, `seo`, `stock_management`
- [ ] Eksik view tanımları oluşturuldu (41 eksik view)
- [ ] Eksik template dosyaları oluşturuldu (102 eksik template)
- [ ] API versiyonlama kontrol edildi ve yapılandırıldı
- [ ] GraphQL endpoint'leri kontrol edildi (varsa)
- [ ] WebSocket bağlantıları kontrol edildi
- [ ] Middleware zinciri optimize edildi
- [ ] Signal handlers kontrol edildi
- [ ] Celery task'ları kontrol edildi

## 2. Güvenlik Kontrolleri

*Bu bölümde, güvenlik ile ilgili kontroller bulunur.*

- [ ] `DEBUG = False` ayarlandı (`settings/prod.py` içinde)
- [ ] `SECRET_KEY` güvenli ve ortama özgü bir değer olarak ayarlandı
- [ ] `ALLOWED_HOSTS` doğru yapılandırıldı (sadece izin verilen host'lar)
- [ ] SSL/TLS sertifikaları hazırlandı ve yapılandırıldı
- [ ] CSRF koruması aktif ve doğru yapılandırıldı
- [ ] API rate limiting kontrol edildi
- [ ] Giriş denemesi sınırlaması aktif
- [ ] Oturum zaman aşımı süresi kontrol edildi
- [ ] Hassas bilgilerin loglanması engellendi
- [ ] Güvenlik başlıkları yapılandırıldı (Content-Security-Policy, X-XSS-Protection, X-Frame-Options)
- [ ] Django admin URL'i özelleştirildi
- [ ] Kullanıcı yetkilendirme sistemi kontrol edildi
- [ ] Dosya yükleme kısıtlamaları yapılandırıldı
- [ ] OWASP Top 10 güvenlik açıkları kontrol edildi
- [ ] Dependency check (güvenlik açığı taraması) yapıldı
- [ ] Penetrasyon testi yapıldı
- [ ] API güvenlik testleri yapıldı
- [ ] JWT token yönetimi kontrol edildi
- [ ] 2FA (İki Faktörlü Doğrulama) kontrol edildi
- [ ] Güvenlik duvarı kuralları kontrol edildi

## 3. Veritabanı Kontrolleri

*Bu bölümde, veritabanı ile ilgili kontroller bulunur.*

- [ ] Tüm modellerin migrasyonları oluşturuldu ve uygulandı
- [ ] Veritabanı bağlantı ayarları kontrol edildi
- [ ] Veritabanı kullanıcı adı ve şifresi güvenli
- [ ] Veritabanı yedekleme planı oluşturuldu
- [ ] Veritabanı indeksleri optimize edildi
- [ ] Veritabanı bağlantı havuzu yapılandırıldı (`CONN_MAX_AGE`)
- [ ] Atomik işlemler kontrol edildi
- [ ] Büyük veri kümeleri için sayfalama yapılandırıldı
- [ ] Gereksiz model alanları temizlendi
- [ ] Veritabanı replikasyonu kontrol edildi
- [ ] Veritabanı şifreleme kontrol edildi
- [ ] Veritabanı performans metrikleri tanımlandı
- [ ] Veritabanı yedekleme ve geri yükleme testleri yapıldı
- [ ] Veritabanı sürüm kontrolü yapıldı
- [ ] Veritabanı izleme sistemi kuruldu

## 4. Performans Kontrolleri

*Bu bölümde, performans ile ilgili kontroller bulunur.*

- [ ] Statik dosyalar toplandı (`collectstatic`)
- [ ] Media dosyaları için depolama yapılandırıldı
- [ ] Önbellek yapılandırıldı (Redis veya Memcached)
- [ ] Statik dosya sıkıştırma etkin (WhiteNoise veya benzeri)
- [ ] Veritabanı sorguları optimize edildi
- [ ] Gereksiz N+1 sorguları giderildi
- [ ] Template önbelleği kontrol edildi
- [ ] CDN yapılandırması kontrol edildi (gerekirse)
- [ ] Resim boyutları optimize edildi
- [ ] JavaScript/CSS küçültme yapılandırıldı
- [ ] Yük testi yapıldı ve sonuçları değerlendirildi
- [ ] API response time optimizasyonu yapıldı
- [ ] Lazy loading kontrol edildi
- [ ] Code splitting yapılandırıldı
- [ ] Service Worker yapılandırması kontrol edildi
- [ ] Progressive Web App (PWA) performansı kontrol edildi
- [ ] Core Web Vitals metrikleri optimize edildi

## 5. Hata Yakalama ve Loglama

*Bu bölümde, hata yakalama ve loglama ile ilgili kontroller bulunur.*

- [ ] Hata yakalama mekanizması yapılandırıldı
- [ ] 404 ve 500 hata sayfaları özelleştirildi
- [ ] Loglama yapılandırıldı ve dosya rotasyonu etkinleştirildi
- [ ] Log dosyalarının konumu ve erişim izinleri kontrol edildi
- [ ] Kritik hatalar için bildirim sistemi kuruldu (e-posta, SMS vb.)
- [ ] Hata raporlama servisi entegre edildi (Sentry veya benzeri)
- [ ] Exception middleware yapılandırıldı
- [ ] API hata yanıtları standardize edildi
- [ ] Distributed tracing yapılandırıldı
- [ ] Log aggregation sistemi kuruldu
- [ ] Log analiz ve görselleştirme araçları entegre edildi
- [ ] Audit logging yapılandırıldı
- [ ] Log retention politikası belirlendi

## 6. Dağıtım ve Altyapı

*Bu bölümde, dağıtım ve altyapı ile ilgili kontroller bulunur.*

- [ ] Sunucu gereksinimleri kontrol edildi
- [ ] WSGI/ASGI yapılandırması kontrol edildi (Gunicorn, uWSGI vb.)
- [ ] Nginx/Apache yapılandırması kontrol edildi
- [ ] Statik ve media dosyalarının sunulması kontrol edildi
- [ ] Docker imajları güncel ve optimize edildi
- [ ] Docker Compose yapılandırması kontrol edildi
- [ ] Kubernetes yapılandırması kontrol edildi (gerekirse)
- [ ] Ölçeklendirme stratejisi belirlendi
- [ ] CI/CD pipeline kontrol edildi
- [ ] Yedeklilik (redundancy) kontrol edildi
- [ ] Otomatik ölçeklendirme yapılandırıldı (gerekirse)
- [ ] Envanter yönetimi yapılandırıldı
- [ ] Infrastructure as Code (IaC) kontrol edildi
- [ ] Cloud provider yapılandırması kontrol edildi
- [ ] Load balancing yapılandırması kontrol edildi
- [ ] Disaster recovery planı hazırlandı
- [ ] Zero-downtime deployment stratejisi belirlendi

## 7. Kullanıcı Deneyimi ve Son Kontroller

*Bu bölümde, kullanıcı deneyimi ve son kontroller bulunur.*

- [ ] Tüm sayfalar ve formlar test edildi
- [ ] Responsive tasarım kontrol edildi
- [ ] Tarayıcı uyumluluğu test edildi
- [ ] Erişilebilirlik standartları kontrol edildi
- [ ] Çoklu dil desteği kontrol edildi
- [ ] Progressive Web App (PWA) özellikleri kontrol edildi
- [ ] Sayfa yükleme hızı ölçüldü ve optimize edildi
- [ ] SEO ayarları kontrol edildi
- [ ] Analiz araçları entegre edildi (Google Analytics vb.)
- [ ] Sosyal medya meta etiketleri kontrol edildi
- [ ] Arama motoru dostu URL'ler kontrol edildi
- [ ] Kullanım kılavuzu hazırlandı
- [ ] Sistem dokümantasyonu güncellendi
- [ ] Kullanıcı geri bildirim mekanizması kuruldu
- [ ] A/B test altyapısı hazırlandı
- [ ] Kullanıcı davranış analizi yapılandırıldı
- [ ] Kullanıcı segmentasyonu kontrol edildi

## 8. İzleme ve Bakım

*Bu bölümde, izleme ve bakım ile ilgili kontroller bulunur.*

- [ ] İzleme sistemleri kuruldu (Prometheus, Grafana vb.)
- [ ] Uyarı sistemleri yapılandırıldı
- [ ] Performans metrikleri tanımlandı
- [ ] Düzenli yedekleme sistemi kuruldu
- [ ] Güvenlik güncellemeleri için plan oluşturuldu
- [ ] Bakım modu yapılandırıldı
- [ ] Servis durumu sayfası hazırlandı
- [ ] Kullanıcı geribildirimi toplamak için mekanizmalar kuruldu
- [ ] Kesinti bildirimleri için plan oluşturuldu
- [ ] Düzenli bakım takvimi oluşturuldu
- [ ] SLA (Service Level Agreement) metrikleri tanımlandı
- [ ] Incident response planı hazırlandı
- [ ] Capacity planning yapıldı
- [ ] Cost optimization kontrol edildi

## 9. Yasal ve Uyumluluk Kontrolleri

*Bu bölümde, yasal ve uyumluluk ile ilgili kontroller bulunur.*

- [ ] KVKK/GDPR uyumluluğu kontrol edildi
- [ ] Çerez politikası hazırlandı
- [ ] Gizlilik politikası hazırlandı
- [ ] Kullanım şartları hazırlandı
- [ ] Telif hakkı bildirimleri kontrol edildi
- [ ] Lisans uyumluluğu kontrol edildi
- [ ] Finansal düzenlemelere uygunluk kontrol edildi
- [ ] Veri saklama politikası belirlendi
- [ ] Veri silme politikası belirlendi
- [ ] Veri transfer politikası belirlendi

## Notlar

- Bu liste kapsamlı bir kontrol listesi olmakla birlikte, projenin ihtiyaçlarına göre özelleştirilebilir.
- Her madde için sorumlu kişi ve tamamlanma tarihi belirlenmelidir.
- Canlıya geçiş öncesi bir toplantı düzenlenerek bu liste gözden geçirilmelidir.
- Canlıya geçiş sonrası için bir izleme planı oluşturulmalıdır.
- Sorun durumunda geri alma (rollback) planı hazırlanmalıdır.
- Her madde için öncelik seviyesi belirlenmelidir (Kritik, Yüksek, Orta, Düşük).
- Her madde için test senaryoları hazırlanmalıdır.
- Her madde için dokümantasyon gereksinimleri belirlenmelidir.

## Son Kontrol

Projeyi canlıya almadan önce, şu komutları çalıştırarak kontrolleri yapınız:

```bash
# MVT yapısı kontrolü
python mvt_checker.py

# Django kontrol mekanizması
python manage.py check --deploy

# Güvenlik taraması
python manage.py check --deploy --settings=settings.prod

# Performans testi
python manage.py test --settings=settings.prod

# Dependency check
safety check

# Code quality check
flake8 .
black --check .
isort --check-only .

# Test coverage
pytest --cov=. --cov-report=html
```

## Rollback Planı

1. Veritabanı yedeği alın
2. Kod versiyonu yedeği alın
3. Rollback senaryoları hazırlanmış olmalı
4. Rollback testleri yapılmış olmalı
5. Rollback süresi belirlenmiş olmalı
6. Rollback sorumluları belirlenmiş olmalı 