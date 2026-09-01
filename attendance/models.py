from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models


class Attendance(models.Model):

    # ==========================================================
    # STATUS CHOICES
    # ==========================================================

    STATUS_CHOICES = [
        ("Present", "Present"),
        ("Half Day", "Half Day"),
        ("Leave", "Leave"),
    ]

    # ==========================================================
    # EMPLOYEE
    # ==========================================================

    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.CASCADE,
        related_name="attendances"
    )

    # ==========================================================
    # DATE
    # ==========================================================

    date = models.DateField()

    # ==========================================================
    # CHECK IN
    # ==========================================================

    check_in = models.TimeField(
        null=True,
        blank=True
    )

    # ==========================================================
    # CHECK OUT
    # IMPORTANT:
    # check_out MUST be nullable because an employee
    # can check in before checking out.
    # ==========================================================

    check_out = models.TimeField(
        null=True,
        blank=True
    )

    # ==========================================================
    # STATUS
    # ==========================================================

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Present"
    )

    # ==========================================================
    # WORKING HOURS
    # ==========================================================

    working_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00")
    )

    # ==========================================================
    # REMARKS
    # ==========================================================

    remarks = models.TextField(
        blank=True,
        null=True
    )

    # ==========================================================
    # CREATED / UPDATED
    # ==========================================================

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    # ==========================================================
    # MODEL VALIDATION
    # ==========================================================

    def clean(self):

        # ------------------------------------------------------
        # If checkout exists, check-in must exist
        # ------------------------------------------------------

        if self.check_out and not self.check_in:

            raise ValidationError({
                "check_out":
                "Check-In time is required before Check-Out."
            })

        # ------------------------------------------------------
        # If both times exist, checkout must be later
        # ------------------------------------------------------

        if self.check_in and self.check_out:

            if self.check_out <= self.check_in:

                raise ValidationError({
                    "check_out":
                    "Check-Out time must be later than Check-In time."
                })

        # ------------------------------------------------------
        # Validate working hours only when checkout exists
        # ------------------------------------------------------

        if self.check_in and self.check_out:

            from datetime import datetime

            check_in_datetime = datetime.combine(
                self.date,
                self.check_in
            )

            check_out_datetime = datetime.combine(
                self.date,
                self.check_out
            )

            duration = (
                check_out_datetime - check_in_datetime
            )

            total_hours = (
                duration.total_seconds() / 3600
            )

            # --------------------------------------------------
            # PRESENT
            # --------------------------------------------------

            if self.status == "Present":

                if total_hours <= 7:

                    raise ValidationError({
                        "working_hours":
                        "For Present status, total working hours "
                        "must be more than 7 hours."
                    })

            # --------------------------------------------------
            # HALF DAY
            # --------------------------------------------------

            elif self.status == "Half Day":

                if total_hours <= 3:

                    raise ValidationError({
                        "working_hours":
                        "For Half Day status, total working hours "
                        "must be more than 3 hours."
                    })

    # ==========================================================
    # SAVE
    # ==========================================================

    def save(self, *args, **kwargs):

        # ------------------------------------------------------
        # DO NOT call full_clean() here.
        #
        # Check-in intentionally saves without checkout.
        # Validation is handled by:
        #
        # 1. AttendanceForm for Add/Edit
        # 2. check_in() / check_out() views for button actions
        # ------------------------------------------------------

        if self.working_hours is None:

            self.working_hours = Decimal("0.00")

        else:

            self.working_hours = Decimal(
                str(self.working_hours)
            ).quantize(
                Decimal("0.01")
            )

        super().save(*args, **kwargs)

    # ==========================================================
    # STRING REPRESENTATION
    # ==========================================================

    def __str__(self):

        return (
            f"{self.employee} - "
            f"{self.date} - "
            f"{self.status}"
        )

    # ==========================================================
    # META
    # ==========================================================

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