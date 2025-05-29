# models.py
from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal
from django.conf import settings


class VirtualCompany(models.Model):
    """
    Öğrenci/katılımcı tarafından oluşturulan sanal şirket modeli.
    Finansal işlemlerin ve ürünlerin merkezi yapısıdır.
    """
    name = models.CharField(max_length=100, verbose_name="Şirket Adı")
    description = models.TextField(verbose_name="Şirket Açıklaması")
    balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Bakiye (₺)"
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_virtual_companies',
        verbose_name="Şirket Sahibi (Kullanıcı)"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Son Güncelleme")

    class Meta:
        verbose_name = "Sanal Şirket"
        verbose_name_plural = "Sanal Şirketler"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.owner.username})"

    def total_stock_value(self):
        """
        Şirketin ürün stoğunun toplam maliyet değeri.
        """
        return sum(p.price * p.stock for p in self.products.all())

    def is_profitable(self):
        """
        Şirket kârda mı değil mi? Bakiye pozitifse True döner.
        """
        return self.balance > 0


class Product(models.Model):
    """
    Sanal şirketin sattığı veya yönettiği ürünler.
    Muhasebe uygulamaları için temel varlık.
    """
    name = models.CharField(max_length=100, verbose_name="Ürün Adı")
    description = models.TextField(verbose_name="Ürün Açıklaması")
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Birim Fiyat (₺)"
    )
    stock = models.PositiveIntegerField(default=0, verbose_name="Stok Miktarı")
    company = models.ForeignKey(
        VirtualCompany,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name="Bağlı Olduğu Şirket"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Eklenme Tarihi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Son Güncelleme")

    class Meta:
        verbose_name = "Ürün"
        verbose_name_plural = "Ürünler"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.company.name})"

    def total_value(self):
        """
        Bu ürünün toplam stok değeri (fiyat * adet).
        """
        return self.price * self.stock


class Transaction(models.Model):
    """
    Sanal şirketin yaptığı finansal işlemler: gelir veya gider.
    """
    TRANSACTION_TYPES = [
        ('INCOME', 'Gelir'),
        ('EXPENSE', 'Gider'),
    ]

    company = models.ForeignKey(VirtualCompany, on_delete=models.CASCADE, related_name='transactions', verbose_name="Şirket")
    transaction_type = models.CharField(max_length=7, choices=TRANSACTION_TYPES, verbose_name="İşlem Türü")
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Tutar (₺)")
    description = models.TextField(verbose_name="Açıklama")
    date = models.DateField(auto_now_add=True, verbose_name="Tarih")

    class Meta:
        verbose_name = "Finansal İşlem"
        verbose_name_plural = "Finansal İşlemler"
        ordering = ['-date']

    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.amount}₺ ({self.company.name})"


class Invoice(models.Model):
    """
    Fatura kaydı. Eğitim amaçlı uygulamalarda kullanılabilir.
    """
    company = models.ForeignKey(VirtualCompany, on_delete=models.CASCADE, related_name='invoices', verbose_name="Şirket")
    invoice_number = models.CharField(max_length=20, verbose_name="Fatura No")
    customer_name = models.CharField(max_length=100, verbose_name="Müşteri Adı")
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Toplam Tutar (₺)")
    issue_date = models.DateField(verbose_name="Fatura Tarihi")

    class Meta:
        verbose_name = "Fatura"
        verbose_name_plural = "Faturalar"
        ordering = ['-issue_date']

    def __str__(self):
        return f"Fatura #{self.invoice_number} - {self.total_amount}₺"


class EducationModule(models.Model):
    """
    Öğrenme senaryosu: Öğrencilere verilen görevler.
    Örnek: 'Satış işlemi gir', 'Fatura oluştur', 'Rapor hazırla'
    """
    title = models.CharField(max_length=100, verbose_name="Görev Başlığı")
    description = models.TextField(verbose_name="Görev Açıklaması")
    points = models.PositiveIntegerField(default=10, verbose_name="Puan")
    is_active = models.BooleanField(default=True, verbose_name="Aktif mi?")

    class Meta:
        verbose_name = "Eğitim Modülü"
        verbose_name_plural = "Eğitim Modülleri"

    def __str__(self):
        return self.title


