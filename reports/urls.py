from django.urls import path
from . import views

urlpatterns = [

    path(
        "",
        views.report_dashboard,
        name="report_dashboard",
    ),

    path(
        "employees/",
        views.employee_report,
        name="employee_report",
    ),

    path(
        "attendance/",
        views.attendance_report,
        name="attendance_report",
    ),

    path(
        "payroll/",
        views.payroll_report,
        name="payroll_report",
    ),

    # ==========================================
    # Employee Report Export
    # ==========================================

    path(
        "employees/excel/",
        views.employee_report_excel,
        name="employee_report_excel",
    ),

    path(
        "employees/pdf/",
        views.employee_report_pdf,
        name="employee_report_pdf",
    ),

    path(
        "attendance/excel/",
        views.attendance_report_excel,
        name="attendance_report_excel",
    ),

    path(
        "attendance/pdf/",
        views.attendance_report_pdf,
        name="attendance_report_pdf",
    ),

    path(
        "payroll/excel/",
        views.payroll_report_excel,
        name="payroll_report_excel",
    ),

    path(
        "payroll/pdf/",
        views.payroll_report_pdf,
        name="payroll_report_pdf",
    ),

]