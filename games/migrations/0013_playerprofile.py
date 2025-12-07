from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):
    dependencies = [
        ("games", "0012_remove_playerachievement_achievement_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="PlayerProfile",
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
                    "difficulty",
                    models.CharField(
                        choices=[
                            ("easy", "Kolay"),
                            ("medium", "Orta"),
                            ("hard", "Zor"),
                            ("adaptive", "Uyarlanır"),
                        ],
                        default="adaptive",
                        max_length=16,
                        verbose_name="Zorluk",
                    ),
                ),
                ("skill_trade", models.PositiveIntegerField(default=50)),
                ("skill_invest", models.PositiveIntegerField(default=50)),
                ("skill_budget", models.PositiveIntegerField(default=50)),
                ("skill_education", models.PositiveIntegerField(default=50)),
                ("stats", models.JSONField(blank=True, default=dict)),
                ("preferences", models.JSONField(blank=True, default=dict)),
                ("games_played", models.PositiveIntegerField(default=0)),
                ("last_recommended", models.JSONField(blank=True, default=dict)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="player_profile",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Oyuncu Profili",
                "verbose_name_plural": "Oyuncu Profilleri",
            },
        ),
    ]
