from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        ("security", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="SecurityAuditLog",
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
                ("action", models.CharField(max_length=120)),
                ("resource", models.CharField(blank=True, max_length=255)),
                ("ip_address", models.GenericIPAddressField(blank=True, null=True)),
                ("user_agent", models.TextField(blank=True)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("success", models.BooleanField(default=True)),
                (
                    "occurred_at",
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "actor",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="security_audit_logs",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Güvenlik Audit Logu",
                "verbose_name_plural": "Güvenlik Audit Logları",
                "ordering": ("-occurred_at",),
            },
        ),
        migrations.AddIndex(
            model_name="securityauditlog",
            index=models.Index(
                fields=("action", "occurred_at"), name="security_se_action__f34f6a_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="securityauditlog",
            index=models.Index(
                fields=("actor", "occurred_at"), name="security_se_actor__b0f690_idx"
            ),
        ),
    ]
