from django.db import models
from django.conf import settings
from django.utils import timezone


# ============================================================================
# UI & THEME MANAGEMENT MODELS
# ============================================================================

class Theme(models.Model):
    """UI temaları - özelleştirilebilir temalar"""
    name = models.CharField(max_length=100, unique=True, verbose_name="Tema Adı")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="Slug")
    description = models.TextField(blank=True, verbose_name="Açıklama")
    
    # Renkler
    primary_color = models.CharField(max_length=7, default='#007bff', verbose_name="Ana Renk")
    secondary_color = models.CharField(max_length=7, default='#6c757d', verbose_name="İkincil Renk")
    success_color = models.CharField(max_length=7, default='#28a745', verbose_name="Başarı Rengi")
    danger_color = models.CharField(max_length=7, default='#dc3545', verbose_name="Hata Rengi")
    warning_color = models.CharField(max_length=7, default='#ffc107', verbose_name="Uyarı Rengi")
    info_color = models.CharField(max_length=7, default='#17a2b8', verbose_name="Bilgi Rengi")
    
    # Arka plan
    background_color = models.CharField(max_length=7, default='#ffffff', verbose_name="Arka Plan Rengi")
    text_color = models.CharField(max_length=7, default='#212529', verbose_name="Metin Rengi")
    
    # Fontlar
    font_family = models.CharField(max_length=200, default='Inter, system-ui, sans-serif', verbose_name="Font Ailesi")
    font_size_base = models.CharField(max_length=10, default='14px', verbose_name="Temel Font Boyutu")
    
    # Layout
    border_radius = models.CharField(max_length=10, default='8px', verbose_name="Köşe Yuvarlaklığı")
    box_shadow = models.CharField(max_length=100, default='0 2px 8px rgba(0,0,0,0.1)', verbose_name="Gölge")
    
    # Custom CSS
    custom_css = models.TextField(blank=True, verbose_name="Özel CSS")
    
    # Durum
    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    is_default = models.BooleanField(default=False, verbose_name="Varsayılan")
    
    # Preview
    thumbnail = models.ImageField(upload_to='themes/', null=True, blank=True, verbose_name="Önizleme")
    
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Oluşturan")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Tema"
        verbose_name_plural = "Temalar"
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        # Sadece bir varsayılan tema olabilir
        if self.is_default:
            Theme.objects.filter(is_default=True).update(is_default=False)
        super().save(*args, **kwargs)


class Banner(models.Model):
    """Duyuru banner'ları - site genelinde bildirimler"""
    BANNER_TYPES = [
        ('info', 'Bilgilendirme'),
        ('success', 'Başarı'),
        ('warning', 'Uyarı'),
        ('danger', 'Hata'),
        ('announcement', 'Duyuru'),
    ]
    
    POSITIONS = [
        ('top', 'Üst'),
        ('bottom', 'Alt'),
        ('floating', 'Yüzer'),
    ]
    
    title = models.CharField(max_length=200, verbose_name="Başlık")
    message = models.TextField(verbose_name="Mesaj")
    banner_type = models.CharField(max_length=20, choices=BANNER_TYPES, default='info', verbose_name="Tip")
    position = models.CharField(max_length=20, choices=POSITIONS, default='top', verbose_name="Konum")
    
    # Link
    button_text = models.CharField(max_length=50, blank=True, verbose_name="Buton Metni")
    button_url = models.CharField(max_length=500, blank=True, verbose_name="Buton URL")
    
    # Hedef kitle
    show_to_guests = models.BooleanField(default=True, verbose_name="Misafirlere Göster")
    show_to_authenticated = models.BooleanField(default=True, verbose_name="Üyelere Göster")
    target_roles = models.JSONField(default=list, blank=True, verbose_name="Hedef Roller")
    
    # Zamanlama
    start_date = models.DateTimeField(null=True, blank=True, verbose_name="Başlangıç Tarihi")
    end_date = models.DateTimeField(null=True, blank=True, verbose_name="Bitiş Tarihi")
    
    # Durum
    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    is_dismissible = models.BooleanField(default=True, verbose_name="Kapatılabilir")
    
    # İstatistikler
    view_count = models.IntegerField(default=0, verbose_name="Görüntüleme")
    click_count = models.IntegerField(default=0, verbose_name="Tıklama")
    
    # Öncelik
    priority = models.IntegerField(default=0, verbose_name="Öncelik", help_text="Yüksek öncelik üstte gösterilir")
    
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_banners', verbose_name="Oluşturan")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Banner"
        verbose_name_plural = "Bannerlar"
        ordering = ['-priority', '-created_at']
    
    def __str__(self):
        return self.title
    
    def is_visible(self):
        """Banner'ın görünür olup olmadığını kontrol et"""
        if not self.is_active:
            return False
        now = timezone.now()
        if self.start_date and now < self.start_date:
            return False
        if self.end_date and now > self.end_date:
            return False
        return True


