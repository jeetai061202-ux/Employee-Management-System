from datetime import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from openpyxl import Workbook

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from accounts.decorators import role_required
from departments.models import Department

from .forms import EmployeeForm
from .models import Employee


# ==========================================================
# ROLE HELPERS
# ==========================================================

def is_admin_or_hr(user):
    return (
        user.role
        and user.role.name in ["Admin", "HR"]
    )


def is_employee(user):
    return (
        user.role
        and user.role.name == "Employee"
    )


# ==========================================================
# EMPLOYEE LIST
# ==========================================================

@login_required
@role_required("ADMIN", "HR", "EMPLOYEE")
def employee_list(request):

    user = request.user

    if is_admin_or_hr(user):

        employees = Employee.objects.select_related(
            "department",
            "user",
        ).all()

    else:

        employee = getattr(
            user,
            "employee_profile",
            None,
        )

        if employee is None:

            messages.warning(
                request,
                "Your employee profile has not been created yet.",
            )

            return render(
                request,
                "employees/employee_list.html",
                {
                    "employees": Employee.objects.none(),
                    "page_obj": None,
                    "departments": Department.objects.none(),
                    "search": "",
                    "department": "",
                    "status": "",
                    "total_employees": 0,
                    "active_employees": 0,
                    "inactive_employees": 0,
                },
            )

        employees = Employee.objects.select_related(
            "department",
            "user",
        ).filter(
            user=user
        )

    search = request.GET.get(
        "search",
        "",
    ).strip()

    department = request.GET.get(
        "department",
        "",
    ).strip()

    status = request.GET.get(
        "status",
        "",
    ).strip()

    if search:

        employees = employees.filter(
            Q(first_name__icontains=search)
            | Q(last_name__icontains=search)
            | Q(employee_id__icontains=search)
            | Q(email__icontains=search)
        )

    # UUID department IDs must not be converted to int.
    if department:

        employees = employees.filter(
            department_id=department
        )

    if status == "Active":

        employees = employees.filter(
            is_active=True
        )

    elif status == "Inactive":

        employees = employees.filter(
            is_active=False
        )

    elif is_admin_or_hr(user):

        employees = employees.filter(
            is_active=True
        )

    paginator = Paginator(
        employees,
        10,
    )

    page_number = request.GET.get(
        "page"
    )

    page_obj = paginator.get_page(
        page_number
    )

    if is_admin_or_hr(user):

        departments = Department.objects.filter(
            is_active=True
        ).order_by(
            "name"
        )

    else:

        departments = Department.objects.none()

    if is_admin_or_hr(user):

        total_employees = Employee.objects.count()

        active_employees = Employee.objects.filter(
            is_active=True
        ).count()

        inactive_employees = Employee.objects.filter(
            is_active=False
        ).count()

    else:

        employee = getattr(
            user,
            "employee_profile",
            None,
        )

        if employee is not None:

            total_employees = 1

            active_employees = (
                1
                if employee.is_active
                else 0
            )

            inactive_employees = (
                0
                if employee.is_active
                else 1
            )

        else:

            total_employees = 0
            active_employees = 0
            inactive_employees = 0

    context = {
        "employees": page_obj,
        "page_obj": page_obj,
        "departments": departments,
        "search": search,
        "department": department,
        "status": status,
        "total_employees": total_employees,
        "active_employees": active_employees,
        "inactive_employees": inactive_employees,
    }

    return render(
        request,
        "employees/employee_list.html",
        context,
    )


# ==========================================================
# ADD EMPLOYEE
# ==========================================================

@login_required
@role_required("ADMIN", "HR")
def add_employee(request):

    if request.method == "POST":

        form = EmployeeForm(
            request.POST,
            request.FILES,
            current_user=request.user,
            self_edit=False,
        )

        if form.is_valid():

            employee = form.save(commit=False)

            employee.created_by = request.user
            employee.updated_by = request.user

            employee.save()

            linked_user = employee.user

            if linked_user:

                linked_user.first_name = employee.first_name
                linked_user.last_name = employee.last_name
                linked_user.email = employee.email
                linked_user.phone_number = employee.phone

                linked_user.save(
                    update_fields=[
                        "first_name",
                        "last_name",
                        "email",
                        "phone_number",
                        "updated_at",
                    ]
                )

            try:

                send_mail(
                    subject=(
                        "Welcome to Employee "
                        "Management System"
                    ),
                    message=f"""
Dear {employee.first_name},

Welcome to our organization!

Your employee profile has been created successfully.

Employee ID: {employee.employee_id}
Department: {employee.department.name}
Designation: {employee.designation}

We wish you a successful journey with us.

Regards,
HR Department
                    """,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[
                        employee.email
                    ],
                    fail_silently=True,
                )

            except Exception:
                pass

            messages.success(
                request,
                "Employee added and linked to the registered user successfully.",
            )

            return redirect(
                "employee_list"
            )

    else:

        form = EmployeeForm(
            current_user=request.user,
            self_edit=False,
        )

    return render(
        request,
        "employees/add_employee.html",
        {
            "form": form,
        },
    )


# ==========================================================
# EMPLOYEE DETAIL
# ==========================================================

@login_required
@role_required("ADMIN", "HR", "EMPLOYEE")
def employee_detail(request, pk):

    employee = get_object_or_404(
        Employee.objects.select_related(
            "department",
            "user",
        ),
        pk=pk,
    )

    if is_employee(request.user):

        if employee.user_id != request.user.id:

            messages.error(
                request,
                (
                    "You are not allowed to view "
                    "another employee's details."
                ),
            )

            return redirect(
                "employee_list"
            )

    return render(
        request,
        "employees/employee_detail.html",
        {
            "employee": employee,
        },
    )


