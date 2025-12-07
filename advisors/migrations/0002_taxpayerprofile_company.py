from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("tenancy", "0001_initial"),
        ("advisors", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="taxpayerprofile",
            name="company",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.SET_NULL,
                related_name="taxpayers",
                to="tenancy.company",
            ),
        ),
    ]
