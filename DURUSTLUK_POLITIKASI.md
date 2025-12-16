# FinAsis Dürüstlük ve Doğruluk Politikası

## 🎯 Prensip

**"FinAsis'in hiçbir yerinde gerçeği yansıtmayan veri olmasın. Kullanıcıları aldatmasın. Doğru bilgi ve dürüstlük prensibimizdir."**

## 📋 Kapsam

Bu politika aşağıdaki alanları kapsar:
- Kullanıcı arayüzü metinleri
- Veritabanı kayıtları
- API yanıtları
- Raporlar ve analitikler
- E-posta ve bildirimler
- Dokümantasyon
- Demo/test verileri

## ✅ İzin Verilenler

1. **Test Ortamı Verileri:**
   - Sadece `DEBUG=True` ve test ortamlarında
   - Açıkça "TEST" veya "DEMO" etiketi ile işaretlenmiş
   - Production'a asla deploy edilmemeli

2. **Gerçek Veri Örnekleri:**
   - Kullanıcının kendi gerçek verileri
   - Anonimleştirilmiş gerçek veriler (izin ile)
   - Açıkça belirtilmiş örnek senaryolar

## ❌ Yasak Olanlar

1. **Sahte/Placeholder Veriler:**
   - Production'da demo/test verileri
   - "Örnek" olarak sunulan gerçek olmayan veriler
   - Kullanıcıyı yanıltabilecek placeholder metinler

2. **Yanıltıcı Bilgiler:**
   - Gerçek olmayan istatistikler
   - Sahte başarı hikayeleri
   - Gerçek olmayan referanslar

3. **Belirsiz Durumlar:**
   - Gerçek mi test mi belli olmayan veriler
   - Etiketlenmemiş demo içerikler

## 🔍 Kontrol Listesi

### Kod İncelemesi
- [ ] Demo/test verileri sadece test ortamında
- [ ] Production'da placeholder yok
- [ ] Tüm örnek veriler açıkça etiketlenmiş
- [ ] Kullanıcıya gösterilen veriler gerçek

### Veritabanı
- [ ] Production DB'de demo kullanıcı yok
- [ ] Test verileri ayrı veritabanında
- [ ] Gerçek olmayan şirket/müşteri kayıtları yok

### Arayüz
- [ ] Placeholder metinler gerçek bilgi veriyor
- [ ] "Örnek" içerikler açıkça belirtilmiş
- [ ] Kullanıcı gerçek verilerini görüyor

### API
- [ ] API yanıtları gerçek veri döndürüyor
- [ ] Mock yanıtlar sadece test'te
- [ ] Production'da sahte veri yok

## 🛠️ Uygulama

### Development
- Test verileri `setup_test_environment.py` ile oluşturulur
- Sadece `DEBUG=True` ve test ortamlarında çalışır
- Production'a deploy edilmez

### Production
- Sadece gerçek kullanıcı verileri
- Demo/test verileri tamamen kaldırılır
- Tüm placeholder'lar gerçek verilerle değiştirilir

### Code Review
- Her PR'da dürüstlük politikası kontrol edilir
- Demo/test verileri production'a giremez
- Placeholder'lar gerçek verilerle değiştirilir

## 📝 Örnekler

### ❌ YANLIŞ
```python
# Production'da demo veri
company = Company.objects.create(
    name="Örnek Şirket",  # ❌ Gerçek değil
    tax_number="1234567890"  # ❌ Sahte
)
```

### ✅ DOĞRU
```python
# Sadece test ortamında
if settings.DEBUG:
    company = Company.objects.create(
        name="TEST - Demo Şirket",  # ✅ Açıkça etiketlenmiş
        tax_number="TEST1234567890"  # ✅ Test verisi
    )
```

## 🚨 İhlal Durumunda

1. Hemen düzeltilir
2. Kullanıcılar bilgilendirilir
3. Politika güncellenir
4. Tekrarını önlemek için önlemler alınır

## 📞 Sorumluluk

- **Geliştiriciler:** Kod review'da kontrol eder
- **QA:** Test sırasında kontrol eder
- **DevOps:** Production deploy'da kontrol eder
- **Product:** Kullanıcı deneyiminde kontrol eder

---

**Son Güncelleme:** 2025-01-XX  
**Versiyon:** 1.0  
**Onaylayan:** FinAsis Yönetim Ekibi