class NavigationMenu(models.Model):
    """Navigasyon menüleri - dinamik menü yönetimi"""
    MENU_TYPES = [
        ('header', 'Üst Menü'),
        ('footer', 'Alt Menü'),
        ('sidebar', 'Yan Menü'),
        ('mobile', 'Mobil Menü'),
    ]
    
    name = models.CharField(max_length=100, verbose_name="Menü Adı")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="Slug")
    menu_type = models.CharField(max_length=20, choices=MENU_TYPES, verbose_name="Menü Tipi")
    
    # Hedef
    target_roles = models.JSONField(default=list, blank=True, verbose_name="Hedef Roller", help_text="Boş bırakılırsa herkese gösterilir")
    
    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Navigasyon Menüsü"
        verbose_name_plural = "Navigasyon Menüleri"
        ordering = ['menu_type', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_menu_type_display()})"


class MenuItem(models.Model):
    """Menü öğeleri - navigasyon linkler"""
    menu = models.ForeignKey(NavigationMenu, on_delete=models.CASCADE, related_name='items', verbose_name="Menü")
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='children', verbose_name="Üst Öğe")
    
    title = models.CharField(max_length=100, verbose_name="Başlık")
    url = models.CharField(max_length=500, verbose_name="URL")
    icon = models.CharField(max_length=50, blank=True, verbose_name="İkon (Bootstrap Icons)")
    
    # Hedef
    target_blank = models.BooleanField(default=False, verbose_name="Yeni Sekmede Aç")
    
    # Görünüm
    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    order = models.IntegerField(default=0, verbose_name="Sıra")
    
    # Badge
    badge_text = models.CharField(max_length=20, blank=True, verbose_name="Rozet Metni")
    badge_color = models.CharField(max_length=20, blank=True, verbose_name="Rozet Rengi", help_text="primary, success, danger, warning, info")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Menü Öğesi"
        verbose_name_plural = "Menü Öğeleri"
        ordering = ['menu', 'order', 'title']
    
    def __str__(self):
        return f"{self.menu.name} - {self.title}"


class Page(models.Model):
    """Dinamik sayfalar - CMS benzeri içerik yönetimi"""
    PAGE_TYPES = [
        ('standard', 'Standart Sayfa'),
        ('landing', 'Landing Page'),
        ('faq', 'SSS'),
        ('terms', 'Kullanım Koşulları'),
        ('privacy', 'Gizlilik Politikası'),
        ('about', 'Hakkımızda'),
        ('contact', 'İletişim'),
    ]
    
    title = models.CharField(max_length=200, verbose_name="Sayfa Başlığı")
    slug = models.SlugField(max_length=200, unique=True, verbose_name="Slug")
    page_type = models.CharField(max_length=20, choices=PAGE_TYPES, default='standard', verbose_name="Sayfa Tipi")
    
    # İçerik
    content = models.TextField(verbose_name="İçerik (HTML)")
    excerpt = models.TextField(blank=True, verbose_name="Özet")
    
    # SEO
    meta_title = models.CharField(max_length=200, blank=True, verbose_name="Meta Başlık")
    meta_description = models.TextField(blank=True, verbose_name="Meta Açıklama")
    meta_keywords = models.CharField(max_length=500, blank=True, verbose_name="Meta Anahtar Kelimeler")
    
    # Görsel
    featured_image = models.ImageField(upload_to='pages/', null=True, blank=True, verbose_name="Öne Çıkan Görsel")
    
    # Tema
    theme = models.ForeignKey(Theme, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Özel Tema")
    custom_css = models.TextField(blank=True, verbose_name="Özel CSS")
    custom_js = models.TextField(blank=True, verbose_name="Özel JavaScript")
    
    # Durum
    is_published = models.BooleanField(default=False, verbose_name="Yayınlandı")
    published_at = models.DateTimeField(null=True, blank=True, verbose_name="Yayın Tarihi")
    
    # İstatistikler
    view_count = models.IntegerField(default=0, verbose_name="Görüntüleme")
    
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='authored_pages', verbose_name="Yazar")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Sayfa"
        verbose_name_plural = "Sayfalar"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title


