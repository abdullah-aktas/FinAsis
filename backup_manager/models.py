from django.db import models
from django.contrib.auth.models import User

class Backup(models.Model):
    name = models.CharField(max_length=255)
    file_path = models.FileField(upload_to='backups/')
    size = models.BigIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    backup_type = models.CharField(max_length=50, choices=[
        ('FULL', 'Tam Yedek'),
        ('INCREMENTAL', 'Artırımlı Yedek'),
        ('DIFFERENTIAL', 'Fark Yedek')
    ])
    status = models.CharField(max_length=50, choices=[
        ('PENDING', 'Beklemede'),
        ('IN_PROGRESS', 'Devam Ediyor'),
        ('COMPLETED', 'Tamamlandı'),
        ('FAILED', 'Başarısız')
    ])
    metadata = models.JSONField(default=dict)

    def __str__(self):
        return f"{self.name} - {self.created_at}"

class RestorePoint(models.Model):
    backup = models.ForeignKey(Backup, on_delete=models.CASCADE)
    restored_at = models.DateTimeField(auto_now_add=True)
    restored_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=50, choices=[
        ('PENDING', 'Beklemede'),
        ('IN_PROGRESS', 'Devam Ediyor'),
        ('COMPLETED', 'Tamamlandı'),
        ('FAILED', 'Başarısız')
    ])
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Restore from {self.backup.name} - {self.restored_at}"

class BackupSchedule(models.Model):
    name = models.CharField(max_length=255)
    backup_type = models.CharField(max_length=50, choices=[
        ('FULL', 'Tam Yedek'),
        ('INCREMENTAL', 'Artırımlı Yedek'),
        ('DIFFERENTIAL', 'Fark Yedek')
    ])
    frequency = models.CharField(max_length=50, choices=[
        ('DAILY', 'Günlük'),
        ('WEEKLY', 'Haftalık'),
        ('MONTHLY', 'Aylık')
    ])
    time = models.TimeField()
    is_active = models.BooleanField(default=True)
    last_run = models.DateTimeField(null=True, blank=True)
    next_run = models.DateTimeField(null=True, blank=True)
    retention_days = models.IntegerField(default=30)

    def __str__(self):
        return f"{self.name} - {self.frequency}" 