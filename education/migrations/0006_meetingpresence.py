from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):
    dependencies = [
        ("education", "0005_normalize_user_m2m_fk_columns"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="MeetingPresence",
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
                    "joined_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="Katılım"),
                ),
                (
                    "left_at",
                    models.DateTimeField(blank=True, null=True, verbose_name="Ayrılış"),
                ),
                (
                    "client_id",
                    models.CharField(
                        blank=True, max_length=64, verbose_name="İstemci Kimliği"
                    ),
                ),
                (
                    "meeting",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        related_name="presences",
                        to="education.meeting",
                        verbose_name="Toplantı",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        related_name="meeting_presences",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Kullanıcı",
                    ),
                ),
            ],
            options={
                "verbose_name": "Toplantı Varlığı",
                "verbose_name_plural": "Toplantı Varlıkları",
            },
        ),
        migrations.AddIndex(
            model_name="meetingpresence",
            index=models.Index(
                fields=["meeting", "user", "joined_at"],
                name="education_meetingpresence_idx",
            ),
        ),
    ]
