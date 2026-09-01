
from django.db import migrations, models
import django.db.models.deletion


def create_departments_from_existing_employees(apps, schema_editor):
    """
    Create Department records for all existing department names.
    """

    Employee = apps.get_model(
        "employees",
        "Employee"
    )

    Department = apps.get_model(
        "departments",
        "Department"
    )

    existing_department_names = set()

    for employee in Employee.objects.all():

        department_name = employee.department

        if not department_name:
            continue

        department_name = department_name.strip()

        if not department_name:
            continue

        existing_department_names.add(
            department_name
        )

    for department_name in existing_department_names:

        Department.objects.get_or_create(
            name=department_name
        )


def convert_department_names_to_ids(apps, schema_editor):
    """
    Convert the old text department values into
    Department primary-key values.
    """

    Employee = apps.get_model(
        "employees",
        "Employee"
    )

    Department = apps.get_model(
        "departments",
        "Department"
    )

    for employee in Employee.objects.all():

        department_name = employee.department

        if not department_name:
            continue

        department_name = department_name.strip()

        department = Department.objects.get(
            name=department_name
        )

        employee.department = str(
            department.pk
        )

        employee.save(
            update_fields=["department"]
        )


class Migration(migrations.Migration):

    dependencies = [

        (
            "departments",
            "0001_initial"
        ),

        (
            "employees",
            "0002_alter_employee_phone_alter_employee_status"
        ),

    ]

    operations = [

        # ======================================================
        # STEP 1
        # Create Department records
        # ======================================================

        migrations.RunPython(
            create_departments_from_existing_employees,
            migrations.RunPython.noop
        ),

        # ======================================================
        # STEP 2
        # Convert ECE / CSE / HR etc. into Department IDs
        # ======================================================

        migrations.RunPython(
            convert_department_names_to_ids,
            migrations.RunPython.noop
        ),

        # ======================================================
        # STEP 3
        # Convert the field into ForeignKey
        # ======================================================

        migrations.AlterField(
            model_name="employee",
            name="department",

            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="employees",
                to="departments.department",
            ),
        ),
    ]

