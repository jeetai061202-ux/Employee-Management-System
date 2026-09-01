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
        "edit/<int:pk>/",
        views.edit_attendance,
        name="edit_attendance",
    ),

    path(
        "delete/<int:pk>/",
        views.delete_attendance,
        name="delete_attendance",
    ),
    path(
    "check-in/<int:employee_id>/",
    views.check_in,
    name="check_in",
    ),

    path(
    "check-out/<int:attendance_id>/",
    views.check_out,
    name="check_out",
    ),

]