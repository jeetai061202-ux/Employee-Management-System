from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum
from django.http import HttpResponse
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
)

from openpyxl import Workbook

from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

from accounts.decorators import role_required

from .models import Payroll
from .forms import PayrollForm


# ============================================================
# PAYROLL LIST
# ============================================================

@login_required
@role_required("ADMIN", "HR")
def payroll_list(request):

    payrolls = (
        Payroll.objects
        .select_related("employee")
        .all()
        .order_by("-year", "-month")
    )

    search = request.GET.get("search")

    if search:

        payrolls = payrolls.filter(
            Q(employee__first_name__icontains=search)
            | Q(employee__last_name__icontains=search)
            | Q(employee__employee_id__icontains=search)
        )

    context = {

        "payrolls": payrolls,

        "search": search,

        "total_payrolls": Payroll.objects.count(),

        "total_salary": Payroll.objects.aggregate(
            Sum("net_salary")
        )["net_salary__sum"] or 0,

    }

    return render(
        request,
        "payroll/payroll_list.html",
        context,
    )


# ============================================================
# ADD PAYROLL
# ============================================================

@login_required
@role_required("ADMIN", "HR")
def add_payroll(request):

    if request.method == "POST":

        form = PayrollForm(request.POST)

        if form.is_valid():

            payroll = form.save(commit=False)

            payroll.net_salary = (

                payroll.basic_salary
                + payroll.hra
                + payroll.allowance
                + payroll.bonus
                - payroll.tax
                - payroll.pf

            )

            payroll.save()

            messages.success(
                request,
                "Payroll generated successfully."
            )

            return redirect("payroll_list")

    else:

        form = PayrollForm()

    return render(
        request,
        "payroll/add_payroll.html",
        {
            "form": form
        },
    )


# ============================================================
# EDIT PAYROLL
# ============================================================

@login_required
@role_required("ADMIN", "HR")
def edit_payroll(request, pk):

    payroll = get_object_or_404(
        Payroll,
        pk=pk
    )

    if request.method == "POST":

        form = PayrollForm(
            request.POST,
            instance=payroll
        )

        if form.is_valid():

            payroll = form.save(commit=False)

            payroll.net_salary = (

                payroll.basic_salary
                + payroll.hra
                + payroll.allowance
                + payroll.bonus
                - payroll.tax
                - payroll.pf

            )

            payroll.save()

            messages.success(
                request,
                "Payroll updated successfully."
            )

            return redirect("payroll_list")

    else:

        form = PayrollForm(
            instance=payroll
        )

    return render(
        request,
        "payroll/edit_payroll.html",
        {
            "form": form
        },
    )


# ============================================================
# DELETE PAYROLL
# ============================================================

@login_required
@role_required("ADMIN", "HR")
def delete_payroll(request, pk):

    payroll = get_object_or_404(
        Payroll,
        pk=pk
    )

    if request.method == "POST":

        payroll.delete()

        messages.success(
            request,
            "Payroll deleted successfully."
        )

        return redirect("payroll_list")

    return render(
        request,
        "payroll/delete_payroll.html",
        {
            "payroll": payroll
        },
    )


# ============================================================
# SALARY SLIP PDF
# ============================================================

