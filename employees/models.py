import uuid

from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models

from departments.models import Department


class Employee(models.Model):

    GENDER_CHOICES = (
        ("Male", "Male"),
        ("Female", "Female"),
        ("Other", "Other"),
    )

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    # Existing relationship with the registered user account.
    # Kept during the migration so existing user/employee links
    # are preserved.
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employee_profile",
    )

    employee_id = models.CharField(
        max_length=50,
        unique=True
    )

    first_name = models.CharField(
        max_length=150
    )

    last_name = models.CharField(
        max_length=150
    )

    email = models.EmailField(
        unique=True
    )

    phone = models.CharField(
        max_length=15,
        validators=[
            RegexValidator(
                regex=r"^\d+$",
                message="Phone number must contain only numerical digits."
            )
        ]
    )

    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES
    )

    date_of_birth = models.DateField()

    designation = models.CharField(
        max_length=100
    )

    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name="employees"
    )

    joining_date = models.DateField()

    is_active = models.BooleanField(
        default=True
    )

    profile_picture = models.ImageField(
        upload_to="employees/",
        blank=True,
        null=True
    )

    # ----------------------------------------------------------
    # New target address fields
    # ----------------------------------------------------------

    address_line_1 = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    address_line_2 = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    city = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    state = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    country = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    pincode = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    # ----------------------------------------------------------
    # Legacy fields
    #
    # These are intentionally kept for now so existing data is
    # not removed before we perform the controlled migration.
    # They can be removed after the migration/data-copy step.
    # ----------------------------------------------------------

    salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )

    address = models.TextField(
        blank=True,
        null=True
    )

    # ----------------------------------------------------------
    # Audit fields
    # ----------------------------------------------------------

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employees_created",
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employees_updated",
    )

    class Meta:
        ordering = ["employee_id"]

    def __str__(self):
        return (
            f"{self.employee_id} - "
            f"{self.first_name} {self.last_name}"
        )