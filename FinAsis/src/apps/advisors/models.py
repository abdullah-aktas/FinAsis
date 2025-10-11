from django.db import models
from django.conf import settings


class AdvisorProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='advisor_profile')
    type = models.CharField(max_length=10, choices=(('SMMM','SMMM'),('YMM','YMM')))
    chamber_no = models.CharField(max_length=50, blank=True)
    mersis_no = models.CharField(max_length=50, blank=True)
    e_signature_serial = models.CharField(max_length=128, blank=True)
    mali_muhur_fingerprint = models.CharField(max_length=128, blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} ({self.type})"


class AdvisorRegistrySource(models.Model):
    source = models.CharField(max_length=50)
    external_id = models.CharField(max_length=100, blank=True)
    data = models.JSONField(default=dict, blank=True)
    fetched_at = models.DateTimeField(auto_now=True)


class TaxpayerProfile(models.Model):
    # Minimal taxpayer profile; can be linked to tenancy/company later
    name = models.CharField(max_length=255)
    vkn_tckn = models.CharField(max_length=20)
    mersis_no = models.CharField(max_length=50, blank=True)
    # Optional alignment with tenancy Company; backfilled progressively
    company = models.ForeignKey('tenancy.Company', null=True, blank=True, on_delete=models.SET_NULL, related_name='taxpayers')

    def __str__(self):
        return f"{self.name} ({self.vkn_tckn})"


class Engagement(models.Model):
    advisor = models.ForeignKey(AdvisorProfile, on_delete=models.CASCADE, related_name='engagements')
    taxpayer = models.ForeignKey(TaxpayerProfile, on_delete=models.CASCADE, related_name='engagements')
    scope = models.CharField(max_length=30, choices=(('defter','e-Defter'),('beyan','e-Beyan'),('both','Her ikisi')))
    status = models.CharField(max_length=20, choices=(('pending','Beklemede'),('active','Aktif'),('revoked','İptal')),
                              default='active')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('advisor','taxpayer','scope'),)

    def __str__(self):
        return f"{self.advisor} -> {self.taxpayer} ({self.scope})"
