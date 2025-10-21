# Role-Based Access Control (RBAC) İmplementasyonu

## 🎯 **Genel Bakış**

FinAsis artık **rol tabanlı erişim kontrolü (RBAC)** sistemine sahip. Kullanıcılar rollerine göre farklı menüler, eylemler ve içerikler görürler.

---

## 📋 **Rol Sistemi**

### Tanımlı Roller:

#### 1. **Yönetim Rolleri**
- `admin` - Tam yetkili yönetici
- `staff` - Çalışan
- `viewer` - Sadece görüntüleme

#### 2. **İş Rolleri**
- `kobi_owner` - KOBİ Sahibi
- `kobi_staff` - KOBİ Çalışanı
- `accountant` - Muhasebeci
- `financial_advisor` - Mali Müşavir
- `finance_manager` - Finans Müdürü
- `auditor` - Denetçi

#### 3. **Eğitim Rolleri**
- `teacher` - Öğretmen
- `student` - Öğrenci

#### 4. **Oyun Rolleri**
- `player` - Oyuncu

---

## 🔧 **Teknik Yapı**

### 1. Oluşturulan Dosyalar:

```
src/apps/common/
├── role_utils.py              # Rol kontrol fonksiyonları
├── context_processors.py      # Template context processors
└── templatetags/
    ├── __init__.py
    └── role_tags.py          # Template tags

templates/components/
├── header_role_based.html    # Rol bazlı header
├── role_badge.html           # Rol rozeti component
└── quick_actions_menu.html   # Hızlı işlemler menüsü

templates/
└── dashboard_role_based.html # Rol bazlı dashboard
```

### 2. Settings Değişikliği:

```python
# src/config/settings_pkg/base.py

TEMPLATES = [{
    'OPTIONS': {
        'context_processors': [
            # ... mevcut processors
            'src.apps.common.context_processors.user_roles',      # YENİ
            'src.apps.common.context_processors.platform_context', # YENİ
        ],
    },
}]
```

---

## 🎨 **Template'lerde Kullanım**

### 1. Rol Kontrolü:

```django
{% load role_tags %}

{# Basit rol kontrolü #}
{% if user|has_role:'admin' %}
    <a href="{% url 'admin:index' %}">Admin Panel</a>
{% endif %}

{# Birden fazla rol kontrolü #}
{% if user|has_any_role:'admin,kobi_owner' %}
    <button class="btn btn-danger">Sil</button>
{% endif %}

{# İzin grubu kontrolü #}
{% can_user user 'CAN_CREATE_INVOICE' as can_create %}
{% if can_create %}
    <a href="{% url 'accounting:invoice_create' %}">Yeni Fatura</a>
{% endif %}
```

### 2. Otomatik Context Variables:

Tüm template'lerde kullanılabilir:

```django
{{ user_role }}               {# Kullanıcının ana rolü #}
{{ user_roles }}              {# Kullanıcının tüm rolleri (list) #}
{{ user_role_display }}       {# "Muhasebeci" gibi görünen isim #}
{{ user_role_icon }}          {# "bi-calculator" gibi icon #}
{{ user_role_color }}         {# "success" gibi renk #}

{{ user_menu_items }}         {# Kullanıcının erişebileceği menü öğeleri #}
{{ user_quick_actions }}      {# Hızlı işlemler listesi #}
{{ user_modules }}            {# Erişilebilir modüller #}
{{ user_dashboard_type }}     {# 'kobi', 'accountant', vb. #}
```

### 3. Rol Rozeti Gösterme:

```django
{% load role_tags %}

{# Kullanıcının rolünü rozet olarak göster #}
{% show_role_badge user %}

{# Çıktı: #}
<span class="badge bg-success-subtle text-success">
  <i class="bi-calculator me-1"></i>Muhasebeci
</span>
```

### 4. Hızlı İşlemler Menüsü:

```django
{% load role_tags %}

{# Kullanıcının yapabileceği hızlı işlemleri göster #}
{% show_quick_actions %}
```

---

## 💻 **View'larda Kullanım**

### 1. Decorator ile Rol Kontrolü:

```python
from src.apps.common.role_utils import role_required, permission_required, PermissionGroups

# Sadece admin'lerin erişebileceği view
@role_required('admin')
def admin_dashboard(request):
    return render(request, 'admin_dashboard.html')

# Admin veya KOBİ sahibinin erişebileceği view
@role_required('admin', 'kobi_owner')
def company_settings(request):
    return render(request, 'company_settings.html')

# İzin grubu kontrolü
@permission_required(PermissionGroups.CAN_CREATE_INVOICE)
def create_invoice(request):
    return render(request, 'invoice_form.html')
```

### 2. View İçinde Manuel Kontrol:

