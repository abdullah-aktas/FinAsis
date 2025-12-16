# Admin Panelinde Template Değişkenleri Kullanımı

## 📋 Kullanılabilir Değişkenler

Admin panelinde aşağıdaki değişkenler otomatik olarak template'lere eklenir:

### 1. `{{user}}`
**Açıklama:** Giriş yapmış kullanıcı bilgisi  
**Tip:** `CustomUser` modeli  
**Kullanım:**
```django
{{ user.username }}
{{ user.email }}
{{ user.first_name }}
{{ user.last_name }}
{{ user.is_staff }}
{{ user.is_superuser }}
```

**Örnek:**
```django
{% if user.is_authenticated %}
    <p>Hoş geldiniz, {{ user.username }}!</p>
    <p>Email: {{ user.email }}</p>
{% endif %}
```

### 2. `{{company}}`
**Açıklama:** Kullanıcının bağlı olduğu şirket  
**Tip:** `Company` modeli veya `None`  
**Kullanım:**
```django
{% if company %}
    {{ company.name }}
    {{ company.tax_number }}
    {{ company.address }}
    {{ company.phone }}
    {{ company.email }}
    {{ company.sector }}
{% else %}
    <p>Henüz şirket atanmamış</p>
{% endif %}
```

**Örnek:**
```django
{% if company %}
    <div class="company-info">
        <h3>{{ company.name }}</h3>
        <p>Vergi No: {{ company.tax_number }}</p>
        <p>Sektör: {{ company.sector }}</p>
    </div>
{% endif %}
```

## 🔧 Nasıl Çalışır?

### Yapılandırma
**Dosya:** `config/admin_site.py`

```python
def each_context(self, request):
    """Her sayfada kullanılacak context"""
    context = super().each_context(request)
    
    # Kullanıcı bilgisi
    if hasattr(request, 'user'):
        context['user'] = request.user
        
        # Kullanıcının şirketini al
        if hasattr(request.user, 'company') and request.user.company:
            context['company'] = request.user.company
        else:
            context['company'] = None
    
    return context
```

### Context Processor'lar
Ayrıca `settings.py`'de tanımlı context processor'lar da çalışır:

```python
TEMPLATES = [
    {
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',  # user değişkeni
                'common.context_processors.rbac_context',      # user_role, is_superadmin
                'common.context_processors.user_roles',        # user_groups, is_kobi_owner
                'common.context_processors.platform_context',  # platform_name, version
                'common.context_processors.brand_identity',    # brand_identity
            ],
        },
    },
]
```

## 📝 Admin Template'lerinde Kullanım

### 1. Admin Base Template'i Özelleştirme

**Dosya:** `templates/admin/base_site.html`

```django
{% extends "admin/base.html" %}

{% block title %}{{ title }} | {{ company.name|default:"FinAsis" }} Admin{% endblock %}

{% block branding %}
<h1 id="site-name">
    <a href="{% url 'admin:index' %}">
        {% if company %}
            {{ company.name }} - FinAsis Admin
        {% else %}
            FinAsis Yönetim Paneli
        {% endif %}
    </a>
</h1>
{% endblock %}

{% block userlinks %}
    {% if user.is_authenticated %}
        <a href="{% url 'admin:index' %}">
            {{ user.username }}
            {% if company %}
                ({{ company.name }})
            {% endif %}
        </a>
    {% endif %}
    {{ block.super }}
{% endblock %}
```

### 2. Admin Index Sayfası Özelleştirme

**Dosya:** `templates/admin/index.html`

```django
{% extends "admin/index.html" %}

{% block content %}
    {% if company %}
        <div class="company-banner">
            <h2>Şirket: {{ company.name }}</h2>
            <p>Vergi No: {{ company.tax_number }}</p>
            <p>Sektör: {{ company.sector }}</p>
        </div>
    {% endif %}
    
    {% if user.is_superuser %}
        <div class="superuser-info">
            <p>Süper yönetici olarak giriş yaptınız.</p>
        </div>
    {% endif %}
    
    {{ block.super }}
{% endblock %}
```

### 3. Model Admin Template'lerinde Kullanım

**Dosya:** `templates/admin/accounting/company/change_form.html`

