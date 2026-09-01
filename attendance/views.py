from datetime import date, datetime
from decimal import Decimal

from django.contrib import messages
from django.db.models import Q
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)

from employees.models import Employee

from .forms import AttendanceForm
from .models import Attendance


# ============================================================
# ATTENDANCE LIST
# ============================================================

def attendance_list(request):

    # ========================================================
    # ALWAYS USE TODAY'S DATE
    # ========================================================

    today = date.today()

    search = request.GET.get(
        "search",
        ""
    )

    department = request.GET.get(
        "department",
        ""
    )

    # ========================================================
    # EMPLOYEES
    # ========================================================

    employees = Employee.objects.all()

    # ========================================================
    # SEARCH
    # ========================================================

    if search:

        employees = employees.filter(

            Q(first_name__icontains=search)
            |
            Q(last_name__icontains=search)
            |
            Q(employee_id__icontains=search)

        )

    # ========================================================
    # DEPARTMENT FILTER
    # ========================================================

    if department:

        employees = employees.filter(
            department=department
        )

    # ========================================================
    # ATTENDANCE DATA
    # ========================================================

    attendance_data = []

    for employee in employees:

        attendance = Attendance.objects.filter(

            employee=employee,

            date=today

        ).first()

        attendance_data.append({

            "employee": employee,

            "attendance": attendance

        })

    # ========================================================
    # COUNTS
    # ========================================================

    present_count = Attendance.objects.filter(
        date=today,
        status="Present"
    ).count()

    leave_count = Attendance.objects.filter(
        date=today,
        status="Leave"
    ).count()

    halfday_count = Attendance.objects.filter(
        date=today,
        status="Half Day"
    ).count()

    # ========================================================
    # CONTEXT
    # ========================================================

    context = {

        "attendance_data": attendance_data,

        "departments": Employee.objects.values_list(
            "department",
            flat=True
        ).distinct(),

        "search": search,

        "selected_department": department,

        "selected_date": today,

        "present_count": present_count,

        "leave_count": leave_count,

        "halfday_count": halfday_count,

    }

    return render(

        request,

        "attendance/attendance_list.html",

        context

    )


# ============================================================
# ADD ATTENDANCE
# ============================================================

def add_attendance(request):

    today = date.today()

    # ========================================================
    # POST
    # ========================================================

    if request.method == "POST":

        form = AttendanceForm(
            request.POST
        )

        if form.is_valid():

            attendance = form.save(
                commit=False
            )

            # ------------------------------------------------
            # NEVER TRUST SUBMITTED DATE
            # ------------------------------------------------

            attendance.date = today

            attendance.save()

            messages.success(
                request,
                "Attendance added successfully."
            )

            return redirect(
                "attendance_list"
            )

    # ========================================================
    # GET
    # ========================================================

    else:

        form = AttendanceForm(
            initial={
                "date": today
            }
        )

    return render(

        request,

        "attendance/add_attendance.html",

        {
            "form": form
        }

    )


# ============================================================
# EDIT ATTENDANCE
# ============================================================

def edit_attendance(request, pk):

    attendance = get_object_or_404(
        Attendance,
        pk=pk
    )

    today = date.today()

    # ========================================================
    # POST
    # ========================================================

    if request.method == "POST":

        form = AttendanceForm(

            request.POST,

            instance=attendance

        )

        if form.is_valid():

            attendance = form.save(
                commit=False
            )

            # ------------------------------------------------
            # ALWAYS FORCE TODAY'S DATE
            # ------------------------------------------------

            attendance.date = today

            attendance.save()

            messages.success(
                request,
                "Attendance updated successfully."
            )

            return redirect(
                "attendance_list"
            )

    # ========================================================
    # GET
    # ========================================================

    else:

        form = AttendanceForm(
            instance=attendance
        )

        form.initial["date"] = today

    return render(

        request,

        "attendance/edit_attendance.html",

        {
            "form": form,

            "attendance": attendance
        }

    )


# ============================================================
# DELETE ATTENDANCE
# ============================================================

