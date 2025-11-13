from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("developer_portal", "0002_rename_developer__api_key_058ed9_idx_developer_p_api_key_2199ed_idx_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="WebhookTestLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("event_type", models.CharField(max_length=64)),
                ("target_url", models.URLField()),
                ("request_headers", models.JSONField(blank=True, default=dict)),
                ("payload", models.JSONField(blank=True, default=dict)),
                ("signature", models.CharField(blank=True, max_length=128)),
                ("response_status", models.IntegerField(blank=True, null=True)),
                ("response_body", models.TextField(blank=True)),
                ("duration_ms", models.IntegerField(blank=True, null=True)),
                ("error", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "actor",
                    models.ForeignKey(
                        null=True,
                        on_delete=models.deletion.SET_NULL,
                        related_name="developer_webhook_tests",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Webhook Test Logu",
                "verbose_name_plural": "Webhook Test Logları",
                "ordering": ("-created_at",),
            },
        ),
        migrations.AddIndex(
            model_name="webhooktestlog",
            index=models.Index(fields=("event_type", "created_at"), name="developer_p_event_t_d3e07c_idx"),
        ),
        migrations.AddIndex(
            model_name="webhooktestlog",
            index=models.Index(fields=("actor", "created_at"), name="developer_p_actor_i_975d64_idx"),
        ),
    ]

