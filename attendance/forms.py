from datetime import timedelta

from django import forms
from django.utils import timezone

from employees.models import Employee

from .models import Attendance


class AttendanceForm(forms.ModelForm):

    class Meta:
        model = Attendance

        fields = [
            "employee",
            "date",
            "check_in",
            "check_out",
            "status",
            "remarks",
        ]

        widgets = {
            "employee": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                    "readonly": "readonly",
                }
            ),

            "check_in": forms.TimeInput(
                attrs={
                    "class": "form-control",
                    "type": "time",
                    "readonly": "readonly",
                }
            ),

            "check_out": forms.TimeInput(
                attrs={
                    "class": "form-control",
                    "type": "time",
                    "readonly": "readonly",
                }
            ),

            "status": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "remarks": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3
                }
            ),
        }

    def __init__(
        self,
        *args,
        current_user=None,
        **kwargs
    ):

        super().__init__(*args, **kwargs)

        self.current_user = current_user

        now = timezone.localtime()

        # =====================================================
        # ROLE
        # =====================================================

        role = getattr(
            current_user,
            "role",
            None
        )

        role_name = getattr(
            role,
            "name",
            None
        )

        # =====================================================
        # EMPLOYEE DROPDOWN
        # =====================================================

        if (
            current_user
            and role_name == "Employee"
        ):

            linked_employee = getattr(
                current_user,
                "employee_profile",
                None
            )

            if linked_employee:

                # Employee users can only see themselves.
                self.fields["employee"].queryset = (
                    Employee.objects
                    .filter(
                        pk=linked_employee.pk,
                        is_active=True
                    )
                    .select_related(
                        "department",
                        "user"
                    )
                )

                # Automatically select the logged-in employee.
                self.initial["employee"] = linked_employee

                # Employee cannot change the employee.
                self.fields["employee"].disabled = True

            else:

                self.fields["employee"].queryset = (
                    Employee.objects.none()
                )

        else:

            # Admin / HR can select any active employee.
            self.fields["employee"].queryset = (
                Employee.objects
                .filter(is_active=True)
                .select_related(
                    "department",
                    "user"
                )
                .order_by("employee_id")
            )

        # =====================================================
        # DATE
        # =====================================================

        # Attendance date is always controlled by the server.
        self.initial["date"] = now.date()

        self.fields["date"].disabled = True

        # =====================================================
        # SERVER-CONTROLLED TIMES
        # =====================================================

        if not self.instance.pk:

            current_time = now.time().replace(
                second=0,
                microsecond=0
            )

            self.initial["check_in"] = current_time

            # Display earliest Present checkout time.
            minimum_checkout = (
                now + timedelta(hours=7)
            )

            self.initial["check_out"] = (
                minimum_checkout.time().replace(
                    second=0,
                    microsecond=0
                )
            )

        # Check-in and check-out are controlled by the server.
        self.fields["check_in"].disabled = True
        self.fields["check_out"].disabled = True

    # ==========================================================
    # DATE VALIDATION
    # ==========================================================

    def clean_date(self):

        # Server is authoritative for attendance date.
        return timezone.localdate()

    # ==========================================================
    # EMPLOYEE VALIDATION
    # ==========================================================

    def clean_employee(self):

        employee = self.cleaned_data.get(
            "employee"
        )

        if employee is None:

            raise forms.ValidationError(
                "Employee is required."
            )

        if not employee.is_active:

            raise forms.ValidationError(
                "Inactive employees cannot mark attendance."
            )

        # =====================================================
        # EMPLOYEE OWNERSHIP VALIDATION
        # =====================================================

        role = getattr(
            self.current_user,
            "role",
            None
        )

        role_name = getattr(
            role,
            "name",
            None
        )

        if role_name == "Employee":

            linked_employee = getattr(
                self.current_user,
                "employee_profile",
                None
            )

            if linked_employee is None:

                raise forms.ValidationError(
                    "Your employee profile has not been created yet."
                )

            if employee.pk != linked_employee.pk:

                raise forms.ValidationError(
                    "You can only mark attendance for yourself."
                )

        return employee

    # ==========================================================
    # FORM CLEAN
    # ==========================================================

    def clean(self):

        cleaned_data = super().clean()

        # =====================================================
        # SERVER-CONTROLLED CHECK-IN
        # =====================================================

        if not self.instance.pk:

            now = timezone.localtime()

            cleaned_data["date"] = now.date()

            cleaned_data["check_in"] = (
                now.time().replace(
                    second=0,
                    microsecond=0
                )
            )

            cleaned_data["check_out"] = None

        return cleaned_data

    # ==========================================================
    # SAVE
    # ==========================================================

    def save(self, commit=True):

        attendance = super().save(
            commit=False
        )

        # =====================================================
        # NEW ATTENDANCE
        # =====================================================

        if not attendance.pk:

            now = timezone.localtime()

            attendance.date = now.date()

            attendance.check_in = (
                now.time().replace(
                    second=0,
                    microsecond=0
                )
            )

            attendance.check_out = None

            attendance.working_hours = 0

        # =====================================================
        # EMPLOYEE USER
        # =====================================================

        role = getattr(
            self.current_user,
            "role",
            None
        )

        role_name = getattr(
            role,
            "name",
            None
        )

        if role_name == "Employee":

            linked_employee = getattr(
                self.current_user,
                "employee_profile",
                None
            )

            if linked_employee:

                attendance.employee = linked_employee

        # =====================================================
        # AUDIT USER
        # =====================================================

        if self.current_user:

            if not attendance.pk:
                attendance.created_by = self.current_user

            attendance.updated_by = self.current_user

        # =====================================================
        # SAVE
        # =====================================================

        if commit:

            attendance.save()

        return attendance