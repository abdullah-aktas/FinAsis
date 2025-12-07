from django.db import migrations


def forwards(apps, schema_editor):
    UserRole = apps.get_model("accounts", "UserRole")
    updates = [
        ("business_owner", "kobi_owner", "KOBİ Sahibi"),
        ("employee", "kobi_employee", "KOBİ Çalışanı"),
    ]
    for old_code, new_code, new_display in updates:
        try:
            role = UserRole.objects.get(name=old_code)
        except UserRole.DoesNotExist:
            continue
        if UserRole.objects.filter(name=new_code).exclude(pk=role.pk).exists():
            continue
        role.name = new_code
        role.display_name = new_display
        role.save(update_fields=["name", "display_name"])


def backwards(apps, schema_editor):
    UserRole = apps.get_model("accounts", "UserRole")
    updates = [
        ("kobi_owner", "business_owner", "İşletme Sahibi"),
        ("kobi_employee", "employee", "Çalışan"),
    ]
    for old_code, new_code, new_display in updates:
        try:
            role = UserRole.objects.get(name=old_code)
        except UserRole.DoesNotExist:
            continue
        if UserRole.objects.filter(name=new_code).exclude(pk=role.pk).exists():
            continue
        role.name = new_code
        role.display_name = new_display
        role.save(update_fields=["name", "display_name"])


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0010_subscriptionplan_userrole_rolebaseduserprofile_and_more"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
