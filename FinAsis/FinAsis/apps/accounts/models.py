from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from FinAsis.apps.accounting.models import Company


class UserType(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=50)
    default_subscription = models.ForeignKey('SubscriptionType', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name

class SubscriptionType(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class CustomUser(AbstractUser):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True)
    role = models.CharField(max_length=50, choices=[
        ('admin', 'Yönetici'),
        ('staff', 'Çalışan'),
        ('viewer', 'İzleyici')
    ], default='staff')
    user_type = models.ForeignKey(UserType, on_delete=models.SET_NULL, null=True, blank=True)
    groups = models.ManyToManyField(
        Group,
        related_name='customuser_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups'
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customuser_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions'
    )

    def __str__(self):
        return f"{self.username} ({self.role})"

class Achievement(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='achievements', verbose_name="Şirket")
    title = models.CharField(max_length=100, verbose_name="Başlık")
    description = models.TextField(blank=True, null=True, verbose_name="Açıklama")
    icon = models.CharField(max_length=50, default="bi-trophy", verbose_name="İkon (Bootstrap)")
    date_earned = models.DateField(auto_now_add=True, verbose_name="Kazanılma Tarihi")

    def __str__(self):
        return f"{self.title} ({self.company})"

    class Meta:
        verbose_name = "Başarım"
        verbose_name_plural = "Başarımlar"
        ordering = ['-date_earned']

class UserSettings(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='settings', verbose_name="Kullanıcı")
    email_notifications = models.BooleanField(default=True, verbose_name="E-posta Bildirimleri")
    dark_mode = models.BooleanField(default=False, verbose_name="Koyu Tema Tercihi")

    def __str__(self):
        return f"Ayarlar: {self.user.username}"

    class Meta:
        verbose_name = "Kullanıcı Ayarları"
        verbose_name_plural = "Kullanıcı Ayarları"

class Subscription(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='subscription')
    subscription_type = models.ForeignKey(SubscriptionType, on_delete=models.SET_NULL, null=True)
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} - {self.subscription_type}"

class SubscriptionLog(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='subscription_logs')
    old_subscription = models.ForeignKey(SubscriptionType, on_delete=models.SET_NULL, null=True, blank=True, related_name='old_logs')
    new_subscription = models.ForeignKey(SubscriptionType, on_delete=models.SET_NULL, null=True, blank=True, related_name='new_logs')
    changed_at = models.DateTimeField(auto_now_add=True)
    note = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.user.username}: {self.old_subscription} → {self.new_subscription} ({self.changed_at:%Y-%m-%d %H:%M})"

# Create your models here.

# Not: Invoice modeli accounting uygulamasında tanımlı ve Company ile ilişkilidir.
