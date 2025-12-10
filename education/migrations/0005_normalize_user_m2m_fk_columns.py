from django.db import migrations, connection


TABLES_AND_COLS = [
    ("education_course_students", "user_id", "customuser_id"),
    ("education_groupassignment_members", "user_id", "customuser_id"),
]


def forward(apps, schema_editor):
    """Rename user_id to customuser_id in multiple tables."""
    db_engine = connection.settings_dict.get("ENGINE", "")
    is_postgresql = "postgresql" in db_engine.lower()
    is_sqlite = "sqlite" in db_engine.lower()

    cursor = schema_editor.connection.cursor()

    for table, old_col, new_col in TABLES_AND_COLS:
        # Check if table exists and get columns
        if is_postgresql:
            # Check if table exists
            cursor.execute(
                """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = %s
                );
                """,
                [table],
            )
            table_exists = cursor.fetchone()[0]
            if not table_exists:
                continue

            # Get columns
            cursor.execute(
                """
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_schema = 'public' 
                AND table_name = %s
                AND column_name IN (%s, %s);
                """,
                [table, old_col, new_col],
            )
            cols = [row[0] for row in cursor.fetchall()]
        elif is_sqlite:
            try:
                cursor.execute(f"PRAGMA table_info({table})")
                cols = [row[1] for row in cursor.fetchall()]
            except Exception:
                continue
        else:
            continue  # Unknown database engine

        # Rename column if needed
        if new_col not in cols and old_col in cols:
            try:
                cursor.execute(
                    f"ALTER TABLE {table} RENAME COLUMN {old_col} TO {new_col}"
                )
            except Exception:
                pass  # Column may already be renamed or table structure changed


def backward(apps, schema_editor):
    """Rename customuser_id back to user_id in multiple tables."""
    db_engine = connection.settings_dict.get("ENGINE", "")
    is_postgresql = "postgresql" in db_engine.lower()
    is_sqlite = "sqlite" in db_engine.lower()

    cursor = schema_editor.connection.cursor()

    for table, old_col, new_col in TABLES_AND_COLS:
        # Check if table exists and get columns
        if is_postgresql:
            # Check if table exists
            cursor.execute(
                """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = %s
                );
                """,
                [table],
            )
            table_exists = cursor.fetchone()[0]
            if not table_exists:
                continue

            # Get columns
            cursor.execute(
                """
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_schema = 'public' 
                AND table_name = %s
                AND column_name IN (%s, %s);
                """,
                [table, old_col, new_col],
            )
            cols = [row[0] for row in cursor.fetchall()]
        elif is_sqlite:
            try:
                cursor.execute(f"PRAGMA table_info({table})")
                cols = [row[1] for row in cursor.fetchall()]
            except Exception:
                continue
        else:
            continue  # Unknown database engine

        # Rename column if needed
        if old_col not in cols and new_col in cols:
            try:
                cursor.execute(
                    f"ALTER TABLE {table} RENAME COLUMN {new_col} TO {old_col}"
                )
            except Exception:
                pass  # Column may already be renamed or table structure changed


class Migration(migrations.Migration):
    dependencies = [
        ("education", "0004_fix_badge_users_fk_column"),
    ]

    # atomic=False: Migration'ı transaction dışında çalıştır
    # Böylece bir hata olsa bile diğer migration'lar çalışmaya devam edebilir
    atomic = False

    operations = [
        migrations.RunPython(
            forward,
            backward,
            atomic=False,  # Bu migration atomic değil
        ),
    ]
