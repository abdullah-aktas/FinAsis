from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ai_assistant', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SectorBenchmark',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sector_key', models.CharField(max_length=50, unique=True, verbose_name='Sektör Anahtarı (slug)')),
                ('display_name', models.CharField(max_length=100, verbose_name='Görünen Ad')),
                ('margin_min', models.FloatField(blank=True, null=True, verbose_name='Hedef Net Kar Marjı Min (%)')),
                ('current_ratio_min', models.FloatField(blank=True, null=True, verbose_name='Hedef Cari Oran Min')),
                ('dte_max', models.FloatField(blank=True, null=True, verbose_name='Hedef Borç/Özsermaye Max')),
                ('opex_ratio_max', models.FloatField(blank=True, null=True, verbose_name='Hedef Faaliyet Gider Oranı Max')),
                ('is_active', models.BooleanField(default=True, verbose_name='Aktif')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Sektör Kıyas Hedefi',
                'verbose_name_plural': 'Sektör Kıyas Hedefleri',
                'ordering': ['sector_key'],
            },
        ),
    ]


