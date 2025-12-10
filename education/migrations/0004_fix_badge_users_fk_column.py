from django.db import migrations, connection


def rename_badge_users_fk_forward(apps, schema_editor):
    """Rename user_id to customuser_id in education_badge_users table."""
    db_engine = connection.settings_dict.get("ENGINE", "")
    is_postgresql = "postgresql" in db_engine.lower()
    is_sqlite = "sqlite" in db_engine.lower()

    cursor = schema_editor.connection.cursor()

    # Check if table exists
    if is_postgresql:
        cursor.execute(
            """
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'education_badge_users'
            );
            """
        )
        table_exists = cursor.fetchone()[0]
        if not table_exists:
            return

        # Check if columns exist
        cursor.execute(
            """
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_schema = 'public' 
            AND table_name = 'education_badge_users'
            AND column_name IN ('user_id', 'customuser_id');
            """
        )
        cols = [row[0] for row in cursor.fetchall()]
    elif is_sqlite:
        try:
            cursor.execute("PRAGMA table_info(education_badge_users)")
            cols = [row[1] for row in cursor.fetchall()]
        except Exception:
            return  # table may not exist
    else:
        return  # Unknown database engine

    # Rename column if needed
    if "customuser_id" not in cols and "user_id" in cols:
        try:
            cursor.execute(
                "ALTER TABLE education_badge_users RENAME COLUMN user_id TO customuser_id"
            )
        except Exception:
            pass  # Column may already be renamed or table structure changed


def rename_badge_users_fk_backward(apps, schema_editor):
    """Rename customuser_id back to user_id in education_badge_users table."""
    db_engine = connection.settings_dict.get("ENGINE", "")
    is_postgresql = "postgresql" in db_engine.lower()
    is_sqlite = "sqlite" in db_engine.lower()

    cursor = schema_editor.connection.cursor()

    # Check if table exists
    if is_postgresql:
        cursor.execute(
            """
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'education_badge_users'
            );
            """
        )
        table_exists = cursor.fetchone()[0]
        if not table_exists:
            return

        # Check if columns exist
        cursor.execute(
            """
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_schema = 'public' 
            AND table_name = 'education_badge_users'
            AND column_name IN ('user_id', 'customuser_id');
            """
        )
        cols = [row[0] for row in cursor.fetchall()]
    elif is_sqlite:
        try:
            cursor.execute("PRAGMA table_info(education_badge_users)")
            cols = [row[1] for row in cursor.fetchall()]
        except Exception:
            return
    else:
        return  # Unknown database engine

    # Rename column if needed
    if "user_id" not in cols and "customuser_id" in cols:
        try:
            cursor.execute(
                "ALTER TABLE education_badge_users RENAME COLUMN customuser_id TO user_id"
            )
        except Exception:
            pass  # Column may already be renamed or table structure changed


class Migration(migrations.Migration):
    dependencies = [
        ("education", "0003_meetinginvitation"),
    ]

    # atomic=False: Migration'ı transaction dışında çalıştır
    # Böylece bir hata olsa bile diğer migration'lar çalışmaya devam edebilir
    atomic = False

    operations = [
        migrations.RunPython(
            rename_badge_users_fk_forward,
            rename_badge_users_fk_backward,
            atomic=False,  # Bu migration atomic değil
        ),
    ]
