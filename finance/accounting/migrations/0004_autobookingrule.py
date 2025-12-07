from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("accounting", "0005_edefter_company_base_currency_company_country_and_more"),
        ("finance", "0003_transaction_status"),
    ]

    operations = [
        migrations.CreateModel(
            name="AutoBookingRule",
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
                ("name", models.CharField(max_length=100, verbose_name="Kural Adı")),
                (
                    "keyword_pattern",
                    models.CharField(
                        max_length=255, verbose_name="Anahtar Kelime / Regex"
                    ),
                ),
                (
                    "nature",
                    models.CharField(
                        choices=[
                            ("purchase", "Alış"),
                            ("sales", "Satış"),
                            ("expense", "Gider"),
                            ("bank", "Banka"),
                        ],
                        default="expense",
                        max_length=20,
                        verbose_name="İşlem Türü",
                    ),
                ),
                (
                    "debit_account_code",
                    models.CharField(
                        blank=True,
                        max_length=20,
                        null=True,
                        verbose_name="Borç Hesap Kodu",
                    ),
                ),
                (
                    "credit_account_code",
                    models.CharField(
                        blank=True,
                        max_length=20,
                        null=True,
                        verbose_name="Alacak Hesap Kodu",
                    ),
                ),
                (
                    "kdv_account_code",
                    models.CharField(
                        blank=True,
                        max_length=20,
                        null=True,
                        verbose_name="KDV Hesap Kodu",
                    ),
                ),
                (
                    "priority",
                    models.PositiveIntegerField(
                        default=100, verbose_name="Öncelik (küçük önce)"
                    ),
                ),
                ("is_active", models.BooleanField(default=True, verbose_name="Aktif")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "company",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="auto_booking_rules",
                        to="accounting.company",
                        verbose_name="Şirket",
                    ),
                ),
            ],
            options={
                "verbose_name": "Otomatik Fişleme Kuralı",
                "verbose_name_plural": "Otomatik Fişleme Kuralları",
                "ordering": ["company", "priority", "name"],
                "unique_together": {("company", "name")},
            },
        ),
    ]
