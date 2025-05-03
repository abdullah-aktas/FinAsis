from django.db import models
from django.utils.translation import gettext_lazy as _

class BaseModel(models.Model):
    """Tüm modeller için temel sınıf"""
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Oluşturulma Tarihi'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Güncellenme Tarihi'))
    is_active = models.BooleanField(default=True, verbose_name=_('Aktif'))

    class Meta:
        abstract = True