@login_required
@role_required("ADMIN", "HR")
def salary_slip_pdf(request, pk):

    payroll = get_object_or_404(
        Payroll,
        pk=pk
    )

    response = HttpResponse(
        content_type="application/pdf"
    )

    response["Content-Disposition"] = (
        f'attachment; filename="SalarySlip_'
        f'{payroll.employee.employee_id}.pdf"'
    )

    doc = SimpleDocTemplate(
        response
    )

    styles = getSampleStyleSheet()

    elements = []

    title = Paragraph(
        "<b>Employee Management System</b>",
        styles["Title"]
    )

    subtitle = Paragraph(
        "Salary Slip",
        styles["Heading2"]
    )

    generated = Paragraph(
        f"Generated on: "
        f"{datetime.now().strftime('%d-%m-%Y %H:%M')}",
        styles["Normal"]
    )

    elements.append(title)
    elements.append(subtitle)
    elements.append(generated)
    elements.append(
        Spacer(
            1,
            0.3 * inch
        )
    )

    employee_table = [

        [
            "Employee ID",
            payroll.employee.employee_id
        ],

        [
            "Employee Name",
            (
                f"{payroll.employee.first_name} "
                f"{payroll.employee.last_name}"
            ),
        ],

        [
            "Department",
            payroll.employee.department
        ],

        [
            "Month",
            payroll.month
        ],

        [
            "Year",
            payroll.year
        ],

    ]

    table = Table(
        employee_table,
        colWidths=[
            2.2 * inch,
            4 * inch
        ]
    )

    table.setStyle(

        TableStyle(

            [

                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    1,
                    colors.grey
                ),

                (
                    "BACKGROUND",
                    (0, 0),
                    (0, -1),
                    colors.lightgrey
                ),

                (
                    "FONTNAME",
                    (0, 0),
                    (-1, -1),
                    "Helvetica"
                ),

                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    8
                ),

            ]

        )

    )

    elements.append(table)

    elements.append(
        Spacer(
            1,
            0.4 * inch
        )
    )

    salary_table = [

        [
            "Description",
            "Amount"
        ],

        [
            "Basic Salary",
            f"₹ {payroll.basic_salary}"
        ],

        [
            "HRA",
            f"₹ {payroll.hra}"
        ],

        [
            "Allowance",
            f"₹ {payroll.allowance}"
        ],

        [
            "Bonus",
            f"₹ {payroll.bonus}"
        ],

        [
            "Tax",
            f"- ₹ {payroll.tax}"
        ],

        [
            "PF",
            f"- ₹ {payroll.pf}"
        ],

        [
            "Net Salary",
            f"₹ {payroll.net_salary}"
        ],

    ]

    salary = Table(
        salary_table
    )

    salary.setStyle(

        TableStyle(

            [

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
                    (-1, -2),
                    colors.beige
                ),

                (
                    "BACKGROUND",
                    (0, -1),
                    (-1, -1),
                    colors.lightgreen
                ),

                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold"
                ),

                (
                    "FONTNAME",
                    (0, -1),
                    (-1, -1),
                    "Helvetica-Bold"
                ),

                (
                    "ALIGN",
                    (0, 0),
                    (-1, -1),
                    "CENTER"
                ),

            ]

        )

    )

    elements.append(salary)

    doc.build(
        elements
    )

    return response


# ============================================================
# EXPORT PAYROLL EXCEL
# ============================================================

@login_required
@role_required("ADMIN", "HR")
def export_payroll_excel(request):

    workbook = Workbook()

    worksheet = workbook.active

    worksheet.title = "Payroll"

    headers = [
        "Employee ID",
        "Employee Name",
        "Department",
        "Month",
        "Year",
        "Basic Salary",
        "HRA",
        "Allowance",
        "Bonus",
        "Tax",
        "PF",
        "Net Salary",
    ]

    worksheet.append(
        headers
    )

    payrolls = (
        Payroll.objects
        .select_related("employee")
        .all()
    )

    for payroll in payrolls:

        worksheet.append([

            payroll.employee.employee_id,

            (
                f"{payroll.employee.first_name} "
                f"{payroll.employee.last_name}"
            ),

            payroll.employee.department,

            payroll.month,

            payroll.year,

            float(payroll.basic_salary),

            float(payroll.hra),

            float(payroll.allowance),

            float(payroll.bonus),

            float(payroll.tax),

            float(payroll.pf),

            float(payroll.net_salary),

        ])

    response = HttpResponse(

        content_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        )

    )

    response["Content-Disposition"] = (
        'attachment; filename="Payroll_Report.xlsx"'
    )

    workbook.save(
        response
    )

    return response