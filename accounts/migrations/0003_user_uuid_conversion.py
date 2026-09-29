import uuid

from django.db import migrations, models


def migrate_users_to_uuid(apps, schema_editor):
    """
    Convert accounts_user.id from bigint to UUID while preserving
    existing users and all known foreign-key relationships.
    """

    connection = schema_editor.connection

    with connection.cursor() as cursor:

        # ---------------------------------------------------------
        # 1. Create temporary UUID for every existing User
        # ---------------------------------------------------------

        cursor.execute("""
            ALTER TABLE accounts_user
            ADD COLUMN id_uuid uuid;
        """)

        cursor.execute("""
            UPDATE accounts_user
            SET id_uuid = gen_random_uuid()
            WHERE id_uuid IS NULL;
        """)

        cursor.execute("""
            ALTER TABLE accounts_user
            ALTER COLUMN id_uuid SET NOT NULL;
        """)

        # ---------------------------------------------------------
        # 2. Convert old text role into Role UUID
        # ---------------------------------------------------------

        cursor.execute("""
            ALTER TABLE accounts_user
            ADD COLUMN role_uuid uuid;
        """)

        cursor.execute("""
            UPDATE accounts_user u
            SET role_uuid = r.id
            FROM accounts_role r
            WHERE
                (u.role = 'ADMIN' AND r.level = 'ADMIN')
                OR
                (u.role = 'HR' AND r.level = 'HR')
                OR
                (u.role = 'EMPLOYEE' AND r.level = 'EMPLOYEE');
        """)

        # ---------------------------------------------------------
        # 3. Add new User fields
        # ---------------------------------------------------------

        cursor.execute("""
            ALTER TABLE accounts_user
            ADD COLUMN company varchar(255) NULL,
            ADD COLUMN department varchar(255) NULL,
            ADD COLUMN phone_number varchar(15) NULL,
            ADD COLUMN employee_id varchar(50) NULL,
            ADD COLUMN bio text NULL,
            ADD COLUMN is_email_verified boolean NOT NULL DEFAULT FALSE,
            ADD COLUMN updated_at timestamp with time zone NOT NULL DEFAULT NOW();
        """)

        # Preserve the existing phone values.
        cursor.execute("""
            UPDATE accounts_user
            SET phone_number = NULLIF(phone, '');
        """)

        # ---------------------------------------------------------
        # 4. Prepare UUID FK columns
        # ---------------------------------------------------------

        cursor.execute("""
            ALTER TABLE accounts_user_groups
            ADD COLUMN user_id_uuid uuid;
        """)

        cursor.execute("""
            UPDATE accounts_user_groups g
            SET user_id_uuid = u.id_uuid
            FROM accounts_user u
            WHERE g.user_id = u.id;
        """)

        cursor.execute("""
            ALTER TABLE accounts_user_user_permissions
            ADD COLUMN user_id_uuid uuid;
        """)

        cursor.execute("""
            UPDATE accounts_user_user_permissions p
            SET user_id_uuid = u.id_uuid
            FROM accounts_user u
            WHERE p.user_id = u.id;
        """)

        cursor.execute("""
            ALTER TABLE django_admin_log
            ADD COLUMN user_id_uuid uuid;
        """)

        cursor.execute("""
            UPDATE django_admin_log l
            SET user_id_uuid = u.id_uuid
            FROM accounts_user u
            WHERE l.user_id = u.id;
        """)

        cursor.execute("""
            ALTER TABLE employees_employee
            ADD COLUMN user_id_uuid uuid;
        """)

        cursor.execute("""
            UPDATE employees_employee e
            SET user_id_uuid = u.id_uuid
            FROM accounts_user u
            WHERE e.user_id = u.id;
        """)

        cursor.execute("""
            ALTER TABLE accounts_emailverification
            ADD COLUMN user_id_uuid uuid;
        """)

        cursor.execute("""
            UPDATE accounts_emailverification ev
            SET user_id_uuid = u.id_uuid
            FROM accounts_user u
            WHERE ev.user_id = u.id;
        """)

        # ---------------------------------------------------------
        # 5. Verify every existing FK was successfully mapped
        # ---------------------------------------------------------

        cursor.execute("""
            SELECT COUNT(*)
            FROM accounts_user_groups
            WHERE user_id_uuid IS NULL;
        """)
        if cursor.fetchone()[0] != 0:
            raise RuntimeError(
                "User UUID conversion failed: unmapped accounts_user_groups rows."
            )

        cursor.execute("""
            SELECT COUNT(*)
            FROM accounts_user_user_permissions
            WHERE user_id_uuid IS NULL;
        """)
        if cursor.fetchone()[0] != 0:
            raise RuntimeError(
                "User UUID conversion failed: unmapped user permission rows."
            )

        cursor.execute("""
            SELECT COUNT(*)
            FROM django_admin_log
            WHERE user_id IS NOT NULL
              AND user_id_uuid IS NULL;
        """)
        if cursor.fetchone()[0] != 0:
            raise RuntimeError(
                "User UUID conversion failed: unmapped admin log rows."
            )

        cursor.execute("""
            SELECT COUNT(*)
            FROM employees_employee
            WHERE user_id IS NOT NULL
              AND user_id_uuid IS NULL;
        """)
        if cursor.fetchone()[0] != 0:
            raise RuntimeError(
                "User UUID conversion failed: unmapped employee-user rows."
            )

        cursor.execute("""
            SELECT COUNT(*)
            FROM accounts_emailverification
            WHERE user_id_uuid IS NULL;
        """)
        if cursor.fetchone()[0] != 0:
            raise RuntimeError(
                "User UUID conversion failed: unmapped email verification rows."
            )

        # ---------------------------------------------------------
        # 6. Remove old FK constraints
        # ---------------------------------------------------------

        cursor.execute("""
            ALTER TABLE accounts_user_groups
            DROP CONSTRAINT
            accounts_user_groups_user_id_52b62117_fk_accounts_user_id;
        """)

        cursor.execute("""
            ALTER TABLE accounts_user_user_permissions
            DROP CONSTRAINT
            accounts_user_user_p_user_id_e4f0a161_fk_accounts_;
        """)

        cursor.execute("""
            ALTER TABLE django_admin_log
            DROP CONSTRAINT
            django_admin_log_user_id_c564eba6_fk_accounts_user_id;
        """)

        cursor.execute("""
            ALTER TABLE employees_employee
            DROP CONSTRAINT
            employees_employee_user_id_27bed289_fk_accounts_user_id;
        """)

        cursor.execute("""
            ALTER TABLE accounts_emailverification
            DROP CONSTRAINT
            accounts_emailverification_user_id_4f5b1661_fk_accounts_user_id;
        """)

        # ---------------------------------------------------------
        # 7. Replace old FK columns
        # ---------------------------------------------------------

        cursor.execute("""
            ALTER TABLE accounts_user_groups
            DROP COLUMN user_id;
        """)

        cursor.execute("""
            ALTER TABLE accounts_user_groups
            RENAME COLUMN user_id_uuid TO user_id;
        """)

        cursor.execute("""
            ALTER TABLE accounts_user_user_permissions
            DROP COLUMN user_id;
        """)

        cursor.execute("""
            ALTER TABLE accounts_user_user_permissions
            RENAME COLUMN user_id_uuid TO user_id;
        """)

        cursor.execute("""
            ALTER TABLE django_admin_log
            DROP COLUMN user_id;
        """)

        cursor.execute("""
            ALTER TABLE django_admin_log
            RENAME COLUMN user_id_uuid TO user_id;
        """)

        cursor.execute("""
            ALTER TABLE employees_employee
            DROP COLUMN user_id;
        """)

        cursor.execute("""
            ALTER TABLE employees_employee
            RENAME COLUMN user_id_uuid TO user_id;
        """)

        cursor.execute("""
            ALTER TABLE accounts_emailverification
            DROP COLUMN user_id;
        """)

        cursor.execute("""
            ALTER TABLE accounts_emailverification
            RENAME COLUMN user_id_uuid TO user_id;
        """)

        # ---------------------------------------------------------
        # 8. Replace accounts_user primary key
        # ---------------------------------------------------------

        cursor.execute("""
            ALTER TABLE accounts_user
            DROP CONSTRAINT accounts_user_pkey;
        """)

        cursor.execute("""
            ALTER TABLE accounts_user
            DROP COLUMN id;
        """)

        cursor.execute("""
            ALTER TABLE accounts_user
            RENAME COLUMN id_uuid TO id;
        """)

        cursor.execute("""
            ALTER TABLE accounts_user
            ADD CONSTRAINT accounts_user_pkey
            PRIMARY KEY (id);
        """)

        # ---------------------------------------------------------
        # 9. Replace old role text with Role UUID
        # ---------------------------------------------------------

        cursor.execute("""
            ALTER TABLE accounts_user
            DROP COLUMN role;
        """)

        cursor.execute("""
            ALTER TABLE accounts_user
            RENAME COLUMN role_uuid TO role_id;
        """)

        # ---------------------------------------------------------
        # 10. Restore FK constraints
        # ---------------------------------------------------------

        cursor.execute("""
            ALTER TABLE accounts_user_groups
            ALTER COLUMN user_id SET NOT NULL;
        """)

        cursor.execute("""
            ALTER TABLE accounts_user_groups
            ADD CONSTRAINT accounts_user_groups_user_id_fk
            FOREIGN KEY (user_id)
            REFERENCES accounts_user(id)
            ON DELETE CASCADE
            DEFERRABLE INITIALLY DEFERRED;
        """)

        cursor.execute("""
            ALTER TABLE accounts_user_user_permissions
            ALTER COLUMN user_id SET NOT NULL;
        """)

        cursor.execute("""
            ALTER TABLE accounts_user_user_permissions
            ADD CONSTRAINT accounts_user_user_permissions_user_id_fk
            FOREIGN KEY (user_id)
            REFERENCES accounts_user(id)
            ON DELETE CASCADE
            DEFERRABLE INITIALLY DEFERRED;
        """)

        cursor.execute("""
            ALTER TABLE django_admin_log
            ADD CONSTRAINT django_admin_log_user_id_fk
            FOREIGN KEY (user_id)
            REFERENCES accounts_user(id)
            ON DELETE SET NULL
            DEFERRABLE INITIALLY DEFERRED;
        """)

        cursor.execute("""
            ALTER TABLE employees_employee
            ADD CONSTRAINT employees_employee_user_id_fk
            FOREIGN KEY (user_id)
            REFERENCES accounts_user(id)
            ON DELETE SET NULL
            DEFERRABLE INITIALLY DEFERRED;
        """)

        cursor.execute("""
            ALTER TABLE accounts_emailverification
            ADD CONSTRAINT accounts_emailverification_user_id_fk
            FOREIGN KEY (user_id)
            REFERENCES accounts_user(id)
            ON DELETE CASCADE
            DEFERRABLE INITIALLY DEFERRED;
        """)

        cursor.execute("""
            ALTER TABLE accounts_user
            ADD CONSTRAINT accounts_user_role_id_fk
            FOREIGN KEY (role_id)
            REFERENCES accounts_role(id)
            ON DELETE RESTRICT
            DEFERRABLE INITIALLY DEFERRED;
        """)

        # ---------------------------------------------------------
        # 11. Make email unique
        # ---------------------------------------------------------

        cursor.execute("""
            CREATE UNIQUE INDEX accounts_user_email_unique_uuid_migration
            ON accounts_user(email);
        """)


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0002_uuid_core_migration"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunPython(
                    migrate_users_to_uuid,
                    migrations.RunPython.noop,
                ),
            ],
            state_operations=[
                migrations.AlterField(
                    model_name="user",
                    name="id",
                    field=models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                migrations.AlterField(
                    model_name="user",
                    name="email",
                    field=models.EmailField(
                        max_length=254,
                        unique=True,
                    ),
                ),
                migrations.AddField(
                    model_name="user",
                    name="company",
                    field=models.CharField(
                        max_length=255,
                        blank=True,
                        null=True,
                    ),
                ),
                migrations.AddField(
                    model_name="user",
                    name="department",
                    field=models.CharField(
                        max_length=255,
                        blank=True,
                        null=True,
                    ),
                ),
                migrations.AddField(
                    model_name="user",
                    name="phone_number",
                    field=models.CharField(
                        max_length=15,
                        blank=True,
                        null=True,
                    ),
                ),
                migrations.AddField(
                    model_name="user",
                    name="employee_id",
                    field=models.CharField(
                        max_length=50,
                        blank=True,
                        null=True,
                    ),
                ),
                migrations.AddField(
                    model_name="user",
                    name="bio",
                    field=models.TextField(
                        blank=True,
                        null=True,
                    ),
                ),
                migrations.AlterField(
                    model_name="user",
                    name="role",
                    field=models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=models.PROTECT,
                        related_name="users",
                        to="accounts.role",
                    ),
                ),
                migrations.AddField(
                    model_name="user",
                    name="is_email_verified",
                    field=models.BooleanField(
                        default=False,
                    ),
                ),
                migrations.AddField(
                    model_name="user",
                    name="updated_at",
                    field=models.DateTimeField(
                        auto_now=True,
                    ),
                ),
                migrations.RemoveField(
                    model_name="user",
                    name="phone",
                ),
                migrations.RemoveField(
                    model_name="user",
                    name="profile_picture",
                ),
            ],
        ),
    ]