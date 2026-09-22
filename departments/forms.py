from django import forms

from .models import Department


class DepartmentForm(forms.ModelForm):

    class Meta:

        model = Department

        fields = [
            "name",
            "code",
            "description",
        ]

        widgets = {

            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter department name",
                }
            ),

            "code": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter department code",
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter department description",
                    "rows": 4,
                }
            ),

        }

    def clean_name(self):

        name = self.cleaned_data["name"].strip()

        if not name:
            raise forms.ValidationError(
                "Department name is required."
            )

        return name

    def clean_code(self):

        code = self.cleaned_data.get("code")

        if code:
            code = code.strip().upper()

        return code