class FinanceReport(models.Model):
    """
    Otomatik veya elle oluşturulmuş finansal analiz raporu.
    """
    company = models.ForeignKey(VirtualCompany, on_delete=models.CASCADE, related_name='reports', verbose_name="Şirket")
    title = models.CharField(max_length=100, verbose_name="Rapor Başlığı")
    content = models.TextField(verbose_name="Rapor İçeriği")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")

    class Meta:
        verbose_name = "Finansal Rapor"
        verbose_name_plural = "Finansal Raporlar"

    def __str__(self):
        return self.title


class StudentProfile(models.Model):
    """
    Öğrenci bilgileri: Eğitim modüllerini tamamlama durumu vs.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Kullanıcı")
    virtual_company = models.OneToOneField(VirtualCompany, on_delete=models.CASCADE, verbose_name="Şirket")
    completed_modules = models.ManyToManyField(EducationModule, blank=True, verbose_name="Tamamlanan Görevler")

    class Meta:
        verbose_name = "Öğrenci Profili"
        verbose_name_plural = "Öğrenci Profilleri"

    def __str__(self):
        return f"Öğrenci: {self.user.username}"


class TeacherProfile(models.Model):
    """
    Öğretmenler için takip ve değerlendirme alanı.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Kullanıcı")
    managed_students = models.ManyToManyField(StudentProfile, blank=True, verbose_name="Takip Ettiği Öğrenciler")

    class Meta:
        verbose_name = "Öğretmen Profili"
        verbose_name_plural = "Öğretmen Profilleri"

    def __str__(self):
        return f"Öğretmen: {self.user.username}"


class AccountingEntry(models.Model):
    """
    Öğrencinin girdiği muhasebe kaydı. Şirketin finansal yapısına etkisi izlenir.
    """
    company = models.ForeignKey(VirtualCompany, on_delete=models.CASCADE, related_name='entries', verbose_name="Şirket")
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Öğrenci")
    date = models.DateField(auto_now_add=True, verbose_name="Kayıt Tarihi")
    description = models.CharField(max_length=255, verbose_name="İşlem Açıklaması")
    debit_account = models.CharField(max_length=100, verbose_name="Borç Hesabı")
    credit_account = models.CharField(max_length=100, verbose_name="Alacak Hesabı")
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Tutar (₺)")
    effect_on_balance = models.CharField(
        max_length=50,
        choices=[("POSITIVE", "Pozitif"), ("NEGATIVE", "Negatif"), ("NEUTRAL", "Nötr")],
        verbose_name="Şirket Bakiyesine Etki"
    )
    ai_recommendation = models.TextField(blank=True, null=True, verbose_name="Yapay Zeka Önerisi")

    class Meta:
        verbose_name = "Muhasebe Kaydı"
        verbose_name_plural = "Muhasebe Kayıtları"
        ordering = ['-date']

    def __str__(self):
        return f"{self.date} | {self.description} ({self.amount}₺)"

    def apply_effect(self):
        """
        Şirketin bakiyesine işlemin etkisini uygula.
        """
        if self.effect_on_balance == "POSITIVE":
            self.company.balance += self.amount
        elif self.effect_on_balance == "NEGATIVE":
            self.company.balance -= self.amount
        self.company.save()


class AIAccountingRecommendation(models.Model):
    """
    Yapay zekanın öğrenciye sunduğu muhasebe önerisi.
    """
    company = models.ForeignKey(VirtualCompany, on_delete=models.CASCADE, verbose_name="Şirket")
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Öğrenci")
    suggestion = models.TextField(verbose_name="Öneri Açıklaması")
    confidence_score = models.FloatField(verbose_name="Tahmin Güveni (%)")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "AI Muhasebe Önerisi"
        verbose_name_plural = "AI Muhasebe Önerileri"

    def __str__(self):
        return f"%{round(self.confidence_score * 100)} güvenle öneri"
