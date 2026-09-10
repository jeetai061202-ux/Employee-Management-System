from datetime import datetime, timedelta
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models


class Attendance(models.Model):

    STATUS_CHOICES = [
        ("Present", "Present"),
        ("Half Day", "Half Day"),
    ]

    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.CASCADE,
        related_name="attendances"
    )

    date = models.DateField()

    check_in = models.TimeField(
        null=True,
        blank=True
    )

    check_out = models.TimeField(
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Present"
    )

    working_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00")
    )

    remarks = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    @property
    def minimum_working_hours(self):
        """
        Minimum required working hours according to status.
        """
        if self.status == "Present":
            return Decimal("7.00")

        if self.status == "Half Day":
            return Decimal("3.00")

        return Decimal("0.00")

    @property
    def minimum_checkout_datetime(self):
        """
        Calculates the earliest permitted checkout datetime.
        """
        if not self.check_in:
            return None

        hours = self.minimum_working_hours

        check_in_datetime = datetime.combine(
            self.date,
            self.check_in
        )

        return check_in_datetime + timedelta(
            hours=float(hours)
        )

    @property
    def minimum_checkout_time(self):
        """
        Returns the minimum checkout time for display.
        """
        minimum_datetime = self.minimum_checkout_datetime

        if minimum_datetime is None:
            return None

        return minimum_datetime.time()

    def get_checkout_datetime(self):
        """
        Converts checkout time into a datetime.

        If checkout time is earlier than check-in time,
        it is treated as next-day checkout.
        """
        if not self.check_in or not self.check_out:
            return None

        checkout_date = self.date

        if self.check_out < self.check_in:
            checkout_date += timedelta(days=1)

        return datetime.combine(
            checkout_date,
            self.check_out
        )

    def clean(self):

        errors = {}

        # Check-out cannot exist without check-in.
        if self.check_out and not self.check_in:
            errors["check_out"] = (
                "Check-In time is required before Check-Out."
            )

        # Validate employee.
        if not self.employee:
            errors["employee"] = "Employee is required."

        # Validate status.
        if self.status not in ["Present", "Half Day"]:
            errors["status"] = "Invalid attendance status."

        if errors:
            raise ValidationError(errors)

        # Validate working time.
        if self.check_in and self.check_out:

            checkout_datetime = self.get_checkout_datetime()

            checkin_datetime = datetime.combine(
                self.date,
                self.check_in
            )

            duration = checkout_datetime - checkin_datetime

            total_hours = (
                Decimal(str(duration.total_seconds()))
                / Decimal("3600")
            )

            minimum_hours = self.minimum_working_hours

            if total_hours < minimum_hours:
                raise ValidationError({
                    "check_out": (
                        f"{self.status} attendance requires at least "
                        f"{minimum_hours:.0f} hours of working time."
                    )
                })

            # Automatically calculate working hours.
            self.working_hours = (
                total_hours.quantize(Decimal("0.01"))
            )

    def save(self, *args, **kwargs):

        if self.working_hours is None:
            self.working_hours = Decimal("0.00")

        self.working_hours = Decimal(
            str(self.working_hours)
        ).quantize(
            Decimal("0.01")
        )

        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{self.employee} - "
            f"{self.date} - "
            f"{self.status}"
        )

    class Meta:
        ordering = [
            "-date",
            "-created_at"
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "employee",
                    "date"
                ],
                name="unique_employee_attendance_per_day"
            )
        ]