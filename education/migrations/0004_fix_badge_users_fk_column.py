from django.db import migrations


def rename_badge_users_fk_forward(apps, schema_editor):
    cursor = schema_editor.connection.cursor()
    try:
        cursor.execute("PRAGMA table_info(education_badge_users)")
        cols = [row[1] for row in cursor.fetchall()]
    except Exception:
        return  # table may not exist
    if "customuser_id" not in cols and "user_id" in cols:
        try:
            cursor.execute(
                "ALTER TABLE education_badge_users RENAME COLUMN user_id TO customuser_id"
            )
        except Exception:
            pass


def rename_badge_users_fk_backward(apps, schema_editor):
    cursor = schema_editor.connection.cursor()
    try:
        cursor.execute("PRAGMA table_info(education_badge_users)")
        cols = [row[1] for row in cursor.fetchall()]
    except Exception:
        return
    if "user_id" not in cols and "customuser_id" in cols:
        try:
            cursor.execute(
                "ALTER TABLE education_badge_users RENAME COLUMN customuser_id TO user_id"
            )
        except Exception:
            pass


class Migration(migrations.Migration):
    dependencies = [
        ("education", "0003_meetinginvitation"),
    ]

    operations = [
        migrations.RunPython(
            rename_badge_users_fk_forward, rename_badge_users_fk_backward
        ),
    ]