```python
from src.apps.common.role_utils import user_can, user_has_role, PermissionGroups

def my_view(request):
    # Rol kontrolü
    is_admin = user_has_role(request.user, 'admin')
    
    # İzin kontrolü
    can_create_invoice = user_can(request.user, PermissionGroups.CAN_CREATE_INVOICE)
    
    # Context'e ekle
    context = {
        'is_admin': is_admin,
        'can_create_invoice': can_create_invoice,
    }
    return render(request, 'my_template.html', context)
```

---

## 🎭 **İzin Grupları**

### Finansal İşlemler:
```python
PermissionGroups.CAN_VIEW_FINANCE         # admin, kobi_owner, accountant, financial_advisor, finance_manager
PermissionGroups.CAN_CREATE_INVOICE       # admin, kobi_owner, accountant
PermissionGroups.CAN_DELETE_INVOICE       # admin, kobi_owner
PermissionGroups.CAN_APPROVE_PAYMENT      # admin, kobi_owner, finance_manager
```

### Eğitim İşlemleri:
```python
PermissionGroups.CAN_VIEW_EDUCATION       # admin, teacher, student
PermissionGroups.CAN_CREATE_COURSE        # admin, teacher
PermissionGroups.CAN_GRADE_ASSIGNMENT     # admin, teacher
```

### Oyun İşlemleri:
```python
PermissionGroups.CAN_PLAY_GAMES           # admin, player, student
PermissionGroups.CAN_VIEW_LEADERBOARD     # admin, player, student, teacher
```

### Yönetim İşlemleri:
```python
PermissionGroups.CAN_MANAGE_USERS         # admin
PermissionGroups.CAN_MANAGE_COMPANY       # admin, kobi_owner
PermissionGroups.CAN_VIEW_REPORTS         # admin, kobi_owner, accountant, financial_advisor, finance_manager
```

### AI İşlemleri:
```python
PermissionGroups.CAN_USE_AI               # admin, kobi_owner, accountant, financial_advisor, finance_manager, teacher
```

---

## 📱 **Rol Bazlı Dashboard'lar**

### Kullanıcı rolüne göre otomatik dashboard yönlendirmesi:

```python
# views.py (örnek)
from src.apps.common.role_utils import get_user_dashboard_type

def dashboard(request):
    dashboard_type = get_user_dashboard_type(request.user)
    
    if dashboard_type == 'kobi':
        return redirect('accounts:dashboard_kobi')
    elif dashboard_type == 'accountant':
        return redirect('accounting:home')
    elif dashboard_type == 'teacher':
        return redirect('education:dashboard')
    elif dashboard_type == 'player':
        return redirect('games:home')
    
    # Default: rol bazlı dashboard
    return render(request, 'dashboard_role_based.html', context)
```

---

## 🔐 **Güvenlik**

### Best Practices:

1. **Her zaman backend'de kontrol et:**
```python
# ❌ YANLIŞ (sadece template'te)
{% if user_role == 'admin' %}
    <a href="/delete/">Sil</a>
{% endif %}

# ✅ DOĞRU (hem template hem view)
{% if user|has_role:'admin' %}
    <a href="/delete/">Sil</a>
{% endif %}

# view.py
@role_required('admin')
def delete_view(request):
    ...
```

2. **Hassas bilgileri gizle:**
```python
# Context'i role göre filtrele
context = {
    'transactions': get_transactions_for_role(request.user),
    'can_delete': user_has_role(request.user, 'admin'),
}
```

3. **API endpoint'lerde de kontrol et:**
```python
from rest_framework.decorators import api_view
from src.apps.common.role_utils import user_can, PermissionGroups

@api_view(['POST'])
def api_create_invoice(request):
    if not user_can(request.user, PermissionGroups.CAN_CREATE_INVOICE):
        return Response({'error': 'Yetkiniz yok'}, status=403)
    
    # İşlem devam eder
    ...
```

---

## 📊 **Rol Bazlı Menü Örneği**

### Admin Kullanıcısı Görür:
```
Dashboard | Muhasebe | Finans | Eğitim | Oyunlar | AI Asistan | Raporlar | Yönetim
```

### KOBİ Sahibi Görür:
```
Dashboard | Muhasebe | Finans | AI Asistan | Raporlar
```

### Muhasebeci Görür:
```
Dashboard | Muhasebe | Finans | Raporlar
```

### Öğretmen Görür:
```
Dashboard | Eğitim | AI Asistan
```

### Öğrenci Görür:
```
Dashboard | Eğitim | Oyunlar
```

### Oyuncu Görür:
```
Dashboard | Oyunlar
```

---

## 🚀 **Kullanıma Alma**

### 1. Base Template'i Güncelle:

```django
{# templates/core_ui/base.html #}

{# Eski header yerine yeni rol bazlı header #}
{% block header %}
  {% include 'components/header_role_based.html' %}
{% endblock %}
```

