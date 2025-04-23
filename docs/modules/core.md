# Core Modülü

## Genel Bakış
Core modülü, projenin temel bileşenlerini ve ortak işlevselliğini içerir.

## Temel Özellikler

### 1. Ortak Araçlar
- Yardımcı fonksiyonlar
- Özel dekoratörler
- Özel middleware'ler
- Özel context processor'lar

### 2. Veri Doğrulama
- Form doğrulama
- Model doğrulama
- API doğrulama

### 3. Güvenlik
- Güvenlik middleware'leri
- Güvenlik dekoratörleri
- Güvenlik yardımcıları

## Yardımcı Fonksiyonlar

### get_object_or_none
```python
def get_object_or_none(model, **kwargs):
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        return None
```

### get_or_create_object
```python
def get_or_create_object(model, defaults=None, **kwargs):
    obj, created = model.objects.get_or_create(
        defaults=defaults or {},
        **kwargs
    )
    return obj, created
```

## Dekoratörler

### require_ajax
```python
def require_ajax(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return HttpResponseBadRequest()
        return view_func(request, *args, **kwargs)
    return wrapper
```

### require_staff
```python
def require_staff(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapper
```

## Middleware'ler

### TimezoneMiddleware
```python
class TimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            timezone.activate(request.user.timezone)
        return self.get_response(request)
```

### SecurityMiddleware
```python
class SecurityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        return response
```

## Context Processor'lar

### settings_context
```python
def settings_context(request):
    return {
        'DEBUG': settings.DEBUG,
        'SITE_NAME': settings.SITE_NAME,
        'SITE_URL': settings.SITE_URL,
    }
```

### user_context
```python
def user_context(request):
    return {
        'user': request.user,
        'is_staff': request.user.is_staff if request.user.is_authenticated else False,
    }
```

## Kullanım Örnekleri

### View'da Yardımcı Fonksiyon Kullanımı
```python
@require_ajax
@require_staff
def some_view(request):
    obj = get_object_or_none(SomeModel, id=request.GET.get('id'))
    if not obj:
        return JsonResponse({'error': 'Object not found'}, status=404)
    return JsonResponse({'data': obj.to_dict()})
```

### Middleware Kullanımı
```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'core.middleware.TimezoneMiddleware',
    'core.middleware.SecurityMiddleware',
    # ...
]
```

### Context Processor Kullanımı
```python
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'OPTIONS': {
            'context_processors': [
                'core.context_processors.settings_context',
                'core.context_processors.user_context',
                # ...
            ],
        },
    },
]
```

## Güvenlik Önlemleri

- XSS koruması
- CSRF koruması
- Clickjacking koruması
- MIME type sniffing koruması
- Güvenli başlıklar

## Performans İyileştirmeleri

- Önbellekleme stratejileri
- Veritabanı optimizasyonları
- Şablon önbellekleme
- Statik dosya önbellekleme

## Hata Yönetimi

- Özel hata sayfaları
- Hata loglama
- Hata bildirimleri
- Hata izleme 