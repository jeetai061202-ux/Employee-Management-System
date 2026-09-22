from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User, Role


# ==========================================================
# ADMIN CREATE USER FORM
# ==========================================================

class AdminUserCreationForm(UserCreationForm):

    class Meta:
        model = User

        fields = (
            "first_name",
            "last_name",
            "username",
            "email",
            "phone_number",
            "role",
            "password1",
            "password2",
        )

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"

        self.fields["first_name"].widget.attrs["placeholder"] = (
            "Enter first name"
        )

        self.fields["last_name"].widget.attrs["placeholder"] = (
            "Enter last name"
        )

        self.fields["username"].label = "User ID"
        self.fields["username"].widget.attrs["placeholder"] = (
            "Enter User ID"
        )

        self.fields["email"].widget.attrs["placeholder"] = (
            "Enter email address"
        )

        self.fields["phone_number"].label = "Phone Number"
        self.fields["phone_number"].widget.attrs["placeholder"] = (
            "Enter phone number"
        )

        self.fields["role"].label = "Role"
        self.fields["role"].widget.attrs["class"] = "form-select"

        self.fields["password1"].widget.attrs["placeholder"] = (
            "Create password"
        )

        self.fields["password2"].widget.attrs["placeholder"] = (
            "Confirm password"
        )

        # Role is now a ForeignKey to the Role table.
        self.fields["role"].queryset = Role.objects.filter(
            name__in=["Employee", "HR", "Admin"]
        ).order_by("name")

        self.fields["role"].empty_label = "Select role"

    # ------------------------------------------------------
    # PHONE VALIDATION
    # ------------------------------------------------------

    def clean_phone_number(self):

        phone = self.cleaned_data.get(
            "phone_number",
            ""
        ).strip()

        if not phone.isdigit():

            raise forms.ValidationError(
                "Phone number must contain only numerical digits."
            )

        if len(phone) < 10:

            raise forms.ValidationError(
                "Phone number must contain at least 10 digits."
            )

        if len(phone) > 15:

            raise forms.ValidationError(
                "Phone number cannot contain more than 15 digits."
            )

        return phone

    # ------------------------------------------------------
    # EMAIL VALIDATION
    # ------------------------------------------------------

    def clean_email(self):

        email = self.cleaned_data.get(
            "email",
            ""
        ).strip().lower()

        if User.objects.filter(
            email__iexact=email
        ).exists():

            raise forms.ValidationError(
                "An account with this email already exists."
            )

        return email

    # ------------------------------------------------------
    # USER ID VALIDATION
    # ------------------------------------------------------

    def clean_username(self):

        username = self.cleaned_data.get(
            "username",
            ""
        ).strip()

        if User.objects.filter(
            username__iexact=username
        ).exists():

            raise forms.ValidationError(
                "This User ID is already registered. Please choose another."
            )

        return username

    # ------------------------------------------------------
    # SAVE USER
    # ------------------------------------------------------

    def save(self, commit=True):

        user = super().save(commit=False)

        user.role = self.cleaned_data["role"]

        if commit:
            user.save()

        return user


# ==========================================================
# ADMIN USER MANAGEMENT FORM
# ==========================================================

class UserManagementForm(forms.ModelForm):

    class Meta:
        model = User

        fields = (
            "first_name",
            "last_name",
            "username",
            "email",
            "phone_number",
            "role",
            "is_active",
        )

        widgets = {
            "first_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter first name",
                }
            ),

            "last_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter last name",
                }
            ),

            "username": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter User ID",
                }
            ),

            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter email address",
                }
            ),

            "phone_number": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter phone number",
                }
            ),

            "role": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "is_active": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
        }

    def __init__(self, *args, **kwargs):

        super().__init__(
            *args,
            **kwargs
        )

        self.fields["username"].label = "User ID"

        self.fields["phone_number"].label = "Phone Number"

        self.fields["role"].label = "Role"

        self.fields["role"].queryset = Role.objects.filter(
            name__in=["Employee", "HR", "Admin"]
        ).order_by("name")

        self.fields["role"].empty_label = "Select role"

    # ------------------------------------------------------
    # PHONE VALIDATION
    # ------------------------------------------------------

    def clean_phone_number(self):

        phone = self.cleaned_data.get(
            "phone_number",
            ""
        ).strip()

        if not phone.isdigit():

            raise forms.ValidationError(
                "Phone number must contain only numerical digits."
            )

        if len(phone) < 10:

            raise forms.ValidationError(
                "Phone number must contain at least 10 digits."
            )

        if len(phone) > 15:

            raise forms.ValidationError(
                "Phone number cannot contain more than 15 digits."
            )

        return phone

    # ------------------------------------------------------
    # EMAIL VALIDATION
    # ------------------------------------------------------

    def clean_email(self):

        email = self.cleaned_data.get(
            "email",
            ""
        ).strip().lower()

        existing_user = User.objects.filter(
            email__iexact=email
        ).exclude(
            pk=self.instance.pk
        )

        if existing_user.exists():

            raise forms.ValidationError(
                "An account with this email already exists."
            )

        return email

    # ------------------------------------------------------
    # USER ID VALIDATION
    # ------------------------------------------------------

    def clean_username(self):

        username = self.cleaned_data.get(
            "username",
            ""
        ).strip()

        existing_user = User.objects.filter(
            username__iexact=username
        ).exclude(
            pk=self.instance.pk
        )

        if existing_user.exists():

            raise forms.ValidationError(
                "This User ID is already registered."
            )

        return username