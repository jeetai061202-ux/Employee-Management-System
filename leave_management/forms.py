from django import forms
from .models import Leave


class LeaveForm(forms.ModelForm):

    class Meta:

        model = Leave

        fields = [
            "employee",
            "leave_type",
            "start_date",
            "end_date",
            "reason",
        ]

        widgets = {

            "employee": forms.Select(attrs={
                "class": "form-select"
            }),

            "leave_type": forms.Select(attrs={
                "class": "form-select"
            }),

            "start_date": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date"
            }),

            "end_date": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date"
            }),

            "reason": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4
            }),

        }