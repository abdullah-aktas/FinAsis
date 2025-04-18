from django.db import models
from django.conf import settings

class Customer(models.Model):
    """Müşteri modeli"""
    name = models.CharField(max_length=200, verbose_name='Müşteri Adı')
    email = models.EmailField(verbose_name='E-posta')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Telefon')
    company = models.CharField(max_length=200, blank=True, verbose_name='Şirket')
    address = models.TextField(blank=True, verbose_name='Adres')
    tax_number = models.CharField(max_length=20, blank=True, verbose_name='Vergi Numarası')
    tax_office = models.CharField(max_length=100, blank=True, verbose_name='Vergi Dairesi')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Oluşturan')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Oluşturulma Tarihi')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Güncellenme Tarihi')
    is_active = models.BooleanField(default=True, verbose_name='Aktif')

    class Meta:
        verbose_name = 'Müşteri'
        verbose_name_plural = 'Müşteriler'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

class CustomerNote(models.Model):
    """Müşteri notu modeli"""
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='customer_notes', verbose_name='Müşteri')
    title = models.CharField(max_length=200, verbose_name='Başlık')
    content = models.TextField(verbose_name='İçerik')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Oluşturan')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Oluşturulma Tarihi')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Güncellenme Tarihi')

    class Meta:
        verbose_name = 'Müşteri Notu'
        verbose_name_plural = 'Müşteri Notları'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.customer.name} - {self.title}"

class CustomerDocument(models.Model):
    """Müşteri belgesi modeli"""
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='documents', verbose_name='Müşteri')
    title = models.CharField(max_length=200, verbose_name='Başlık')
    file = models.FileField(upload_to='customer_documents/', verbose_name='Dosya')
    description = models.TextField(blank=True, verbose_name='Açıklama')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Oluşturan')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Oluşturulma Tarihi')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Güncellenme Tarihi')

    class Meta:
        verbose_name = 'Müşteri Belgesi'
        verbose_name_plural = 'Müşteri Belgeleri'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.customer.name} - {self.title}"
