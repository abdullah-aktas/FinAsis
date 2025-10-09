from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission, UserManager
from src.apps.accounting.models import Company


class CustomUserQuerySet(models.QuerySet["CustomUser"]):
    """Kullanıcı listelerinde N+1'ı önlemek için ilişkileri hazırla."""
    def with_related(self):
        return self.select_related('company').prefetch_related('groups', 'user_permissions')


# from_queryset ile dinamik oluşturulan manager'lar migration sırasında serileştirilemediği
# için adlandırılmış bir sınıf olarak tanımlıyoruz.
class CustomUserManager(UserManager):
    def get_queryset(self):
        return CustomUserQuerySet(self.model, using=self._db)

    # Manager üzerinden de aynı API'yi sunalım
    def with_related(self):
        return self.get_queryset().with_related()


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
    audience = models.CharField(
        max_length=20,
        choices=[
            ('sme', 'KOBİ'),
            ('edu_student', 'Öğrenci'),
            ('edu_teacher', 'Öğretmen'),
            ('edu_campus', 'Kampüs/Okul'),
        ],
        default='sme'
    )
    period_options = models.CharField(
        max_length=20,
        choices=[
            ('monthly', 'Aylık'),
            ('yearly', 'Yıllık'),
            ('monthly_yearly', 'Aylık/Yıllık'),
        ],
        default='monthly'
    )
    monthly_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    yearly_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    user_limit = models.IntegerField(null=True, blank=True)  # None/sınırsız
    features = models.JSONField(default=list, blank=True)

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
    # Varsayılan manager: adlandırılmış CustomUserManager kullan
    objects = CustomUserManager()
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