def delete_attendance(request, pk):

    attendance = get_object_or_404(

        Attendance,

        pk=pk

    )

    # ========================================================
    # DELETE
    # ========================================================

    if request.method == "POST":

        attendance.delete()

        messages.success(

            request,

            "Attendance deleted successfully."

        )

        return redirect(
            "attendance_list"
        )

    # ========================================================
    # CONFIRMATION PAGE
    # ========================================================

    return render(

        request,

        "attendance/delete_attendance.html",

        {
            "attendance": attendance
        }

    )


# ============================================================
# CHECK IN
# ============================================================

def check_in(request, employee_id):

    employee = get_object_or_404(

        Employee,

        id=employee_id

    )

    today = date.today()

    # ========================================================
    # CHECK IF ATTENDANCE ALREADY EXISTS
    # ========================================================

    attendance = Attendance.objects.filter(

        employee=employee,

        date=today

    ).first()

    if attendance:

        messages.warning(

            request,

            "Attendance already exists for today."

        )

        return redirect(
            "attendance_list"
        )

    # ========================================================
    # CURRENT TIME
    # ========================================================

    current_time = datetime.now().time()

    # ========================================================
    # CREATE ATTENDANCE
    #
    # IMPORTANT:
    # check_out remains NULL.
    # ========================================================

    attendance = Attendance(

        employee=employee,

        date=today,

        check_in=current_time,

        check_out=None,

        status="Present",

        working_hours=Decimal("0.00")

    )

    # ========================================================
    # SAVE
    #
    # Model save() no longer calls full_clean().
    # Therefore check-in can be saved without checkout.
    # ========================================================

    attendance.save()

    messages.success(

        request,

        f"{employee.first_name} checked in successfully."

    )

    return redirect(
        "attendance_list"
    )


# ============================================================
# CHECK OUT
# ============================================================

def check_out(request, attendance_id):

    attendance = get_object_or_404(

        Attendance,

        id=attendance_id

    )

    # ========================================================
    # ALREADY CHECKED OUT
    # ========================================================

    if attendance.check_out:

        messages.warning(

            request,

            "Already checked out."

        )

        return redirect(
            "attendance_list"
        )

    # ========================================================
    # CHECK-IN REQUIRED
    # ========================================================

    if not attendance.check_in:

        messages.error(

            request,

            "Cannot check out because Check-In time is missing."

        )

        return redirect(
            "attendance_list"
        )

    # ========================================================
    # CURRENT CHECK-OUT TIME
    # ========================================================

    check_out_time = datetime.now().time()

    # ========================================================
    # CALCULATE WORKING HOURS
    # ========================================================

    check_in_datetime = datetime.combine(

        attendance.date,

        attendance.check_in

    )

    check_out_datetime = datetime.combine(

        attendance.date,

        check_out_time

    )

    duration = (

        check_out_datetime
        -
        check_in_datetime

    )

    total_seconds = duration.total_seconds()

    total_hours = total_seconds / 3600

    # ========================================================
    # PRESENT VALIDATION
    #
    # MUST BE MORE THAN 7 HOURS
    # ========================================================

    if attendance.status == "Present":

        if total_hours <= 7:

            messages.error(

                request,

                f"Cannot check out. Present attendance "
                f"requires more than 7 hours. "
                f"Current working time: "
                f"{total_hours:.2f} hours."

            )

            return redirect(
                "attendance_list"
            )

    # ========================================================
    # HALF DAY VALIDATION
    #
    # MUST BE MORE THAN 3 HOURS
    # ========================================================

    if attendance.status == "Half Day":

        if total_hours <= 3:

            messages.error(

                request,

                f"Cannot check out. Half Day attendance "
                f"requires more than 3 hours. "
                f"Current working time: "
                f"{total_hours:.2f} hours."

            )

            return redirect(
                "attendance_list"
            )

    # ========================================================
    # ROUND TO 2 DECIMAL PLACES
    # ========================================================

    working_hours = Decimal(
        str(
            round(
                total_hours,
                2
            )
        )
    ).quantize(
        Decimal("0.01")
    )

    # ========================================================
    # UPDATE ATTENDANCE
    # ========================================================

    attendance.check_out = check_out_time

    attendance.working_hours = working_hours

    attendance.save()

    # ========================================================
    # SUCCESS MESSAGE
    # ========================================================

    messages.success(

        request,

        f"Checked out successfully. "
        f"Total working time: "
        f"{working_hours:.2f} hours."

    )

    return redirect(
        "attendance_list"
    )