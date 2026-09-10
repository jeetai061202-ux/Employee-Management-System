from datetime import date

from django import forms
from django.core.exceptions import ValidationError
from django.db import models

from accounts.models import User
from departments.models import Department

from .models import Employee


MAX_PROFILE_PICTURE_SIZE = 2 * 1024 * 1024  # 2 MB


class EmployeeForm(forms.ModelForm):

    STATUS_CHOICES = (
        ("True", "Active"),
        ("False", "Inactive"),
    )

    # =============================================================
    # REGISTERED LOGIN ACCOUNT
    # =============================================================

    user = forms.ModelChoiceField(
        queryset=User.objects.none(),
        required=True,
        label="Registered Employee User",
        empty_label="Select Registered Employee User",
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
        help_text=(
            "Select the registered Employee user who will be linked "
            "to this Employee record."
        ),
    )

    # =============================================================
    # STATUS
    # =============================================================

    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
        label="Status",
    )

    # =============================================================
    # EMPLOYEE SELF-EDITABLE FIELDS
    # =============================================================

    EMPLOYEE_EDITABLE_FIELDS = {
        "first_name",
        "last_name",
        "email",
        "phone",
        "gender",
        "date_of_birth",
        "profile_picture",
        "address",
    }

    class Meta:

        model = Employee

        fields = [
            "user",
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

    # =============================================================
    # INITIALIZE FORM
    # =============================================================

    def __init__(
        self,
        *args,
        current_user=None,
        self_edit=False,
        **kwargs
    ):

        super().__init__(*args, **kwargs)

        self.current_user = current_user
        self.is_employee_self_edit = self_edit

        # =========================================================
        # REGISTERED EMPLOYEE USERS
        # =========================================================

        linked_user_id = None

        if self.instance and self.instance.pk:
            linked_user_id = self.instance.user_id

        available_users = (
            User.objects
            .filter(
                role="EMPLOYEE"
            )
            .order_by(
                "username"
            )
        )

        # When editing an existing Employee:
        #
        # - Show users that are not already linked.
        # - Also keep this Employee's current linked user.
        #
        if linked_user_id:

            available_users = available_users.filter(
                models.Q(
                    employee_profile__isnull=True
                )
                |
                models.Q(
                    pk=linked_user_id
                )
            )

        else:

            # Adding a new Employee:
            #
            # Only show registered Employee accounts that
            # are not already linked.
            #
            available_users = available_users.filter(
                employee_profile__isnull=True
            )

        self.fields["user"].queryset = available_users

        # =========================================================
        # EMPLOYEE SELF EDIT
        # =========================================================

        if self.is_employee_self_edit:

            for field_name in list(self.fields):

                if field_name not in self.EMPLOYEE_EDITABLE_FIELDS:

                    self.fields.pop(
                        field_name,
                        None
                    )

        # =========================================================
        # ADMIN / HR EDIT
        # =========================================================

        elif self.instance and self.instance.pk:

            self.fields["employee_id"].disabled = True

            self.fields["employee_id"].help_text = (
                "Employee ID cannot be changed after creation."
            )

            self.fields["user"].disabled = True

            self.fields["user"].help_text = (
                "The registered Employee user linked to this "
                "Employee record cannot be changed here."
            )

        # =========================================================
        # STATUS
        # =========================================================

        if (
            not self.is_employee_self_edit
            and self.instance
            and self.instance.pk
            and "status" in self.fields
        ):

            self.fields["status"].initial = (
                "True"
                if self.instance.is_active
                else "False"
            )

        # =========================================================
        # DEPARTMENT
        # =========================================================

        if "department" in self.fields:

            self.fields["department"].empty_label = (
                "Select Department"
            )

            self.fields["department"].queryset = (
                Department.objects
                .filter(
                    is_active=True
                )
                .order_by(
                    "name"
                )
            )

    # =============================================================
    # USER VALIDATION
    # =============================================================

    def clean_user(self):

        user = self.cleaned_data.get("user")

        if not user:

            raise ValidationError(
                "Please select a registered Employee user."
            )

        if user.role != "EMPLOYEE":

            raise ValidationError(
                "Only users with the Employee role can be linked "
                "to an Employee record."
            )

        existing_employee = getattr(
            user,
            "employee_profile",
            None
        )

        if existing_employee:

            # During editing, the Employee can keep its own
            # existing linked user.

            if (
                not self.instance
                or existing_employee.pk != self.instance.pk
            ):

                raise ValidationError(
                    "This registered user is already linked "
                    "to an Employee record."
                )

        return user

    # =============================================================
    # DEPARTMENT VALIDATION
    # =============================================================

    def clean_department(self):

        department = self.cleaned_data.get(
            "department"
        )

        if not department:

            raise ValidationError(
                "Please select a department."
            )

        if not department.is_active:

            raise ValidationError(
                "The selected department is inactive. "
                "Please select an active department."
            )

        return department

    # =============================================================
    # DATE OF BIRTH VALIDATION
    # =============================================================

    def clean_date_of_birth(self):

        date_of_birth = self.cleaned_data.get(
            "date_of_birth"
        )

        if not date_of_birth:
            return date_of_birth

        today = date.today()

        if date_of_birth > today:

            raise ValidationError(
                "Date of Birth cannot be a future date."
            )

        age = (
            today.year
            - date_of_birth.year
        )

        if (
            today.month,
            today.day
        ) < (
            date_of_birth.month,
            date_of_birth.day
        ):

            age -= 1

        if age < 18:

            raise ValidationError(
                "Employee must be at least 18 years old."
            )

        return date_of_birth

    # =============================================================
    # PHONE VALIDATION
    # =============================================================

    def clean_phone(self):

        phone = (
            self.cleaned_data.get("phone") or ""
        ).strip()

        if not phone.isdigit():

            raise ValidationError(
                "Phone number must contain only numerical digits."
            )

        if len(phone) < 10:

            raise ValidationError(
                "Phone number must contain at least 10 digits."
            )

        if len(phone) > 15:

            raise ValidationError(
                "Phone number cannot contain more than 15 digits."
            )

        return phone

    # =============================================================
    # EMAIL VALIDATION
    # =============================================================

    def clean_email(self):

        email = (
            self.cleaned_data.get("email") or ""
        ).strip().lower()

        if not email:

            raise ValidationError(
                "Email address is required."
            )

        if self.instance and self.instance.pk:

            existing_employee = (
                Employee.objects
                .filter(
                    email__iexact=email
                )
                .exclude(
                    pk=self.instance.pk
                )
            )

        else:

            existing_employee = (
                Employee.objects
                .filter(
                    email__iexact=email
                )
            )

        if existing_employee.exists():

            raise ValidationError(
                "An Employee with this email address "
                "already exists."
            )

        return email

    # =============================================================
    # PROFILE PICTURE VALIDATION
    # =============================================================

    def clean_profile_picture(self):

        profile_picture = self.cleaned_data.get(
            "profile_picture"
        )

        if not profile_picture:
            return profile_picture

        if profile_picture.size > MAX_PROFILE_PICTURE_SIZE:

            raise ValidationError(
                "Profile picture size must not exceed 2 MB."
            )

        try:

            from PIL import Image

            image = Image.open(
                profile_picture
            )

            image.verify()

        except Exception:

            raise ValidationError(
                "Please upload a valid image file."
            )

        return profile_picture

    # =============================================================
    # SAVE
    # =============================================================

    def save(self, commit=True):

        employee = super().save(
            commit=False
        )

        # =========================================================
        # EMPLOYEE SELF EDIT
        # =========================================================

        if self.is_employee_self_edit:

            if commit:
                employee.save()

            return employee

        # =========================================================
        # ADMIN / HR
        # =========================================================

        selected_user = self.cleaned_data.get(
            "user"
        )

        # Explicitly connect the Employee record
        # to the registered User account.
        #
        # This is the important relationship:
        #
        # User → Employee
        #
        # Once saved, account.employee_profile will work.
        #
        if selected_user:

            employee.user = selected_user

        # =========================================================
        # STATUS
        # =========================================================

        status = self.cleaned_data.get(
            "status"
        )

        employee.is_active = (
            status == "True"
        )

        # =========================================================
        # SAVE EMPLOYEE
        # =========================================================

        if commit:

            employee.save()

        return employee