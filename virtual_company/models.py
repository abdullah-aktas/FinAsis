from django.db import models
from django.conf import settings

class VirtualCompany(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    capital = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    def __str__(self):
        return self.company_name

    class Meta:
        verbose_name = 'Sanal Şirket'
        verbose_name_plural = 'Sanal Şirketler' 