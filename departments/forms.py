from django import forms

from .models import Department


class DepartmentForm(forms.ModelForm):

    class Meta:

        model = Department

        fields = [
            "name",
            "description",
        ]

        widgets = {

            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter department name",
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