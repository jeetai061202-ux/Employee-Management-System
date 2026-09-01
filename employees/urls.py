from django.urls import path
from . import views

urlpatterns = [

    path(
        "",
        views.employee_list,
        name="employee_list"
    ),

    path(
        "add/",
        views.add_employee,
        name="add_employee"
    ),

    path(
        "<int:pk>/",
        views.employee_detail,
        name="employee_detail"
    ),

    path(
        "<int:pk>/edit/",
        views.edit_employee,
        name="edit_employee"
    ),

    path(
        "<int:pk>/delete/",
        views.delete_employee,
        name="delete_employee"
    ),

    path(
    "export/pdf/",
    views.export_employees_pdf,
    name="export_pdf",
    ),

    path("export/excel/", views.export_employees_excel, name="export_excel"),
    path("export/pdf/", views.export_employees_pdf, name="export_pdf"), 

]