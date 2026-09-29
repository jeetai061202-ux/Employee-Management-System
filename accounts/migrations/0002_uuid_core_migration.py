import uuid

from django.db import migrations, models


def create_roles(apps, schema_editor):
    Role = apps.get_model("accounts", "Role")

    roles = [
        {
            "name": "Admin",
            "description": "System administrator",
            "level": "ADMIN",
        },
        {
            "name": "HR",
            "description": "Human resources",
            "level": "HR",
        },
        {
            "name": "Employee",
            "description": "Regular employee",
            "level": "EMPLOYEE",
        },
    ]

    for role_data in roles:
        Role.objects.create(
            id=uuid.uuid4(),
            **role_data,
        )


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
        ("employees", "0005_employee_user"),
        ("departments", "0002_department_is_active"),
        ("attendance", "0003_alter_attendance_options_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="Role",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        max_length=100,
                        unique=True,
                    ),
                ),
                (
                    "description",
                    models.CharField(
                        max_length=255,
                        blank=True,
                    ),
                ),
                (
                    "level",
                    models.CharField(
                        max_length=50,
                        blank=True,
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True,
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="EmailVerification",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "secret_key",
                    models.CharField(
                        max_length=255,
                    ),
                ),
                (
                    "is_used",
                    models.BooleanField(
                        default=False,
                    ),
                ),
                (
                    "attempts",
                    models.PositiveSmallIntegerField(
                        default=0,
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True,
                    ),
                ),
                (
                    "expires_at",
                    models.DateTimeField(),
                    ),
                (
                    "verified_at",
                    models.DateTimeField(
                        null=True,
                        blank=True,
                    ),
                ),
                (
                    "last_sent_at",
                    models.DateTimeField(
                        null=True,
                        blank=True,
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=models.CASCADE,
                        related_name="email_verifications",
                        to="accounts.user",
                    ),
                ),
            ],
        ),
        migrations.RunPython(
            create_roles,
            migrations.RunPython.noop,
        ),
    ]