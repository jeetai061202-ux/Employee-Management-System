import uuid

from django.conf import settings
from django.db import migrations, models


def migrate_departments_to_uuid(apps, schema_editor):
    # 1. Create temporary UUIDs for every existing Department.
    schema_editor.execute("""
        ALTER TABLE departments_department
        ADD COLUMN id_uuid uuid;
    """)

    schema_editor.execute("""
        UPDATE departments_department
        SET id_uuid = gen_random_uuid()
        WHERE id_uuid IS NULL;
    """)

    # 2. Create temporary UUID department references on Employee.
    schema_editor.execute("""
        ALTER TABLE employees_employee
        ADD COLUMN department_id_uuid uuid;
    """)

    schema_editor.execute("""
        UPDATE employees_employee e
        SET department_id_uuid = d.id_uuid
        FROM departments_department d
        WHERE e.department_id = d.id;
    """)

    # 3. Verify every existing Employee department reference was mapped.
    schema_editor.execute("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM employees_employee
                WHERE department_id IS NOT NULL
                  AND department_id_uuid IS NULL
            ) THEN
                RAISE EXCEPTION
                    'Unmapped employee department FK found during UUID conversion';
            END IF;
        END $$;
    """)

    # 4. Remove the old Employee -> Department FK.
    schema_editor.execute("""
        ALTER TABLE employees_employee
        DROP CONSTRAINT IF EXISTS
        employees_employee_department_id_410c23c8_fk_departmen;
    """)

    # 5. Remove the old BIGINT department reference.
    schema_editor.execute("""
        ALTER TABLE employees_employee
        DROP COLUMN department_id;
    """)

    # 6. Rename the temporary UUID department reference.
    schema_editor.execute("""
        ALTER TABLE employees_employee
        RENAME COLUMN department_id_uuid TO department_id;
    """)

    # 7. Replace Department BIGINT PK with UUID PK.
    schema_editor.execute("""
        ALTER TABLE departments_department
        DROP CONSTRAINT departments_department_pkey;
    """)

    schema_editor.execute("""
        ALTER TABLE departments_department
        DROP COLUMN id;
    """)

    schema_editor.execute("""
        ALTER TABLE departments_department
        RENAME COLUMN id_uuid TO id;
    """)

    schema_editor.execute("""
        ALTER TABLE departments_department
        ADD PRIMARY KEY (id);
    """)

    # 8. Add the new Department code field.
    schema_editor.execute("""
        ALTER TABLE departments_department
        ADD COLUMN code varchar(50);
    """)

    # 9. Add Department audit fields.
    schema_editor.execute("""
        ALTER TABLE departments_department
        ADD COLUMN created_by_id uuid;
    """)

    schema_editor.execute("""
        ALTER TABLE departments_department
        ADD COLUMN updated_by_id uuid;
    """)

    # 10. Preserve the unique nature of Department.code.
    # NULL values are allowed to repeat in PostgreSQL.
    schema_editor.execute("""
        CREATE UNIQUE INDEX departments_department_code_unique
        ON departments_department (code);
    """)

    # 11. Recreate Department -> User audit FKs.
    schema_editor.execute("""
        ALTER TABLE departments_department
        ADD CONSTRAINT departments_department_created_by_id_fk
        FOREIGN KEY (created_by_id)
        REFERENCES accounts_user (id)
        ON DELETE SET NULL
        DEFERRABLE INITIALLY DEFERRED;
    """)

    schema_editor.execute("""
        ALTER TABLE departments_department
        ADD CONSTRAINT departments_department_updated_by_id_fk
        FOREIGN KEY (updated_by_id)
        REFERENCES accounts_user (id)
        ON DELETE SET NULL
        DEFERRABLE INITIALLY DEFERRED;
    """)

    # 12. Recreate Employee -> Department FK.
    # Department.PROTECT maps to RESTRICT at the database level.
    schema_editor.execute("""
        ALTER TABLE employees_employee
        ADD CONSTRAINT employees_employee_department_id_fk
        FOREIGN KEY (department_id)
        REFERENCES departments_department (id)
        ON DELETE RESTRICT
        DEFERRABLE INITIALLY DEFERRED;
    """)

    # 13. Recreate the Employee department index.
    schema_editor.execute("""
        CREATE INDEX employees_employee_department_id_idx
        ON employees_employee (department_id);
    """)


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0003_user_uuid_conversion"),
        ("departments", "0002_department_is_active"),
        ("employees", "0006_employee_uuid_conversion"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunPython(
                    migrate_departments_to_uuid,
                    reverse_code=migrations.RunPython.noop,
                ),
            ],
            state_operations=[
                migrations.AlterField(
                    model_name="department",
                    name="id",
                    field=models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                migrations.AddField(
                    model_name="department",
                    name="code",
                    field=models.CharField(
                        max_length=50,
                        unique=True,
                        blank=True,
                        null=True,
                    ),
                ),
                migrations.AddField(
                    model_name="department",
                    name="created_by",
                    field=models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=models.SET_NULL,
                        related_name="departments_created",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                migrations.AddField(
                    model_name="department",
                    name="updated_by",
                    field=models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=models.SET_NULL,
                        related_name="departments_updated",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]