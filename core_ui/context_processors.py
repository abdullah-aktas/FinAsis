from django.conf import settings


def project_meta(request):
    """Provide global project meta constants to all templates."""
    return {
        "APP_VERSION": getattr(settings, "APP_VERSION", "v1.0"),
        "BRAND_NAME": getattr(settings, "BRAND_NAME", "FinAsis"),
        "SUPPORT_EMAIL": getattr(settings, "SUPPORT_EMAIL", "destek@finasis.com.tr"),
    }
from django.utils.translation import gettext as _

def marketing_features(request):
    """Provide feature/advantage data for anonymous visitors and quick links for authenticated users.
    Returns a dict consumed by base template optional banners/components.
    """
    guest_features = [
        {
            'icon': 'bi-robot',
            'title': _('AI Otomasyon'),
            'text': _('Muhasebe ve belge işlemlerinde yerel yapay zeka hızlandırması.'),
            'cta_text': _('Nasıl Çalışır?'),
            'cta_url': '/products/finans/'
        },
        {
            'icon': 'bi-file-earmark-text',
            'title': _('e‑Dönüşüm'),
            'text': _('e‑Fatura, e‑Arşiv, e‑Defter süreçlerini tek panelden yönetin.'),
            'cta_text': _('Detaylar'),
            'cta_url': '/products/finans/'
        },
        {
            'icon': 'bi-link-45deg',
            'title': _('Blockchain Kanıt'),
            'text': _('Finansal kayıt bütünlüğünü SHA‑256 hash ile doğrulayın.'),
            'cta_text': _('Güvenliği Gör'),
            'cta_url': '/products/blockchain/'
        },
        {
            'icon': 'bi-mortarboard',
            'title': _('Eğitim & Oyunlaştırma'),
            'text': _('Finansal okuryazarlık ve simülasyonlarla öğrenme ve motivasyon.'),
            'cta_text': _('Öğrenmeye Başla'),
            'cta_url': '/products/egitim/'
        },
    ]

    user_shortcuts = []
    if request.user.is_authenticated:
        # Basic role detection via simple attributes / groups
        roles = []
        if request.user.is_superuser:
            roles.append('admin')
        if request.user.is_staff:
            roles.append('staff')
        # Could be extended with profile/permissions logic
        role = roles[0] if roles else 'user'
        base_shortcuts = [
            {'icon': 'bi-speedometer2', 'label': _('Yönetim Paneli'), 'url': '/dashboard/'},
            {'icon': 'bi-wallet2', 'label': _('Finans'), 'url': '/finance/'},
            {'icon': 'bi-bar-chart', 'label': _('Raporlar'), 'url': '/finance/reports/'},
            {'icon': 'bi-controller', 'label': _('TradeSim'), 'url': '/games/'},
        ]
        if role in ('admin', 'staff'):
            base_shortcuts.insert(0, {'icon': 'bi-people', 'label': _('Kullanıcılar'), 'url': '/yonetim/users/'})
        user_shortcuts = base_shortcuts

    return {
        'guest_features': guest_features,
        'user_shortcuts': user_shortcuts,
    }