class Widget(models.Model):
    """Widgetlar - yeniden kullanılabilir UI bileşenleri"""
    WIDGET_TYPES = [
        ('html', 'HTML'),
        ('text', 'Metin'),
        ('button', 'Buton'),
        ('card', 'Kart'),
        ('stats', 'İstatistik'),
        ('chart', 'Grafik'),
        ('form', 'Form'),
        ('custom', 'Özel'),
    ]
    
    POSITIONS = [
        ('header', 'Üst Kısım'),
        ('sidebar_left', 'Sol Kenar'),
        ('sidebar_right', 'Sağ Kenar'),
        ('footer', 'Alt Kısım'),
        ('content_top', 'İçerik Üstü'),
        ('content_bottom', 'İçerik Altı'),
    ]
    
    title = models.CharField(max_length=200, verbose_name="Widget Başlığı")
    widget_type = models.CharField(max_length=20, choices=WIDGET_TYPES, verbose_name="Widget Tipi")
    content = models.TextField(verbose_name="İçerik")
    
    # Konum
    position = models.CharField(max_length=20, choices=POSITIONS, verbose_name="Konum")
    order = models.IntegerField(default=0, verbose_name="Sıra")
    
    # Görünüm ayarları
    css_classes = models.CharField(max_length=200, blank=True, verbose_name="CSS Sınıfları")
    custom_css = models.TextField(blank=True, verbose_name="Özel CSS")
    
    # Hedef
    target_pages = models.JSONField(default=list, blank=True, verbose_name="Hedef Sayfalar", help_text="Boş bırakılırsa tüm sayfalarda gösterilir")
    target_roles = models.JSONField(default=list, blank=True, verbose_name="Hedef Roller")
    
    # Durum
    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_widgets', verbose_name="Oluşturan")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Widget"
        verbose_name_plural = "Widgetlar"
        ordering = ['position', 'order']
    
    def __str__(self):
        return self.title


class UIComponent(models.Model):
    """UI Bileşenleri - template include edilebilir bileşenler"""
    COMPONENT_TYPES = [
        ('card', 'Kart'),
        ('modal', 'Modal'),
        ('alert', 'Uyarı'),
        ('table', 'Tablo'),
        ('list', 'Liste'),
        ('grid', 'Grid'),
        ('carousel', 'Carousel'),
        ('accordion', 'Accordion'),
        ('tabs', 'Sekmeler'),
        ('custom', 'Özel'),
    ]
    
    name = models.CharField(max_length=100, unique=True, verbose_name="Bileşen Adı")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="Slug")
    component_type = models.CharField(max_length=20, choices=COMPONENT_TYPES, verbose_name="Bileşen Tipi")
    
    description = models.TextField(blank=True, verbose_name="Açıklama")
    
    # Template
    template_code = models.TextField(verbose_name="Template Kodu")
    
    # Parametreler
    default_params = models.JSONField(default=dict, blank=True, verbose_name="Varsayılan Parametreler")
    
    # Preview
    preview_data = models.JSONField(default=dict, blank=True, verbose_name="Önizleme Verisi")
    screenshot = models.ImageField(upload_to='components/', null=True, blank=True, verbose_name="Ekran Görüntüsü")
    
    # Version
    version = models.CharField(max_length=20, default='1.0', verbose_name="Versiyon")
    
    # Durum
    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_components', verbose_name="Oluşturan")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "UI Bileşeni"
        verbose_name_plural = "UI Bileşenleri"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class UserThemePreference(models.Model):
    """Kullanıcı tema tercihleri"""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='theme_preference', verbose_name="Kullanıcı")
    theme = models.ForeignKey(Theme, on_delete=models.SET_NULL, null=True, verbose_name="Tema")
    
    # Mod
    dark_mode = models.BooleanField(default=False, verbose_name="Koyu Mod")
    auto_dark_mode = models.BooleanField(default=True, verbose_name="Otomatik Koyu Mod")
    
    # Layout tercihleri
    sidebar_collapsed = models.BooleanField(default=False, verbose_name="Kenar Çubuğu Daraltılmış")
    compact_mode = models.BooleanField(default=False, verbose_name="Kompakt Mod")
    
    # Font boyutu
    font_size = models.CharField(max_length=10, choices=[
        ('small', 'Küçük'),
        ('medium', 'Orta'),
        ('large', 'Büyük'),
    ], default='medium', verbose_name="Font Boyutu")
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Kullanıcı Tema Tercihi"
        verbose_name_plural = "Kullanıcı Tema Tercihleri"
    
    def __str__(self):
        return f"{self.user.username} - {self.theme}"

