from django.db import models


class PressRelease(models.Model):
    title = models.CharField(max_length=200)
    date = models.DateField()
    summary = models.TextField(blank=True)
    url = models.URLField(blank=True)

    class Meta:
        ordering = ['-date']
        verbose_name = 'Basın Bülteni'
        verbose_name_plural = 'Basın Bültenleri'

    def __str__(self):
        return f"{self.date} - {self.title}"


class InvestorDocument(models.Model):
    name = models.CharField(max_length=200)
    file_url = models.URLField()
    kind = models.CharField(max_length=50, choices=[('deck','Sunum'),('report','Rapor')])
    published_at = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['-published_at', 'name']
        verbose_name = 'Yatırımcı Belgesi'
        verbose_name_plural = 'Yatırımcı Belgeleri'

    def __str__(self):
        return self.name


class TeamMember(models.Model):
    name = models.CharField(max_length=120)
    role = models.CharField(max_length=120)
    department = models.CharField(max_length=120, blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Ekip Üyesi'
        verbose_name_plural = 'Ekip Üyeleri'

    def __str__(self):
        return f"{self.name} - {self.role}"
