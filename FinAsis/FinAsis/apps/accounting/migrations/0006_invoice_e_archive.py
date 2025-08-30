from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0005_edefter_company_base_currency_company_country_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='e_archive',
            field=models.BooleanField(default=False, verbose_name='e-Arşiv'),
        ),
    ]


