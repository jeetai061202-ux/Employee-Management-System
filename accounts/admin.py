from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):

    # ======================================================
    # LIST DISPLAY
    # ======================================================

    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "role",
        "is_active",
        "is_staff",
    )


    # ======================================================
    # FILTERS
    # ======================================================

    list_filter = (
        "role",
        "is_active",
        "is_staff",
    )


    # ======================================================
    # SEARCH
    # ======================================================

    search_fields = (
        "username",
        "email",
        "first_name",
        "last_name",
        "phone",
    )


    # ======================================================
    # EDIT USER
    # ======================================================

    fieldsets = UserAdmin.fieldsets + (
        (
            "Additional Information",
            {
                "fields": (
                    "role",
                    "phone",
                    "profile_picture",
                )
            },
        ),
    )


    # ======================================================
    # ADD USER
    # ======================================================

    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Additional Information",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "email",
                    "role",
                    "phone",
                    "profile_picture",
                )
            },
        ),
    )