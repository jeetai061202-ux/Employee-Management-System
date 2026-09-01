from django.contrib import admin
from .models import Leave


@admin.register(Leave)
class LeaveAdmin(admin.ModelAdmin):

    list_display = (

        "employee",
        "leave_type",
        "start_date",
        "end_date",
        "status",

    )

    list_filter = (

        "status",
        "leave_type",

    )

    search_fields = (

        "employee__first_name",
        "employee__last_name",

    )