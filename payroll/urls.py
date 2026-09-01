from django.urls import path

from . import views

urlpatterns = [

    path(
        "",
        views.payroll_list,
        name="payroll_list"
    ),

    path(
        "add/",
        views.add_payroll,
        name="add_payroll"
    ),

    path(
        "edit/<int:pk>/",
        views.edit_payroll,
        name="edit_payroll"
    ),

    path(
        "delete/<int:pk>/",
        views.delete_payroll,
        name="delete_payroll"
    ),
    path(
        "salary-slip/<int:pk>/",
        views.salary_slip_pdf,
        name="salary_slip_pdf",
    ),
    path(
        "export/excel/",
        views.export_payroll_excel,
        name="export_payroll_excel",
    ),

]