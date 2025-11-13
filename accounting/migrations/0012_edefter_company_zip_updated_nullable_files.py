from django.db import migrations, models
import django.db.models.deletion


def populate_edefter_company(apps, schema_editor):
    EDefter = apps.get_model('accounting', 'EDefter')
    Company = apps.get_model('accounting', 'Company')
    # Heuristic: if exactly 1 company exists, assign it; otherwise leave null
    try:
        company_count = Company.objects.count()
        default_company = Company.objects.first() if company_count == 1 else None
        if default_company:
            for ed in EDefter.objects.filter(company__isnull=True):
                ed.company = default_company
                ed.save(update_fields=['company'])
    except Exception:
        # Be conservative: on any error, do nothing; a follow-up migration can set values.
        pass


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0011_alter_invoice_kdv_rate'),
    ]

    operations = [
        # Make files nullable to match current model
        migrations.AlterField(
            model_name='edefter',
            name='xml_file',
            field=models.FileField(blank=True, null=True, upload_to='edefter/xml/', verbose_name='XML Dosyası'),
        ),
        migrations.AlterField(
            model_name='edefter',
            name='berat_file',
            field=models.FileField(blank=True, null=True, upload_to='edefter/berat/', verbose_name='Berat Dosyası'),
        ),
        # Add missing fields
        migrations.AddField(
            model_name='edefter',
            name='zip_file',
            field=models.FileField(blank=True, null=True, upload_to='edefter/zip/', verbose_name='ZIP Paketi'),
        ),
        migrations.AddField(
            model_name='edefter',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='Güncellenme Tarihi'),
        ),
        # Add company as nullable first
        migrations.AddField(
            model_name='edefter',
            name='company',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='edefters', to='accounting.company', verbose_name='Şirket'),
        ),
        # Backfill where safe
        migrations.RunPython(populate_edefter_company, migrations.RunPython.noop),
        # Enforce non-null to match model
        migrations.AlterField(
            model_name='edefter',
            name='company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='edefters', to='accounting.company', verbose_name='Şirket'),
        ),
    ]
