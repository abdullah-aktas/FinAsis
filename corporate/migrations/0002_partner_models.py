from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('corporate', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PartnerCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120, unique=True)),
                ('slug', models.SlugField(max_length=140, unique=True)),
                ('description', models.TextField(blank=True)),
                ('icon', models.CharField(blank=True, help_text='Bootstrap ikon adı veya özel sınıf.', max_length=80)),
                ('highlight_color', models.CharField(blank=True, help_text='Örn. #0AAE94 veya tailwind sınıfı.', max_length=32)),
                ('priority', models.PositiveIntegerField(default=100)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Partner Kategorisi',
                'verbose_name_plural': 'Partner Kategorileri',
                'ordering': ('priority', 'name'),
            },
        ),
        migrations.CreateModel(
            name='PartnerApplication',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company_name', models.CharField(max_length=180)),
                ('brand_name', models.CharField(blank=True, max_length=160)),
                ('contact_name', models.CharField(max_length=150)),
                ('contact_email', models.EmailField(max_length=254)),
                ('contact_phone', models.CharField(blank=True, max_length=50)),
                ('job_title', models.CharField(blank=True, max_length=120)),
                ('website', models.URLField(blank=True)),
                ('country', models.CharField(blank=True, max_length=80)),
                ('city', models.CharField(blank=True, max_length=80)),
                ('team_size', models.CharField(blank=True, max_length=60)),
                ('integration_focus', models.JSONField(blank=True, default=list)),
                ('product_notes', models.TextField(blank=True)),
                ('message', models.TextField(blank=True)),
                ('go_live_timeline', models.CharField(blank=True, max_length=120)),
                ('revenue_model', models.CharField(blank=True, max_length=120)),
                ('sandbox_needs', models.TextField(blank=True)),
                ('status', models.CharField(choices=[('new', 'Yeni'), ('in_review', 'İncelemede'), ('approved', 'Onaylandı'), ('waitlist', 'Beklemede'), ('rejected', 'Reddedildi')], default='new', max_length=20)),
                ('decision_notes', models.TextField(blank=True)),
                ('reviewed_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('assigned_to', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='partner_applications', to=settings.AUTH_USER_MODEL)),
                ('primary_category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='primary_applications', to='corporate.partnercategory')),
            ],
            options={
                'verbose_name': 'Partner Başvurusu',
                'verbose_name_plural': 'Partner Başvuruları',
                'ordering': ('-created_at',),
            },
        ),
        migrations.CreateModel(
            name='PartnerListing',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('slug', models.SlugField(max_length=160, unique=True)),
                ('tagline', models.CharField(blank=True, max_length=180)),
                ('summary', models.TextField(blank=True)),
                ('description', models.TextField(blank=True)),
                ('website', models.URLField(blank=True)),
                ('contact_email', models.EmailField(blank=True, max_length=254)),
                ('logo_url', models.URLField(blank=True, help_text='CDN veya medya kütüphanesi URL\'si.')),
                ('badge_label', models.CharField(blank=True, max_length=60)),
                ('capabilities', models.JSONField(blank=True, default=list)),
                ('regions', models.JSONField(blank=True, default=list)),
                ('integrations', models.JSONField(blank=True, default=list)),
                ('cta_label', models.CharField(default='Demo Talep Et', max_length=80)),
                ('cta_url', models.URLField(blank=True)),
                ('status', models.CharField(choices=[('draft', 'Taslak'), ('review', 'İncelemede'), ('published', 'Yayında'), ('archived', 'Arşivlendi')], default='draft', max_length=20)),
                ('is_featured', models.BooleanField(default=False)),
                ('feature_order', models.PositiveIntegerField(default=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='partners', to='corporate.partnercategory')),
            ],
            options={
                'verbose_name': 'Partner Liste Kaydı',
                'verbose_name_plural': 'Partner Liste Kayıtları',
                'ordering': ('feature_order', 'name'),
            },
        ),
        migrations.CreateModel(
            name='PartnerApplicationEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(max_length=60)),
                ('from_status', models.CharField(blank=True, max_length=20)),
                ('to_status', models.CharField(blank=True, max_length=20)),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('actor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='partner_application_events', to=settings.AUTH_USER_MODEL)),
                ('application', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='events', to='corporate.partnerapplication')),
            ],
            options={
                'verbose_name': 'Partner Başvuru Logu',
                'verbose_name_plural': 'Partner Başvuru Logları',
                'ordering': ('-created_at',),
            },
        ),
        migrations.AddField(
            model_name='partnerapplication',
            name='categories',
            field=models.ManyToManyField(blank=True, related_name='applications', to='corporate.partnercategory'),
        ),
    ]

