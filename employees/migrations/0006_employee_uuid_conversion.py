import uuid

from django.conf import settings
from django.core.validators import RegexValidator
from django.db import migrations, models


def migrate_employees_to_uuid(apps, schema_editor):
    schema_editor.execute("""
        ALTER TABLE employees_employee
        ADD COLUMN id_uuid uuid;
    """)

    schema_editor.execute("""
        UPDATE employees_employee
        SET id_uuid = gen_random_uuid()
        WHERE id_uuid IS NULL;
    """)

    schema_editor.execute("""
        ALTER TABLE attendance_attendance
        ADD COLUMN employee_id_uuid uuid;
    """)

    schema_editor.execute("""
        UPDATE attendance_attendance a
        SET employee_id_uuid = e.id_uuid
        FROM employees_employee e
        WHERE a.employee_id = e.id;
    """)

    schema_editor.execute("""
        ALTER TABLE leave_management_leave
        ADD COLUMN employee_id_uuid uuid;
    """)

    schema_editor.execute("""
        UPDATE leave_management_leave l
        SET employee_id_uuid = e.id_uuid
        FROM employees_employee e
        WHERE l.employee_id = e.id;
    """)

    schema_editor.execute("""
        ALTER TABLE payroll_payroll
        ADD COLUMN employee_id_uuid uuid;
    """)

    schema_editor.execute("""
        UPDATE payroll_payroll p
        SET employee_id_uuid = e.id_uuid
        FROM employees_employee e
        WHERE p.employee_id = e.id;
    """)

    schema_editor.execute("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM attendance_attendance
                WHERE employee_id IS NOT NULL
                  AND employee_id_uuid IS NULL
            ) THEN
                RAISE EXCEPTION
                    'Unmapped attendance employee FK found during UUID conversion';
            END IF;

            IF EXISTS (
                SELECT 1
                FROM leave_management_leave
                WHERE employee_id IS NOT NULL
                  AND employee_id_uuid IS NULL
            ) THEN
                RAISE EXCEPTION
                    'Unmapped leave employee FK found during UUID conversion';
            END IF;

            IF EXISTS (
                SELECT 1
                FROM payroll_payroll
                WHERE employee_id IS NOT NULL
                  AND employee_id_uuid IS NULL
            ) THEN
                RAISE EXCEPTION
                    'Unmapped payroll employee FK found during UUID conversion';
            END IF;
        END $$;
    """)

    # Remove old foreign-key constraints.
    schema_editor.execute("""
        ALTER TABLE attendance_attendance
        DROP CONSTRAINT IF EXISTS
        attendance_attendanc_employee_id_63b4db5a_fk_employees;
    """)

    schema_editor.execute("""
        ALTER TABLE leave_management_leave
        DROP CONSTRAINT IF EXISTS
        leave_management_lea_employee_id_703574c2_fk_employees;
    """)

    schema_editor.execute("""
        ALTER TABLE payroll_payroll
        DROP CONSTRAINT IF EXISTS
        payroll_payroll_employee_id_cd24ccf6_fk_employees_employee_id;
    """)

    # Remove old BIGINT FK columns.
    schema_editor.execute("""
        ALTER TABLE attendance_attendance
        DROP COLUMN employee_id;
    """)

    schema_editor.execute("""
        ALTER TABLE leave_management_leave
        DROP COLUMN employee_id;
    """)

    schema_editor.execute("""
        ALTER TABLE payroll_payroll
        DROP COLUMN employee_id;
    """)

    # Rename the UUID FK columns.
    schema_editor.execute("""
        ALTER TABLE attendance_attendance
        RENAME COLUMN employee_id_uuid TO employee_id;
    """)

    schema_editor.execute("""
        ALTER TABLE leave_management_leave
        RENAME COLUMN employee_id_uuid TO employee_id;
    """)

    schema_editor.execute("""
        ALTER TABLE payroll_payroll
        RENAME COLUMN employee_id_uuid TO employee_id;
    """)

    # Replace Employee's BIGINT primary key with UUID.
    schema_editor.execute("""
        ALTER TABLE employees_employee
        DROP CONSTRAINT employees_employee_pkey;
    """)

    schema_editor.execute("""
        ALTER TABLE employees_employee
        DROP COLUMN id;
    """)

    schema_editor.execute("""
        ALTER TABLE employees_employee
        RENAME COLUMN id_uuid TO id;
    """)

    schema_editor.execute("""
        ALTER TABLE employees_employee
        ADD PRIMARY KEY (id);
    """)

    # Match the current Employee model field sizes.
    schema_editor.execute("""
        ALTER TABLE employees_employee
        ALTER COLUMN employee_id TYPE varchar(50);
    """)

    schema_editor.execute("""
        ALTER TABLE employees_employee
        ALTER COLUMN first_name TYPE varchar(150);
    """)

    schema_editor.execute("""
        ALTER TABLE employees_employee
        ALTER COLUMN last_name TYPE varchar(150);
    """)

    # Add structured address fields.
    schema_editor.execute("""
        ALTER TABLE employees_employee
        ADD COLUMN address_line_1 varchar(255);
    """)

    schema_editor.execute("""
        ALTER TABLE employees_employee
        ADD COLUMN address_line_2 varchar(255);
    """)

    schema_editor.execute("""
        ALTER TABLE employees_employee
        ADD COLUMN city varchar(100);
    """)

    schema_editor.execute("""
        ALTER TABLE employees_employee
        ADD COLUMN state varchar(100);
    """)

    schema_editor.execute("""
        ALTER TABLE employees_employee
        ADD COLUMN country varchar(100);
    """)

    schema_editor.execute("""
        ALTER TABLE employees_employee
        ADD COLUMN pincode varchar(20);
    """)

    # Add audit-user fields.
    schema_editor.execute("""
        ALTER TABLE employees_employee
        ADD COLUMN created_by_id uuid;
    """)

    schema_editor.execute("""
        ALTER TABLE employees_employee
        ADD COLUMN updated_by_id uuid;
    """)

    # Recreate the Employee -> User uniqueness required by OneToOneField.
    schema_editor.execute("""
        CREATE UNIQUE INDEX employees_employee_user_id_unique
        ON employees_employee (user_id);
    """)

    # Recreate Employee -> User audit FKs.
    schema_editor.execute("""
        ALTER TABLE employees_employee
        ADD CONSTRAINT employees_employee_created_by_id_fk
        FOREIGN KEY (created_by_id)
        REFERENCES accounts_user (id)
        DEFERRABLE INITIALLY DEFERRED;
    """)

    schema_editor.execute("""
        ALTER TABLE employees_employee
        ADD CONSTRAINT employees_employee_updated_by_id_fk
        FOREIGN KEY (updated_by_id)
        REFERENCES accounts_user (id)
        DEFERRABLE INITIALLY DEFERRED;
    """)

    # Recreate Employee FKs from dependent applications.
    schema_editor.execute("""
        ALTER TABLE attendance_attendance
        ADD CONSTRAINT attendance_attendance_employee_id_fk
        FOREIGN KEY (employee_id)
        REFERENCES employees_employee (id)
        ON DELETE CASCADE
        DEFERRABLE INITIALLY DEFERRED;
    """)

    schema_editor.execute("""
        ALTER TABLE leave_management_leave
        ADD CONSTRAINT leave_management_leave_employee_id_fk
        FOREIGN KEY (employee_id)
        REFERENCES employees_employee (id)
        ON DELETE CASCADE
        DEFERRABLE INITIALLY DEFERRED;
    """)

    schema_editor.execute("""
        ALTER TABLE payroll_payroll
        ADD CONSTRAINT payroll_payroll_employee_id_fk
        FOREIGN KEY (employee_id)
        REFERENCES employees_employee (id)
        ON DELETE CASCADE
        DEFERRABLE INITIALLY DEFERRED;
    """)


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0003_user_uuid_conversion"),
        ("departments", "0002_department_is_active"),
        ("employees", "0005_employee_user"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunPython(
                    migrate_employees_to_uuid,
                    reverse_code=migrations.RunPython.noop,
                ),
            ],
            state_operations=[
                migrations.AlterField(
                    model_name="employee",
                    name="id",
                    field=models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                migrations.AlterField(
                    model_name="employee",
                    name="employee_id",
                    field=models.CharField(
                        max_length=50,
                        unique=True,
                    ),
                ),
                migrations.AlterField(
                    model_name="employee",
                    name="first_name",
                    field=models.CharField(max_length=150),
                ),
                migrations.AlterField(
                    model_name="employee",
                    name="last_name",
                    field=models.CharField(max_length=150),
                ),
                migrations.AlterField(
                    model_name="employee",
                    name="phone",
                    field=models.CharField(
                        max_length=15,
                        validators=[
                            RegexValidator(
                                regex=r"^\d+$",
                                message=(
                                    "Phone number must contain only "
                                    "numerical digits."
                                ),
                            )
                        ],
                    ),
                ),
                migrations.AddField(
                    model_name="employee",
                    name="address_line_1",
                    field=models.CharField(
                        max_length=255,
                        blank=True,
                        null=True,
                    ),
                ),
                migrations.AddField(
                    model_name="employee",
                    name="address_line_2",
                    field=models.CharField(
                        max_length=255,
                        blank=True,
                        null=True,
                    ),
                ),
                migrations.AddField(
                    model_name="employee",
                    name="city",
                    field=models.CharField(
                        max_length=100,
                        blank=True,
                        null=True,
                    ),
                ),
                migrations.AddField(
                    model_name="employee",
                    name="state",
                    field=models.CharField(
                        max_length=100,
                        blank=True,
                        null=True,
                    ),
                ),
                migrations.AddField(
                    model_name="employee",
                    name="country",
                    field=models.CharField(
                        max_length=100,
                        blank=True,
                        null=True,
                    ),
                ),
                migrations.AddField(
                    model_name="employee",
                    name="pincode",
                    field=models.CharField(
                        max_length=20,
                        blank=True,
                        null=True,
                    ),
                ),
                migrations.AddField(
                    model_name="employee",
                    name="created_by",
                    field=models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=models.SET_NULL,
                        related_name="employees_created",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                migrations.AddField(
                    model_name="employee",
                    name="updated_by",
                    field=models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=models.SET_NULL,
                        related_name="employees_updated",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                migrations.AlterField(
                    model_name="employee",
                    name="department",
                    field=models.ForeignKey(
                        on_delete=models.PROTECT,
                        related_name="employees",
                        to="departments.department",
                    ),
                ),
                migrations.AlterField(
                    model_name="employee",
                    name="user",
                    field=models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=models.SET_NULL,
                        related_name="employee_profile",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]