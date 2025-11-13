# Generated migration for adding new user types

from django.db import migrations


def create_new_user_types(apps, schema_editor):
    """
    Yeni kullanıcı tiplerini oluşturur:
    - Muhasebe Elemanı
    - Satış Elemanı
    - Depo Elemanı
    """
    UserType = apps.get_model('accounts', 'UserType')
    
    new_user_types = [
        {
            'code': 'muhasebe_elemani',
            'name': 'Muhasebe Elemanı',
        },
        {
            'code': 'satis_elemani',
            'name': 'Satış Elemanı',
        },
        {
            'code': 'depo_elemani',
            'name': 'Depo Elemanı',
        },
    ]
    
    for user_type_data in new_user_types:
        UserType.objects.get_or_create(
            code=user_type_data['code'],
            defaults={
                'name': user_type_data['name'],
                'default_subscription': None
            }
        )
        print(f"✓ Created/Updated UserType: {user_type_data['name']}")


def reverse_create_user_types(apps, schema_editor):
    """
    Migration geri alınırsa, oluşturulan kullanıcı tiplerini siler.
    """
    UserType = apps.get_model('accounts', 'UserType')
    
    codes_to_remove = ['muhasebe_elemani', 'satis_elemani', 'depo_elemani']
    
    deleted_count = UserType.objects.filter(code__in=codes_to_remove).delete()[0]
    print(f"✓ Deleted {deleted_count} UserType records")


class Migration(migrations.Migration):
    """
    Bu migration yeni kullanıcı tiplerini ekler.
    """
    
    dependencies = [
        ('accounts', '0012_alter_userrole_name'),
    ]
    
    operations = [
        migrations.RunPython(
            create_new_user_types,
            reverse_code=reverse_create_user_types
        ),
    ]
