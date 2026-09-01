from datetime import datetime

from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
)

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

from django.core.mail import send_mail
from django.conf import settings

from .forms import EmployeeForm
from .models import Employee


# ==========================================================
# Employee List
# ==========================================================

def employee_list(request):

    employees = Employee.objects.all()

    search = request.GET.get("search", "")
    department = request.GET.get("department", "")
    status = request.GET.get("status", "")

    if search:
        employees = employees.filter(
            Q(first_name__icontains=search)
            | Q(last_name__icontains=search)
            | Q(employee_id__icontains=search)
            | Q(email__icontains=search)
        )

    if department:
        employees = employees.filter(
            department=department
        )

    # ======================================================
    # ACTIVE / INACTIVE FILTER
    # ======================================================

    if status == "Active":
        employees = employees.filter(
            is_active=True
        )

    elif status == "Inactive":
        employees = employees.filter(
            is_active=False
        )

    paginator = Paginator(
        employees,
        10
    )

    page_number = request.GET.get("page")

    page_obj = paginator.get_page(
        page_number
    )

    context = {

        "employees": page_obj,

        "page_obj": page_obj,

        "departments": Employee.objects.values_list(
            "department",
            flat=True
        ).distinct(),

        "search": search,

        "department": department,

        "status": status,

        # ==================================================
        # STATISTICS
        # ==================================================

        "total_employees": Employee.objects.count(),

        "active_employees": Employee.objects.filter(
            is_active=True
        ).count(),

        "inactive_employees": Employee.objects.filter(
            is_active=False
        ).count(),
    }

    return render(
        request,
        "employees/employee_list.html",
        context
    )


# ==========================================================
# Add Employee
# ==========================================================

def add_employee(request):

    if request.method == "POST":

        form = EmployeeForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            employee = form.save()

            try:

                send_mail(

                    subject="Welcome to Employee Management System",

                    message=f"""
Dear {employee.first_name},

Welcome to our organization!

Your employee account has been created successfully.

Employee ID : {employee.employee_id}

Department : {employee.department}

Designation : {employee.designation}

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
                "Employee added successfully."
            )

            return redirect(
                "employee_list"
            )

    else:

        form = EmployeeForm()

    return render(
        request,
        "employees/add_employee.html",
        {
            "form": form
        }
    )


# ==========================================================
# Employee Detail
# ==========================================================

def employee_detail(request, pk):

    employee = get_object_or_404(
        Employee,
        pk=pk
    )

    return render(
        request,
        "employees/employee_detail.html",
        {
            "employee": employee
        }
    )


# ==========================================================
# Edit Employee
# ==========================================================

def edit_employee(request, pk):

    employee = get_object_or_404(
        Employee,
        pk=pk
    )

    if request.method == "POST":

        form = EmployeeForm(
            request.POST,
            request.FILES,
            instance=employee
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Employee updated successfully."
            )

            return redirect(
                "employee_list"
            )

    else:

        form = EmployeeForm(
            instance=employee
        )

    return render(
        request,
        "employees/edit_employee.html",
        {
            "form": form,
            "employee": employee
        }
    )


# ==========================================================
# Delete Employee
# ==========================================================

def delete_employee(request, pk):

    employee = get_object_or_404(
        Employee,
        pk=pk
    )

    if request.method == "POST":

        employee.delete()

        messages.success(
            request,
            "Employee deleted successfully."
        )

        return redirect(
            "employee_list"
        )

    return render(
        request,
        "employees/delete_employee.html",
        {
            "employee": employee
        }
    )


# ==========================================================
# Export Excel
# ==========================================================

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

    employees = Employee.objects.all()

    for employee in employees:

        worksheet.append([

            employee.employee_id,

            employee.first_name,

            employee.last_name,

            employee.email,

            employee.phone,

            employee.department,

            employee.designation,

            "Active" if employee.is_active else "Inactive",

            float(employee.salary),

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
# Export PDF
# ==========================================================

def export_employees_pdf(request):

    response = HttpResponse(
        content_type="application/pdf"
    )

    response["Content-Disposition"] = (
        'attachment; filename="employees.pdf"'
    )

    doc = SimpleDocTemplate(response)

    styles = getSampleStyleSheet()

    elements = []

    elements.append(
        Paragraph(
            "<b>Employee Management System</b>",
            styles["Title"]
        )
    )

    elements.append(
        Paragraph(
            f"Generated on: "
            f"{datetime.now().strftime('%d-%m-%Y %H:%M')}",
            styles["Normal"]
        )
    )

    elements.append(
        Spacer(
            1,
            0.3 * inch
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

    employees = Employee.objects.all()

    for employee in employees:

        data.append([

            employee.employee_id,

            f"{employee.first_name} "
            f"{employee.last_name}",

            employee.department,

            employee.designation,

            "Active" if employee.is_active else "Inactive",

            f"₹ {employee.salary}",
        ])

    table = Table(data)

    table.setStyle(
        TableStyle([

            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.darkblue
            ),

            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white
            ),

            (
                "GRID",
                (0, 0),
                (-1, -1),
                1,
                colors.black
            ),

            (
                "BACKGROUND",
                (0, 1),
                (-1, -1),
                colors.beige
            ),

            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),

            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, 0),
                10
            ),

            (
                "ALIGN",
                (0, 0),
                (-1, -1),
                "CENTER"
            ),
        ])
    )

    elements.append(table)

    doc.build(elements)

    return response