import uuid

from django.conf import settings
from django.db import migrations, models


def migrate_attendance_to_uuid(apps, schema_editor):
    schema_editor.execute("""
        ALTER TABLE attendance_attendance
        ADD COLUMN id_uuid uuid;
    """)

    schema_editor.execute("""
        UPDATE attendance_attendance
        SET id_uuid = gen_random_uuid()
        WHERE id_uuid IS NULL;
    """)

    schema_editor.execute("""
        ALTER TABLE attendance_attendance
        DROP CONSTRAINT attendance_attendance_pkey;
    """)

    schema_editor.execute("""
        ALTER TABLE attendance_attendance
        DROP COLUMN id;
    """)

    schema_editor.execute("""
        ALTER TABLE attendance_attendance
        RENAME COLUMN id_uuid TO id;
    """)

    schema_editor.execute("""
        ALTER TABLE attendance_attendance
        ADD PRIMARY KEY (id);
    """)

    schema_editor.execute("""
        ALTER TABLE attendance_attendance
        ADD COLUMN created_by_id uuid;
    """)

    schema_editor.execute("""
        ALTER TABLE attendance_attendance
        ADD COLUMN updated_by_id uuid;
    """)

    schema_editor.execute("""
        ALTER TABLE attendance_attendance
        ADD CONSTRAINT attendance_attendance_created_by_id_fk
        FOREIGN KEY (created_by_id)
        REFERENCES accounts_user (id)
        ON DELETE SET NULL
        DEFERRABLE INITIALLY DEFERRED;
    """)

    schema_editor.execute("""
        ALTER TABLE attendance_attendance
        ADD CONSTRAINT attendance_attendance_updated_by_id_fk
        FOREIGN KEY (updated_by_id)
        REFERENCES accounts_user (id)
        ON DELETE SET NULL
        DEFERRABLE INITIALLY DEFERRED;
    """)


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0003_user_uuid_conversion"),
        ("employees", "0006_employee_uuid_conversion"),
        ("attendance", "0003_alter_attendance_options_and_more"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunPython(
                    migrate_attendance_to_uuid,
                    reverse_code=migrations.RunPython.noop,
                ),
            ],
            state_operations=[
                migrations.AlterField(
                    model_name="attendance",
                    name="id",
                    field=models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                migrations.AddField(
                    model_name="attendance",
                    name="created_by",
                    field=models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=models.SET_NULL,
                        related_name="attendances_created",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                migrations.AddField(
                    model_name="attendance",
                    name="updated_by",
                    field=models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=models.SET_NULL,
                        related_name="attendances_updated",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]