### 2. Dashboard View'i Güncelle:

```python
# src/views.py veya src/config/views.py

from src.apps.common.role_utils import get_user_dashboard_type

def dashboard(request):
    context = {
        'total_income': 125000,
        'total_expense': 85000,
        'net_profit': 40000,
        'cash_balance': 65000,
        'recent_invoices': [],  # DB'den çek
        'pending_payments': [],  # DB'den çek
    }
    return render(request, 'dashboard_role_based.html', context)
```

### 3. Test Et:

```bash
# Sunucuyu başlat
python manage.py runserver

# Farklı rollerle giriş yap ve test et
```

---

## ✅ **Test Checklist**

- [ ] Admin kullanıcısı tüm menüleri görüyor mu?
- [ ] KOBİ sahibi sadece finans modüllerini görüyor mu?
- [ ] Muhasebeci fatura oluşturabiliyor mu?
- [ ] Öğrenci oyunlara erişebiliyor mu?
- [ ] Öğretmen not verebiliyor mu?
- [ ] Viewer kullanıcısı düzenleme yapamıyor mu?
- [ ] Rol rozetleri doğru renkte mi?
- [ ] Hızlı işlemler rolüne uygun mu?

---

## 💡 **Örnekler**

### Örnek 1: Sadece Muhasebecilerin Göreceği Buton

```django
{% load role_tags %}

{% can_user user 'CAN_CREATE_INVOICE' as can_create %}
{% if can_create %}
    <a href="{% url 'accounting:invoice_create' %}" class="btn btn-primary">
        <i class="bi bi-plus-circle me-2"></i>Yeni Fatura
    </a>
{% endif %}
```

### Örnek 2: Admin veya KOBİ Sahibinin Göreceği Sil Butonu

```django
{% if user|has_any_role:'admin,kobi_owner' %}
    <button class="btn btn-danger btn-sm" onclick="deleteItem()">
        <i class="bi bi-trash me-1"></i>Sil
    </button>
{% endif %}
```

### Örnek 3: Dinamik Menü

```django
<ul class="nav">
    {% for item in user_menu_items %}
        <li class="nav-item">
            <a class="nav-link" href="{% url item.url %}">
                <i class="{{ item.icon }} me-2"></i>{{ item.name }}
            </a>
        </li>
    {% endfor %}
</ul>
```

---

## 🔄 **Migration Path**

### Adım 1: Context Processor'ı Aktif Et ✅
```python
# settings_pkg/base.py
'context_processors': [
    'src.apps.common.context_processors.user_roles',
]
```

### Adım 2: Template'leri Güncelle
```django
{# Eski #}
{% if user.is_staff %}

{# Yeni #}
{% if user|has_role:'admin' %}
```

### Adım 3: View'ları Güncelle
```python
# Eski
if request.user.is_staff:

# Yeni
from src.apps.common.role_utils import user_has_role
if user_has_role(request.user, 'admin'):
```

### Adım 4: Test Et
- Farklı rollerle giriş yap
- Menüleri kontrol et
- İşlevselliği test et

---

## 📚 **API Referansı**

### Helper Fonksiyonlar:

```python
get_user_role(user)                    # Ana rolü döner
get_user_roles(user)                   # Tüm rolleri döner (list)
user_has_role(user, role)              # Belirtilen role sahip mi?
user_has_any_role(user, roles)         # Belirtilen rollerden biri var mı?
user_can(user, permission_group)       # İzin grubu kontrolü
get_menu_items_for_user(user)          # Erişilebilir menü öğeleri
get_quick_actions_for_user(user)       # Hızlı işlemler
get_allowed_modules_for_user(user)     # Erişilebilir modüller
get_user_dashboard_type(user)          # Dashboard tipi
```

### Template Tags:

```django
{% load role_tags %}

{% can_user user 'CAN_CREATE_INVOICE' as can_create %}
{{ user|has_role:'admin' }}
{{ user|has_any_role:'admin,kobi_owner' }}
{% user_primary_role user %}
{% user_all_roles user %}
{% show_role_badge user %}
{% show_quick_actions %}
```

---

## 🎓 **En İyi Uygulamalar**

1. **Always check in backend:**
   - Template kontrolü UX için
   - View decorator'ı güvenlik için

2. **Use permission groups:**
   - Rol isimleri yerine izin grupları kullan
   - Daha esnek ve bakımı kolay

3. **Cache role data:**
   - Her istekte rol hesaplama pahalı
   - Context processor cache kullanabilir

4. **Log access attempts:**
   - Yetkisiz erişim denemelerini logla
   - Audit trail için önemli

---

## 🚀 **Başarıyla İmplemente Edildi!**

FinAsis artık profesyonel bir rol bazlı erişim kontrol sistemine sahip! 🎉

