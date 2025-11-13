# Accounting Breadcrumbs Kullanımı

Yeni şablon yapısı `core_ui/base.html` içinde opsiyonel bir `breadcrumbs` bloğu/partial bekler. Accounting modülü için görünümlerinizde aşağıdaki gibi bir liste gönderebilirsiniz:

```python
# Örnek Django view
from django.shortcuts import render

def expense_list_view(request):
    breadcrumbs = [
        ("Muhasebe", "/accounting/"),
        ("Giderler", None),  # Son öğe (aktif) için URL None
    ]
    context = {"breadcrumbs": breadcrumbs}
    return render(request, "accounting/expense_list.html", context)
```

## Yapı
`breadcrumbs` bir iterable olmalı ve her öğe `(label, url)` tuple'ı:
- `url` None ise aktif/son kırıntı olarak işaretlenir.
- URL varsa link olarak gösterilir.

## Otomasyon Fikri (İsteğe Bağlı)
Sık kullanılan modül yollarını otomatik üretmek için basit bir yardımcı yazabilirsiniz:
```python
# accounting/utils/breadcrumbs.py
def trail(*items):
    return items

# view içinde
from accounting.utils.breadcrumbs import trail
breadcrumbs = trail(("Muhasebe", "/accounting/"), ("Ürünler", None))
```

## Template İçinde
`core_ui/base.html` şu değişkene bakıyor: `breadcrumbs`. Ekstra bir include çağırmanıza gerek yok; varsa otomatik gösterilecek.

## Örnek Diğer Sayfa
```python
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    breadcrumbs = [
        ("Muhasebe", "/accounting/"),
        ("Ürünler", "/accounting/products/"),
        (product.name, None),
    ]
    return render(request, "accounting/product_detail.html", {"product": product, "breadcrumbs": breadcrumbs})
```

## İyi Uygulamalar
- Maksimum 3-4 seviye kullanın.
- Listeyi view içinde kurun; karmaşık senaryolarda context processor düşünebilirsiniz.
- Çok dil desteği için label değerlerinde `gettext_lazy` kullanın.

```python
from django.utils.translation import gettext_lazy as _
breadcrumbs = [(_("Muhasebe"), "/accounting/"), (_("Giderler"), None)]
```

Hazır. Sidebar i18n / aria iyileştirmesine geçmeden önce eklemek istediğiniz başka nokta varsa belirtin.
