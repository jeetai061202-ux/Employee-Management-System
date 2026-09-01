from django import forms
from .models import Payroll


class PayrollForm(forms.ModelForm):

    class Meta:

        model = Payroll

        exclude = ("net_salary",)

        widgets = {

            "employee": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "month": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "year": forms.NumberInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "basic_salary": forms.NumberInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "hra": forms.NumberInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "allowance": forms.NumberInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "bonus": forms.NumberInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "tax": forms.NumberInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "pf": forms.NumberInput(
                attrs={
                    "class": "form-control"
                }
            ),

        }