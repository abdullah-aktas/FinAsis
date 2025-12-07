# Generated migration for ErrorLog model

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("common", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="ErrorLog",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "severity",
                    models.CharField(
                        choices=[
                            ("DEBUG", "Debug"),
                            ("INFO", "Info"),
                            ("WARNING", "Warning"),
                            ("ERROR", "Error"),
                            ("CRITICAL", "Critical"),
                        ],
                        default="ERROR",
                        max_length=20,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("NEW", "Yeni"),
                            ("INVESTIGATING", "İnceleniyor"),
                            ("RESOLVED", "Çözüldü"),
                            ("IGNORED", "Yok Sayıldı"),
                        ],
                        default="NEW",
                        max_length=20,
                    ),
                ),
                (
                    "error_type",
                    models.CharField(max_length=200, verbose_name="Hata Tipi"),
                ),
                ("error_message", models.TextField(verbose_name="Hata Mesajı")),
                ("traceback", models.TextField(blank=True, verbose_name="Stack Trace")),
                (
                    "url",
                    models.URLField(blank=True, max_length=500, verbose_name="URL"),
                ),
                (
                    "method",
                    models.CharField(
                        blank=True, max_length=10, verbose_name="HTTP Method"
                    ),
                ),
                ("ip_address", models.GenericIPAddressField(blank=True, null=True)),
                ("user_agent", models.TextField(blank=True)),
                (
                    "request_data",
                    models.JSONField(
                        blank=True, default=dict, verbose_name="Request Data"
                    ),
                ),
                (
                    "headers",
                    models.JSONField(blank=True, default=dict, verbose_name="Headers"),
                ),
                ("server_name", models.CharField(blank=True, max_length=200)),
                ("python_version", models.CharField(blank=True, max_length=50)),
                ("django_version", models.CharField(blank=True, max_length=50)),
                (
                    "first_seen",
                    models.DateTimeField(auto_now_add=True, verbose_name="İlk Görüldü"),
                ),
                (
                    "last_seen",
                    models.DateTimeField(auto_now=True, verbose_name="Son Görüldü"),
                ),
                (
                    "occurrence_count",
                    models.IntegerField(default=1, verbose_name="Tekrar Sayısı"),
                ),
                ("resolved_at", models.DateTimeField(blank=True, null=True)),
                ("resolution_notes", models.TextField(blank=True)),
                ("admin_notified", models.BooleanField(default=False)),
                ("notification_sent_at", models.DateTimeField(blank=True, null=True)),
                (
                    "resolved_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="beta_resolved_errors",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="beta_errors",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Hata Kaydı",
                "verbose_name_plural": "Hata Kayıtları",
                "ordering": ["-last_seen"],
            },
        ),
        migrations.AddIndex(
            model_name="errorlog",
            index=models.Index(fields=["-last_seen"], name="common_erro_last_se_idx"),
        ),
        migrations.AddIndex(
            model_name="errorlog",
            index=models.Index(
                fields=["severity", "status"], name="common_erro_severit_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="errorlog",
            index=models.Index(
                fields=["error_type", "-last_seen"], name="common_erro_error_t_idx"
            ),
        ),
    ]
