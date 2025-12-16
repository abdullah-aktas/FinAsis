# Hata Çözüm Planı

## 🔴 Kritik Hatalar ve Çözümleri

### 1. `billing_plan.trial_days` sütunu mevcut değil
**Hata:** `billing_plan.trial_days` sütunu mevcut değil  
**Sebep:** Migration uygulanmamış olabilir  
**Çözüm:**
```bash
python manage.py migrate billing
```

### 2. `ticaretin_izinde_ursinagame` tablosu mevcut değil
**Hata:** relation "ticaretin_izinde_ursinagame" does not exist  
**Sebep:** Migration eksik veya uygulanmamış  
**Çözüm:**
```bash
python manage.py makemigrations games.ticaretin_izinde
python manage.py migrate games.ticaretin_izinde
```

### 3. `finquest_finquestworld` ilişkisi mevcut değil
**Hata:** "finquest_finquestworld" ilişkisi mevcut değil  
**Sebep:** Migration eksik  
**Çözüm:**
```bash
python manage.py makemigrations games.finquest
python manage.py migrate games.finquest
```

### 4. `education_studentprofile_student_number_key` unique constraint ihlali
**Hata:** Yinelenen anahtar değeri, "education_studentprofile_student_number_key" benzersiz kısıtlamasını ihlal ediyor  
**Sebep:** Aynı student_number'a sahip birden fazla kayıt var  
**Çözüm:** Duplicate kayıtları temizle veya unique constraint'i kaldır

### 5. `auth_user_change` URL pattern bulunamadı
**Hata:** 'auth_user_change' için ters işlem bulunamadı  
**Sebep:** CustomUser kullanılıyor, auth.User değil  
**Çözüm:** `admin:accounts_customuser_change` kullan

### 6. Template hataları
**Hatalar:**
- Geçersiz blok etiketi: 'endblock'
- 'crispy_forms_tags' kayıtlı bir etiket kütüphanesi değil
- 'userprofile' anahtar kelimesi alana çözümlenemiyor

**Çözüm:** Template'leri düzelt

### 7. Eksik template
**Hata:** öğrenci/kontrol paneli.html mevcut değil  
**Çözüm:** Template'i oluştur