# ==========================================================
# EDIT EMPLOYEE
# ==========================================================

@login_required
@role_required("ADMIN", "HR", "EMPLOYEE")
def edit_employee(request, pk):

    employee = get_object_or_404(
        Employee.objects.select_related(
            "department",
            "user",
        ),
        pk=pk,
    )

    if is_employee(request.user):

        if employee.user_id != request.user.id:

            messages.error(
                request,
                (
                    "You are not allowed to edit "
                    "another employee's details."
                ),
            )

            return redirect(
                "employee_list"
            )

        self_edit = True

    else:

        self_edit = False

    if request.method == "POST":

        form = EmployeeForm(
            request.POST,
            request.FILES,
            instance=employee,
            current_user=request.user,
            self_edit=self_edit,
        )

        if form.is_valid():

            employee = form.save(commit=False)

            employee.updated_by = request.user

            employee.save()

            linked_user = employee.user

            if linked_user:

                linked_user.first_name = employee.first_name
                linked_user.last_name = employee.last_name
                linked_user.email = employee.email
                linked_user.phone_number = employee.phone

                linked_user.save(
                    update_fields=[
                        "first_name",
                        "last_name",
                        "email",
                        "phone_number",
                        "updated_at",
                    ]
                )

            messages.success(
                request,
                "Employee updated successfully.",
            )

            return redirect(
                "employee_list"
            )

    else:

        form = EmployeeForm(
            instance=employee,
            current_user=request.user,
            self_edit=self_edit,
        )

    return render(
        request,
        "employees/edit_employee.html",
        {
            "form": form,
            "employee": employee,
        },
    )


# ==========================================================
# DELETE EMPLOYEE - SOFT DELETE
# ==========================================================

@login_required
@role_required("ADMIN", "HR")
def delete_employee(request, pk):

    employee = get_object_or_404(
        Employee,
        pk=pk,
    )

    if request.method == "POST":

        employee.is_active = False
        employee.updated_by = request.user

        employee.save(
            update_fields=[
                "is_active",
                "updated_by",
                "updated_at",
            ]
        )

        messages.success(
            request,
            "Employee deactivated successfully.",
        )

        return redirect(
            "employee_list"
        )

    return render(
        request,
        "employees/delete_employee.html",
        {
            "employee": employee,
        },
    )


# ==========================================================
# EXPORT EXCEL
# ==========================================================

@login_required
@role_required("ADMIN", "HR")
def export_employees_excel(request):

    workbook = Workbook()

    worksheet = workbook.active

    worksheet.title = "Employees"

    worksheet.append([
        "Employee ID",
        "First Name",
        "Last Name",
        "Email",
        "Phone",
        "Department",
        "Designation",
        "Status",
        "Salary",
    ])

    employees = Employee.objects.select_related(
        "department"
    ).all()

    for employee in employees:

        worksheet.append([
            employee.employee_id,
            employee.first_name,
            employee.last_name,
            employee.email,
            employee.phone,
            (
                employee.department.name
                if employee.department
                else ""
            ),
            employee.designation,
            (
                "Active"
                if employee.is_active
                else "Inactive"
            ),
            (
                float(employee.salary)
                if employee.salary is not None
                else ""
            ),
        ])

    response = HttpResponse(
        content_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        )
    )

    response["Content-Disposition"] = (
        'attachment; filename="employees.xlsx"'
    )

    workbook.save(response)

    return response


# ==========================================================
# EXPORT PDF
# ==========================================================

@login_required
@role_required("ADMIN", "HR")
def export_employees_pdf(request):

    response = HttpResponse(
        content_type="application/pdf"
    )

    response["Content-Disposition"] = (
        'attachment; filename="employees.pdf"'
    )

    document = SimpleDocTemplate(
        response
    )

    styles = getSampleStyleSheet()

    elements = []

    elements.append(
        Paragraph(
            "<b>Employee Management System</b>",
            styles["Title"],
        )
    )

    elements.append(
        Paragraph(
            (
                "Generated on: "
                f"{datetime.now().strftime('%d-%m-%Y %H:%M')}"
            ),
            styles["Normal"],
        )
    )

    elements.append(
        Spacer(
            1,
            0.3 * inch,
        )
    )

    data = [[
        "ID",
        "Name",
        "Department",
        "Designation",
        "Status",
        "Salary",
    ]]

    employees = Employee.objects.select_related(
        "department"
    ).all()

    for employee in employees:

        data.append([
            employee.employee_id,
            (
                f"{employee.first_name} "
                f"{employee.last_name}"
            ),
            (
                employee.department.name
                if employee.department
                else ""
            ),
            employee.designation,
            (
                "Active"
                if employee.is_active
                else "Inactive"
            ),
            (
                f"₹ {employee.salary}"
                if employee.salary is not None
                else ""
            ),
        ])

    table = Table(
        data
    )

    table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.darkblue,
            ),
            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white,
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                1,
                colors.black,
            ),
            (
                "BACKGROUND",
                (0, 1),
                (-1, -1),
                colors.beige,
            ),
            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold",
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, 0),
                10,
            ),
            (
                "ALIGN",
                (0, 0),
                (-1, -1),
                "CENTER",
            ),
        ])
    )

    elements.append(
        table
    )

    document.build(
        elements
    )

    return response