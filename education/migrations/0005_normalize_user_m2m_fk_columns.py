from django.db import migrations


TABLES_AND_COLS = [
    ("education_course_students", "user_id", "customuser_id"),
    ("education_groupassignment_members", "user_id", "customuser_id"),
]


def forward(apps, schema_editor):
    cursor = schema_editor.connection.cursor()
    for table, old_col, new_col in TABLES_AND_COLS:
        try:
            cursor.execute(f"PRAGMA table_info({table})")
            cols = [row[1] for row in cursor.fetchall()]
        except Exception:
            continue
        if new_col not in cols and old_col in cols:
            try:
                cursor.execute(f"ALTER TABLE {table} RENAME COLUMN {old_col} TO {new_col}")
            except Exception:
                pass


def backward(apps, schema_editor):
    cursor = schema_editor.connection.cursor()
    for table, old_col, new_col in TABLES_AND_COLS:
        try:
            cursor.execute(f"PRAGMA table_info({table})")
            cols = [row[1] for row in cursor.fetchall()]
        except Exception:
            continue
        if old_col not in cols and new_col in cols:
            try:
                cursor.execute(f"ALTER TABLE {table} RENAME COLUMN {new_col} TO {old_col}")
            except Exception:
                pass


class Migration(migrations.Migration):
    dependencies = [
        ("education", "0004_fix_badge_users_fk_column"),
    ]

    operations = [
        migrations.RunPython(forward, backward),
    ]