```django
{% extends "admin/change_form.html" %}

{% block after_field_sets %}
    {% if company %}
        <div class="current-company-info">
            <h3>Mevcut Şirket Bilgileri</h3>
            <ul>
                <li><strong>Ad:</strong> {{ company.name }}</li>
                <li><strong>Vergi No:</strong> {{ company.tax_number }}</li>
                <li><strong>Oluşturan:</strong> {{ company.created_by.username|default:"-" }}</li>
            </ul>
        </div>
    {% endif %}
    
    {{ block.super }}
{% endblock %}
```

## 🎨 Örnek Kullanım Senaryoları

### Senaryo 1: Şirket Bazlı Filtreleme

```django
{% if company %}
    <div class="company-filter">
        <p>Şu anda <strong>{{ company.name }}</strong> şirketinin verilerini görüntülüyorsunuz.</p>
        <a href="?company={{ company.id }}">Sadece bu şirketin verilerini göster</a>
    </div>
{% endif %}
```

### Senaryo 2: Kullanıcı Rolüne Göre İçerik

```django
{% if user.is_superuser %}
    <div class="superuser-panel">
        <h3>Süper Yönetici Paneli</h3>
        <p>Tüm şirketleri yönetebilirsiniz.</p>
    </div>
{% elif company %}
    <div class="company-panel">
        <h3>{{ company.name }} Paneli</h3>
        <p>Sadece kendi şirketinizi yönetebilirsiniz.</p>
    </div>
{% endif %}
```

### Senaryo 3: Dinamik Başlık

```django
{% block title %}
    {% if company %}
        {{ company.name }} - {{ block.super }}
    {% else %}
        FinAsis - {{ block.super }}
    {% endif %}
{% endblock %}
```

## 🔍 Değişken Kontrolü

### Güvenli Kullanım

```django
{# Her zaman None kontrolü yapın #}
{% if user %}
    <p>Kullanıcı: {{ user.username }}</p>
{% endif %}

{% if company %}
    <p>Şirket: {{ company.name }}</p>
{% else %}
    <p>Şirket atanmamış</p>
{% endif %}
```

### Varsayılan Değerler

```django
{# Varsayılan değer ile kullanım #}
{{ company.name|default:"Şirket Yok" }}
{{ user.email|default:"Email yok" }}
```

## 📚 İlgili Dosyalar

1. **Admin Site Yapılandırması:**
   - `config/admin_site.py` - `each_context()` metodu

2. **Context Processor'lar:**
   - `common/context_processors.py` - Global context değişkenleri

3. **Model Tanımları:**
   - `accounts/models.py` - `CustomUser` modeli (company ForeignKey)
   - `accounting/models.py` - `Company` modeli

4. **Template Ayarları:**
   - `config/settings/base.py` - `TEMPLATES` yapılandırması

## ⚠️ Önemli Notlar

1. **`{{user}}` değişkeni:**
   - Django'nun `auth.context_processors.auth` ile otomatik gelir
   - Admin site'de `each_context()` ile de eklenir (garanti için)

2. **`{{company}}` değişkeni:**
   - Sadece kullanıcının `company` alanı doluysa gelir
   - `None` olabilir, her zaman kontrol edin

3. **Performans:**
   - `each_context()` her sayfada çalışır
   - Gereksiz sorgu yapmamak için `hasattr()` kontrolü yapılır

4. **Güvenlik:**
   - Kullanıcı bilgileri sadece giriş yapmış kullanıcılar için gelir
   - `request.user.is_authenticated` kontrolü yapılır

## 🚀 Hızlı Başlangıç

1. Admin template'inizi oluşturun:
   ```bash
   mkdir -p templates/admin
   touch templates/admin/base_site.html
   ```

2. Template'inize değişkenleri ekleyin:
   ```django
   {% if user %}
       <p>Kullanıcı: {{ user.username }}</p>
   {% endif %}
   
   {% if company %}
       <p>Şirket: {{ company.name }}</p>
   {% endif %}
   ```

3. Test edin:
   - Admin paneline giriş yapın
   - Template'inizin çalıştığını kontrol edin

## 📞 Yardım

Sorularınız için:
- Dokümantasyon: `config/ADMIN_TEMPLATE_DEGISKENLERI.md`
- Kod: `config/admin_site.py` - `each_context()` metodu

