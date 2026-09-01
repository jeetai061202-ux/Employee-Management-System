from datetime import date, datetime

from django import forms

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
                }
            ),

            "check_in": forms.TimeInput(
                attrs={
                    "class": "form-control",
                    "type": "time",
                }
            ),

            "check_out": forms.TimeInput(
                attrs={
                    "class": "form-control",
                    "type": "time",
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
                    "rows": 3,
                }
            ),
        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.initial["date"] = date.today()

        self.fields["date"].disabled = True

    # ==========================================================
    # DATE
    # ==========================================================

    def clean_date(self):

        return date.today()

    # ==========================================================
    # ATTENDANCE VALIDATION
    # ==========================================================

    def clean(self):

        cleaned_data = super().clean()

        check_in = cleaned_data.get("check_in")
        check_out = cleaned_data.get("check_out")
        status = cleaned_data.get("status")

        # ------------------------------------------------------
        # Present / Half Day requires both times
        # ------------------------------------------------------

        if status in ["Present", "Half Day"]:

            if not check_in:

                self.add_error(
                    "check_in",
                    "Check-In time is required."
                )

            if not check_out:

                self.add_error(
                    "check_out",
                    "Check-Out time is required."
                )

            # Stop here if either time is missing

            if not check_in or not check_out:

                return cleaned_data

        # ------------------------------------------------------
        # If one time is missing for other statuses
        # ------------------------------------------------------

        if not check_in or not check_out:

            return cleaned_data

        # ------------------------------------------------------
        # Check-out must be after check-in
        # ------------------------------------------------------

        if check_out <= check_in:

            self.add_error(
                "check_out",
                "Check-Out Time must be later than Check-In Time."
            )

            return cleaned_data

        # ------------------------------------------------------
        # Calculate working hours
        # ------------------------------------------------------

        check_in_datetime = datetime.combine(
            date.today(),
            check_in
        )

        check_out_datetime = datetime.combine(
            date.today(),
            check_out
        )

        working_duration = (
            check_out_datetime - check_in_datetime
        )

        total_seconds = working_duration.total_seconds()

        total_hours = total_seconds / 3600

        # ------------------------------------------------------
        # PRESENT
        # More than 7 hours
        # ------------------------------------------------------

        if status == "Present" and total_hours <= 7:

            self.add_error(
                "check_out",
                "Present attendance requires more than 7 hours "
                "of working time."
            )

        # ------------------------------------------------------
        # HALF DAY
        # More than 3 hours
        # ------------------------------------------------------

        elif status == "Half Day" and total_hours <= 3:

            self.add_error(
                "check_out",
                "Half Day attendance requires more than 3 hours "
                "of working time."
            )

        # ------------------------------------------------------
        # Store working hours
        # ------------------------------------------------------

        if not self.errors:

            cleaned_data["calculated_working_hours"] = round(
                total_hours,
                2
            )

        return cleaned_data

    # ==========================================================
    # SAVE
    # ==========================================================

    def save(self, commit=True):

        attendance = super().save(commit=False)

        working_hours = self.cleaned_data.get(
            "calculated_working_hours"
        )

        if working_hours is not None:

            attendance.working_hours = working_hours

        else:

            attendance.working_hours = 0

        if commit:

            attendance.save()

        return attendance