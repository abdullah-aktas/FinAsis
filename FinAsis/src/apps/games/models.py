# Bu dosyada model tanımı yok. Tüm form tanımlarını forms.py'ye taşıdım. Eğer model ekleyecekseniz buraya yazabilirsiniz.

from django.db import models

class Game(models.Model):
    name = models.CharField(max_length=100, verbose_name="Oyun Adı")
    description = models.TextField(verbose_name="Açıklama")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")

    def __str__(self):
        return self.name
