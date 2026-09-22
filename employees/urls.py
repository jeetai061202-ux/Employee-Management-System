from django.urls import path

from . import views


urlpatterns = [

    # ==========================================================
    # EMPLOYEE LIST
    # ==========================================================

    path(
        "",
        views.employee_list,
        name="employee_list"
    ),

    # ==========================================================
    # ADD EMPLOYEE
    # ==========================================================

    path(
        "add/",
        views.add_employee,
        name="add_employee"
    ),

    # ==========================================================
    # EMPLOYEE DETAILS
    # ==========================================================

    path(
        "<uuid:pk>/",
        views.employee_detail,
        name="employee_detail"
    ),

    # ==========================================================
    # EDIT EMPLOYEE
    # ==========================================================

    path(
        "<uuid:pk>/edit/",
        views.edit_employee,
        name="edit_employee"
    ),

    # ==========================================================
    # DELETE EMPLOYEE
    # ==========================================================

    path(
        "<uuid:pk>/delete/",
        views.delete_employee,
        name="delete_employee"
    ),

    # ==========================================================
    # EXPORT EXCEL
    # ==========================================================

    path(
        "export/excel/",
        views.export_employees_excel,
        name="export_excel"
    ),

    # ==========================================================
    # EXPORT PDF
    # ==========================================================

    path(
        "export/pdf/",
        views.export_employees_pdf,
        name="export_pdf"
    ),

]