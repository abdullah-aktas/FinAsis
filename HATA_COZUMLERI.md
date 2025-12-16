# Hata Çözümleri - Uygulanan Düzeltmeler

## ✅ Çözülen Hatalar

### 1. ✅ `ticaretin_izinde_ursinagame` tablosu
**Durum:** ÇÖZÜLDÜ  
**Yapılan:** Migration oluşturuldu ve uygulandı
```bash
python manage.py makemigrations ticaretin_izinde
python manage.py migrate ticaretin_izinde
```

### 2. ✅ `finquest_finquestworld` ilişkisi
**Durum:** ÇÖZÜLDÜ  
**Yapılan:** Migration oluşturuldu ve uygulandı
```bash
python manage.py makemigrations finquest
python manage.py migrate finquest
```

### 3. ✅ Template hatası: `crispy_forms_tags`
**Durum:** ÇÖZÜLDÜ  
**Dosya:** `permissions/templates/permissions/permission_form.html`  
**Yapılan:** `crispy_forms_tags` yerine `bootstrap5` kullanıldı, template syntax düzeltildi (`{%%` → `{%`)

## 🔧 Kalan Hatalar ve Çözümleri

### 4. `billing_plan.trial_days` sütunu
**Çözüm:**
```bash
# Migration zaten var, sadece uygulanması gerekiyor
python manage.py migrate billing
```

### 5. `education_studentprofile_student_number_key` unique constraint
**Çözüm:** Duplicate kayıtları temizle
```python
# Django shell'de çalıştır:
from education.student.models import StudentProfile
from django.db.models import Count

# Duplicate student_number'ları bul
duplicates = StudentProfile.objects.values('student_number').annotate(
    count=Count('student_number')
).filter(count__gt=1)

# Her duplicate için en eski olanı tut, diğerlerini sil
for dup in duplicates:
    students = StudentProfile.objects.filter(
        student_number=dup['student_number']
    ).order_by('id')
    # İlkini tut, diğerlerini sil
    for student in students[1:]:
        student.student_number = f"{student.student_number}_duplicate_{student.id}"
        student.save()
```

### 6. `auth_user_change` URL pattern
**Sorun:** CustomUser kullanılıyor, auth.User değil  
**Çözüm:** Template'lerde `admin:accounts_customuser_change` kullan

**Arama:**
```bash
grep -r "auth_user_change" --include="*.html" --include="*.py"
```

### 7. Template hataları
**Çözüm:** Tüm template'lerde `{%%` → `{%` değiştir

**Arama:**
```bash
grep -r "{%%" --include="*.html"
```

### 8. `userprofile` field hatası
**Sorun:** `userprofile` alanı bulunamıyor  
**Çözüm:** `RoleBasedUserProfile` veya `UserProfile` kullan

**Arama:**
```bash
grep -r "userprofile" --include="*.html" --include="*.py"
```

### 9. Eksik template: `öğrenci/kontrol paneli.html`
**Çözüm:** Template'i oluştur veya doğru path'i kullan

**Arama:**
```bash
grep -r "öğrenci/kontrol paneli" --include="*.py"
```

## 📝 Hızlı Çözüm Komutları

```bash
# Tüm migration'ları uygula
python manage.py migrate

# Template syntax hatalarını bul
grep -r "{%%" --include="*.html"

# auth_user_change kullanımlarını bul
grep -r "auth_user_change" --include="*.html" --include="*.py"

# crispy_forms_tags kullanımlarını bul
grep -r "crispy_forms_tags" --include="*.html"
```

