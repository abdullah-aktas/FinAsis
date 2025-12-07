from __future__ import annotations

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("accounting", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="DeveloperAPIKey",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("name", models.CharField(max_length=120)),
                ("description", models.TextField(blank=True)),
                (
                    "prefix",
                    models.CharField(db_index=True, editable=False, max_length=12),
                ),
                ("hashed_key", models.CharField(editable=False, max_length=128)),
                (
                    "rate_limit_plan",
                    models.CharField(default="standard", max_length=32),
                ),
                ("allowed_ips", models.JSONField(blank=True, default=list)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("active", "Active"),
                            ("rotated", "Rotated"),
                            ("revoked", "Revoked"),
                        ],
                        default="active",
                        max_length=16,
                    ),
                ),
                ("expires_at", models.DateTimeField(blank=True, null=True)),
                ("last_used_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "organization",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="developer_api_keys",
                        to="accounting.company",
                    ),
                ),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="developer_api_keys",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Developer API Key",
                "verbose_name_plural": "Developer API Keys",
                "ordering": ("-created_at",),
                "permissions": [
                    ("manage_keys", "Developer portal API anahtarlarını yönetebilir")
                ],
            },
        ),
        migrations.CreateModel(
            name="DeveloperPortalAuditLog",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("action", models.CharField(max_length=64)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "actor",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="developer_portal_audit_logs",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "api_key",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="audit_logs",
                        to="developer_portal.developerapikey",
                    ),
                ),
            ],
            options={
                "verbose_name": "Developer Portal Audit Log",
                "verbose_name_plural": "Developer Portal Audit Logs",
                "ordering": ("-created_at",),
            },
        ),
        migrations.CreateModel(
            name="APIKeyUsageLog",
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
                ("path", models.CharField(max_length=255)),
                ("method", models.CharField(max_length=8)),
                ("response_code", models.IntegerField()),
                ("duration_ms", models.IntegerField()),
                ("client_ip", models.GenericIPAddressField(blank=True, null=True)),
                ("user_agent", models.CharField(blank=True, max_length=255)),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
                (
                    "api_key",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="usage_logs",
                        to="developer_portal.developerapikey",
                    ),
                ),
            ],
            options={
                "verbose_name": "API Key Usage Log",
                "verbose_name_plural": "API Key Usage Logs",
                "ordering": ("-timestamp",),
            },
        ),
        migrations.AddIndex(
            model_name="developerapikey",
            index=models.Index(
                fields=("prefix", "status"), name="developer__prefix_ab512f_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="developerapikey",
            index=models.Index(
                fields=("organization", "status"), name="developer__organiza_d6fe4d_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="apikeyusagelog",
            index=models.Index(
                fields=("api_key", "timestamp"), name="developer__api_key_058ed9_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="apikeyusagelog",
            index=models.Index(
                fields=("api_key", "response_code"),
                name="developer__api_key_413f21_idx",
            ),
        ),
    ]
