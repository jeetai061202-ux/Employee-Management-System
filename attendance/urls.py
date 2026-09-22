
from django.urls import path

from . import views


urlpatterns = [
    path(
        "",
        views.attendance_list,
        name="attendance_list",
    ),

    path(
        "add/",
        views.add_attendance,
        name="add_attendance",
    ),

    path(
        "edit/<uuid:pk>/",
        views.edit_attendance,
        name="edit_attendance",
    ),

    path(
        "delete/<uuid:pk>/",
        views.delete_attendance,
        name="delete_attendance",
    ),

    path(
        "check-in/<uuid:employee_id>/",
        views.check_in,
        name="check_in",
    ),

    path(
        "check-out/<uuid:attendance_id>/",
        views.check_out,
        name="check_out",
    ),
]

