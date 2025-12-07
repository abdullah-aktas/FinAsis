from __future__ import annotations

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

import partners.models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="PartnerCategory",
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
                    "code",
                    models.SlugField(
                        max_length=50, unique=True, verbose_name="Kategori Kodu"
                    ),
                ),
                ("name", models.CharField(max_length=150, verbose_name="Kategori Adı")),
                ("description", models.TextField(blank=True, verbose_name="Açıklama")),
                (
                    "icon",
                    models.CharField(blank=True, max_length=100, verbose_name="Simge"),
                ),
                (
                    "sort_order",
                    models.PositiveIntegerField(default=0, verbose_name="Sıra"),
                ),
            ],
            options={
                "verbose_name": "Partner Kategorisi",
                "verbose_name_plural": "Partner Kategorileri",
                "ordering": ("sort_order", "name"),
            },
        ),
        migrations.CreateModel(
            name="PartnerApplication",
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
                    "company_name",
                    models.CharField(max_length=200, verbose_name="Şirket Adı"),
                ),
                (
                    "contact_name",
                    models.CharField(max_length=120, verbose_name="İletişim Kişisi"),
                ),
                (
                    "contact_email",
                    models.EmailField(max_length=254, verbose_name="E-posta"),
                ),
                (
                    "contact_phone",
                    models.CharField(blank=True, max_length=50, verbose_name="Telefon"),
                ),
                ("website_url", models.URLField(blank=True, verbose_name="Web Sitesi")),
                (
                    "partner_type",
                    models.CharField(
                        choices=[
                            ("erp", "ERP Entegratörü"),
                            ("crm", "CRM / Satış Otomasyonu"),
                            ("compliance", "Uyumluluk / RegTech"),
                            ("education", "Eğitim / LMS"),
                            ("payment", "Ödeme / FinTech"),
                            ("consulting", "Danışmanlık"),
                            ("other", "Diğer"),
                        ],
                        max_length=20,
                        verbose_name="Partner Tipi",
                    ),
                ),
                (
                    "integration_focus",
                    models.CharField(
                        help_text="Örn. e-Fatura, muhasebe, eğitim içeriği",
                        max_length=200,
                        verbose_name="Entegrasyon Odağı",
                    ),
                ),
                (
                    "target_customer_segments",
                    models.CharField(
                        blank=True,
                        max_length=200,
                        verbose_name="Hedef Müşteri Segmentleri",
                    ),
                ),
                (
                    "regions",
                    models.CharField(
                        blank=True,
                        max_length=200,
                        verbose_name="Hizmet Verilen Bölgeler",
                    ),
                ),
                (
                    "sandbox_url",
                    models.URLField(blank=True, verbose_name="Sandbox / Demo URL"),
                ),
                (
                    "compliance_notes",
                    models.TextField(
                        blank=True,
                        help_text="Sertifikalar, KVKK uyumluluğu, güvenlik uygulamaları",
                        verbose_name="Uyumluluk Notları",
                    ),
                ),
                (
                    "go_to_market_plan",
                    models.TextField(
                        blank=True,
                        help_text="Ortak kampanyalar, hedefler",
                        verbose_name="Pazara Giriş Planı",
                    ),
                ),
                (
                    "additional_notes",
                    models.TextField(blank=True, verbose_name="Ek Notlar"),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("received", "Alındı"),
                            ("reviewing", "İnceleniyor"),
                            ("approved", "Onaylandı"),
                            ("rejected", "Reddedildi"),
                        ],
                        default="received",
                        max_length=20,
                        verbose_name="Durum",
                    ),
                ),
                (
                    "reviewed_at",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="İnceleme Tarihi"
                    ),
                ),
                (
                    "metadata",
                    models.JSONField(
                        blank=True,
                        default=partners.models.default_metadata,
                        verbose_name="Ek Veriler",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Gönderim Tarihi"
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True, verbose_name="Güncelleme Tarihi"
                    ),
                ),
                (
                    "reviewed_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="partner_portal_reviews",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="İnceleyen",
                    ),
                ),
                (
                    "submitted_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="partner_portal_submissions",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Gönderen Kullanıcı",
                    ),
                ),
            ],
            options={
                "verbose_name": "Partner Başvurusu",
                "verbose_name_plural": "Partner Başvuruları",
                "ordering": ("-created_at",),
            },
        ),
        migrations.CreateModel(
            name="PartnerProfile",
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
                ("name", models.CharField(max_length=200, verbose_name="Partner Adı")),
                (
                    "slug",
                    models.SlugField(max_length=200, unique=True, verbose_name="Slug"),
                ),
                (
                    "headline",
                    models.CharField(
                        blank=True, max_length=200, verbose_name="Kısa Başlık"
                    ),
                ),
                ("description", models.TextField(verbose_name="Açıklama")),
                (
                    "integration_focus",
                    models.CharField(
                        blank=True, max_length=200, verbose_name="Entegrasyon Odağı"
                    ),
                ),
                ("website_url", models.URLField(blank=True, verbose_name="Web Sitesi")),
                (
                    "contact_email",
                    models.EmailField(
                        blank=True, max_length=254, verbose_name="İletişim E-postası"
                    ),
                ),
                (
                    "badge_label",
                    models.CharField(blank=True, max_length=100, verbose_name="Rozet"),
                ),
                (
                    "regions",
                    models.CharField(
                        blank=True, max_length=200, verbose_name="Hizmet Bölgeleri"
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("draft", "Taslak"),
                            ("review", "İncelemede"),
                            ("published", "Yayında"),
                            ("archived", "Arşivlendi"),
                        ],
                        default="draft",
                        max_length=20,
                        verbose_name="Durum",
                    ),
                ),
                (
                    "is_featured",
                    models.BooleanField(default=False, verbose_name="Öne Çıkan"),
                ),
                (
                    "sort_order",
                    models.PositiveIntegerField(default=0, verbose_name="Sıra"),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="Oluşturma"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="Güncelleme"),
                ),
                (
                    "category",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="partners",
                        to="partners.partnercategory",
                        verbose_name="Kategori",
                    ),
                ),
            ],
            options={
                "verbose_name": "Partner Profili",
                "verbose_name_plural": "Partner Profilleri",
                "ordering": ("sort_order", "name"),
            },
        ),
        migrations.AddIndex(
            model_name="partnerapplication",
            index=models.Index(
                fields=("status", "created_at"), name="partners_pa_status_0ee13f_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="partnerapplication",
            index=models.Index(
                fields=("partner_type",), name="partners_pa_partner_37f9d3_idx"
            ),
        ),
    ]
