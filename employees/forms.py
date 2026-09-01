from django import forms
from django.core.exceptions import ValidationError
from datetime import date

from .models import Employee


MAX_PROFILE_PICTURE_SIZE = 2 * 1024 * 1024  # 2 MB


class EmployeeForm(forms.ModelForm):

    # ==========================================================
    # ACTIVE / INACTIVE DROPDOWN
    # ==========================================================

    STATUS_CHOICES = (
        ("True", "Active"),
        ("False", "Inactive"),
    )

    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        widget=forms.Select(
            attrs={
                "class": "form-select"
            }
        ),
        label="Status",
    )

    class Meta:

        model = Employee

        fields = [
            "employee_id",
            "first_name",
            "last_name",
            "email",
            "phone",
            "gender",
            "date_of_birth",
            "designation",
            "department",
            "salary",
            "joining_date",
            "status",
            "profile_picture",
            "address",
        ]

        widgets = {

            "employee_id": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "EMP001",
                }
            ),

            "first_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "last_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "phone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "inputmode": "numeric",
                    "pattern": "[0-9]+",
                    "maxlength": "15",
                    "placeholder": "Enter phone number",
                }
            ),

            "gender": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "date_of_birth": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),

            "designation": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "department": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "salary": forms.NumberInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "joining_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),

            "profile_picture": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                    "accept": "image/*",
                }
            ),

            "address": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                }
            ),
        }

    # ==========================================================
    # INITIALIZATION
    # ==========================================================

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        # ------------------------------------------------------
        # Employee ID cannot be changed while editing
        # ------------------------------------------------------

        if self.instance and self.instance.pk:

            self.fields["employee_id"].disabled = True

            self.fields["employee_id"].help_text = (
                "Employee ID cannot be changed after creation."
            )

        # ------------------------------------------------------
        # Set current status when editing
        # ------------------------------------------------------

        if self.instance and self.instance.pk:

            self.fields["status"].initial = (
                "True"
                if self.instance.is_active
                else "False"
            )

        # ------------------------------------------------------
        # Department dropdown
        # ------------------------------------------------------

        self.fields["department"].empty_label = "Select Department"

        self.fields["department"].queryset = (
            self.fields["department"]
            .queryset
            .order_by("name")
        )

    # ==========================================================
    # DATE OF BIRTH VALIDATION
    # ==========================================================

    def clean_date_of_birth(self):

        date_of_birth = self.cleaned_data.get(
            "date_of_birth"
        )

        if not date_of_birth:

            return date_of_birth

        today = date.today()

        # ------------------------------------------------------
        # Future date
        # ------------------------------------------------------

        if date_of_birth > today:

            raise ValidationError(
                "Date of Birth cannot be a future date."
            )

        # ------------------------------------------------------
        # Calculate age
        # ------------------------------------------------------

        age = (
            today.year -
            date_of_birth.year
        )

        if (
            today.month,
            today.day
        ) < (
            date_of_birth.month,
            date_of_birth.day
        ):

            age -= 1

        # ------------------------------------------------------
        # Minimum age = 18
        # ------------------------------------------------------

        if age < 18:

            raise ValidationError(
                "Employee must be at least 18 years old."
            )

        return date_of_birth

    # ==========================================================
    # PROFILE PICTURE VALIDATION
    # ==========================================================

    def clean_profile_picture(self):

        profile_picture = self.cleaned_data.get(
            "profile_picture"
        )

        if not profile_picture:

            return profile_picture

        # ------------------------------------------------------
        # File size
        # ------------------------------------------------------

        if profile_picture.size > MAX_PROFILE_PICTURE_SIZE:

            raise ValidationError(
                "Profile picture size must not exceed 2 MB."
            )

        # ------------------------------------------------------
        # Image validation
        # ------------------------------------------------------

        try:

            from PIL import Image

            image = Image.open(profile_picture)

            image.verify()

        except Exception:

            raise ValidationError(
                "Please upload a valid image file."
            )

        return profile_picture

    # ==========================================================
    # SAVE
    # ==========================================================

    def save(self, commit=True):

        employee = super().save(commit=False)

        status = self.cleaned_data.get("status")

        employee.is_active = (
            status == "True"
        )

        if commit:

            employee.save()

        return employee