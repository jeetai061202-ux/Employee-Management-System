from datetime import datetime, timedelta
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
)
from django.utils import timezone
from django.views.decorators.http import require_POST

from accounts.decorators import role_required
from employees.models import Employee
from departments.models import Department

from .forms import AttendanceForm
from .models import Attendance


# ==========================================================
# ROLE HELPERS
# ==========================================================

def _role_name(user):
    """
    Returns the current user's role name.

    The redesigned User model stores role as a ForeignKey
    to the Role model.
    """
    role = getattr(user, "role", None)

    if role is None:
        return None

    return getattr(role, "name", None)


def _is_admin_or_hr(user):
    return _role_name(user) in ["Admin", "HR"]


def _is_employee(user):
    return _role_name(user) == "Employee"


def _get_logged_in_employee(user):
    """
    Returns the Employee record linked to the logged-in User.

    Employee users must always access attendance through
    their linked Employee record.
    """
    return getattr(
        user,
        "employee_profile",
        None
    )


# ==========================================================
# ATTENDANCE LIST
# ADMIN + HR + EMPLOYEE
# ==========================================================

@login_required
@role_required("ADMIN", "HR", "EMPLOYEE")
def attendance_list(request):

    today = timezone.localdate()

    search = request.GET.get(
        "search",
        ""
    ).strip()

    department = request.GET.get(
        "department",
        ""
    ).strip()

    # ======================================================
    # ACTIVE DEPARTMENTS
    # ======================================================

    if _is_admin_or_hr(request.user):

        departments = (
            Department.objects
            .filter(is_active=True)
            .order_by("name")
        )

    else:

        departments = []

    # ======================================================
    # ADMIN / HR
    # ======================================================

    if _is_admin_or_hr(request.user):

        employees = (
            Employee.objects
            .select_related(
                "department",
                "user"
            )
            .filter(
                is_active=True
            )
        )

    # ======================================================
    # EMPLOYEE
    # ======================================================

    else:

        employee = _get_logged_in_employee(
            request.user
        )

        if employee is None:

            messages.warning(
                request,
                "Your employee profile has not been created yet."
            )

            return render(
                request,
                "attendance/attendance_list.html",
                {
                    "attendance_data": [],
                    "departments": [],
                    "search": "",
                    "selected_department": "",
                    "selected_date": today,
                    "present_count": 0,
                    "halfday_count": 0,
                }
            )

        if not employee.is_active:

            messages.warning(
                request,
                "Your employee profile is currently inactive."
            )

            return render(
                request,
                "attendance/attendance_list.html",
                {
                    "attendance_data": [],
                    "departments": [],
                    "search": "",
                    "selected_department": "",
                    "selected_date": today,
                    "present_count": 0,
                    "halfday_count": 0,
                }
            )

        # Employee sees ONLY their own record.
        employees = (
            Employee.objects
            .select_related(
                "department",
                "user"
            )
            .filter(
                pk=employee.pk,
                is_active=True
            )
        )

    # ======================================================
    # SEARCH
    # ======================================================

    if search:

        employees = employees.filter(
            Q(first_name__icontains=search)
            | Q(last_name__icontains=search)
            | Q(employee_id__icontains=search)
        )

    # ======================================================
    # DEPARTMENT FILTER
    # ======================================================

    if department:

        # Department IDs are now UUIDs.
        if _is_admin_or_hr(request.user):

            valid_department = Department.objects.filter(
                id=department,
                is_active=True
            ).exists()

            if valid_department:

                employees = employees.filter(
                    department_id=department
                )

            else:

                employees = employees.none()

        else:

            employees = employees.filter(
                department_id=department
            )

    # ======================================================
    # TODAY'S ATTENDANCE
    # ======================================================

    attendance_data = []

    for employee in employees:

        attendance = Attendance.objects.filter(
            employee=employee,
            date=today
        ).first()

        minimum_checkout = None

        if attendance and attendance.check_in:

            if attendance.status == "Present":

                minimum_checkout = (
                    datetime.combine(
                        attendance.date,
                        attendance.check_in
                    )
                    + timedelta(hours=7)
                ).time()

            elif attendance.status == "Half Day":

                minimum_checkout = (
                    datetime.combine(
                        attendance.date,
                        attendance.check_in
                    )
                    + timedelta(hours=3)
                ).time()

        attendance_data.append(
            {
                "employee": employee,
                "attendance": attendance,
                "minimum_checkout": minimum_checkout,
            }
        )

    # ======================================================
    # COUNTS
    # ======================================================

    if _is_admin_or_hr(request.user):

        present_count = Attendance.objects.filter(
            date=today,
            status="Present"
        ).count()

        halfday_count = Attendance.objects.filter(
            date=today,
            status="Half Day"
        ).count()

    else:

        employee = _get_logged_in_employee(
            request.user
        )

        if employee:

            present_count = Attendance.objects.filter(
                employee=employee,
                date=today,
                status="Present"
            ).count()

            halfday_count = Attendance.objects.filter(
                employee=employee,
                date=today,
                status="Half Day"
            ).count()

        else:

            present_count = 0
            halfday_count = 0

    # ======================================================
    # CONTEXT
    # ======================================================

    context = {
        "attendance_data": attendance_data,
        "departments": departments,
        "search": search,
        "selected_department": department,
        "selected_date": today,
        "present_count": present_count,
        "halfday_count": halfday_count,
    }

    return render(
        request,
        "attendance/attendance_list.html",
        context
    )


# ==========================================================
# ADD ATTENDANCE
# ==========================================================

@login_required
@role_required("ADMIN", "HR", "EMPLOYEE")
def add_attendance(request):

    today = timezone.localdate()

    employee = None

    # ======================================================
    # EMPLOYEE
    # ======================================================

    if _is_employee(request.user):

        employee = _get_logged_in_employee(
            request.user
        )

        if employee is None:

            messages.error(
                request,
                "Your employee profile has not been created yet."
            )

            return redirect(
                "attendance_list"
            )

        if not employee.is_active:

            messages.error(
                request,
                "Inactive employees cannot mark attendance."
            )

            return redirect(
                "attendance_list"
            )

    # ======================================================
    # POST
    # ======================================================

    if request.method == "POST":

        form = AttendanceForm(
            request.POST,
            current_user=request.user
        )

        if form.is_valid():

            selected_employee = form.cleaned_data.get(
                "employee"
            )

            # Employee can ONLY mark their own attendance.
            if _is_employee(request.user):

                if (
                    selected_employee is None
                    or selected_employee.pk != employee.pk
                ):

                    messages.error(
                        request,
                        "You can only mark attendance for yourself."
                    )

                    return redirect(
                        "attendance_list"
                    )

                selected_employee = employee

            else:

                if selected_employee is None:

                    messages.error(
                        request,
                        "Employee is required."
                    )

                    return redirect(
                        "attendance_list"
                    )

            if not selected_employee.is_active:

                messages.error(
                    request,
                    "Inactive employees cannot mark attendance."
                )

                return redirect(
                    "attendance_list"
                )

            # ==================================================
            # DUPLICATE CHECK
            # ==================================================

            existing = Attendance.objects.filter(
                employee=selected_employee,
                date=today
            ).first()

            if existing:

                messages.warning(
                    request,
                    "Attendance has already been marked for this employee today."
                )

                return redirect(
                    "attendance_list"
                )

            # ==================================================
            # SERVER LIVE TIME
            # ==================================================

            now = timezone.localtime()

            attendance = Attendance(
                employee=selected_employee,
                date=now.date(),
                check_in=now.time().replace(
                    second=0,
                    microsecond=0
                ),
                check_out=None,
                status=form.cleaned_data.get(
                    "status"
                ),
                working_hours=Decimal(
                    "0.00"
                ),
                remarks=form.cleaned_data.get(
                    "remarks"
                ),
                created_by=request.user,
                updated_by=request.user,
            )

            attendance.full_clean()
            attendance.save()

            messages.success(
                request,
                f"{selected_employee.first_name} checked in successfully at "
                f"{now.strftime('%I:%M %p')}."
            )

            return redirect(
                "attendance_list"
            )

    # ======================================================
    # GET
    # ======================================================

    else:

        initial = {
            "date": today,
            "status": "Present",
        }

        if employee:
            initial["employee"] = employee

        form = AttendanceForm(
            current_user=request.user,
            initial=initial
        )

    return render(
        request,
        "attendance/add_attendance.html",
        {
            "form": form
        }
    )


# ==========================================================
# EDIT ATTENDANCE
# ==========================================================

@login_required
@role_required("ADMIN", "HR", "EMPLOYEE")
def edit_attendance(request, pk):

    attendance = get_object_or_404(
        Attendance.objects.select_related(
            "employee",
            "employee__user"
        ),
        pk=pk
    )

    # ======================================================
    # EMPLOYEE OWNERSHIP CHECK
    # ======================================================

    if _is_employee(request.user):

        employee = _get_logged_in_employee(
            request.user
        )

        if employee is None:

            messages.error(
                request,
                "Your employee profile has not been created yet."
            )

            return redirect(
                "attendance_list"
            )

        if attendance.employee_id != employee.pk:

            messages.error(
                request,
                "You are not allowed to edit another employee's attendance."
            )

            return redirect(
                "attendance_list"
            )

    # ======================================================
    # POST
    # ======================================================

    if request.method == "POST":

        form = AttendanceForm(
            request.POST,
            instance=attendance,
            current_user=request.user
        )

        if form.is_valid():

            attendance.status = (
                form.cleaned_data.get(
                    "status"
                )
            )

            attendance.remarks = (
                form.cleaned_data.get(
                    "remarks"
                )
            )

            attendance.updated_by = request.user

            # Check-In and Check-Out remain server-controlled.

            if attendance.check_out:

                checkin_datetime = datetime.combine(
                    attendance.date,
                    attendance.check_in
                )

                checkout_datetime = datetime.combine(
                    attendance.date,
                    attendance.check_out
                )

                if attendance.check_out < attendance.check_in:

                    checkout_datetime += timedelta(
                        days=1
                    )

                duration = (
                    checkout_datetime
                    - checkin_datetime
                )

                attendance.working_hours = (
                    Decimal(
                        str(
                            duration.total_seconds()
                            / 3600
                        )
                    ).quantize(
                        Decimal("0.01")
                    )
                )

            attendance.full_clean()
            attendance.save()

            messages.success(
                request,
                "Attendance updated successfully."
            )

            return redirect(
                "attendance_list"
            )

    # ======================================================
    # GET
    # ======================================================

    else:

        form = AttendanceForm(
            instance=attendance,
            current_user=request.user
        )

    return render(
        request,
        "attendance/edit_attendance.html",
        {
            "form": form,
            "attendance": attendance,
        }
    )


# ==========================================================
# DELETE ATTENDANCE
# ==========================================================

@login_required
@role_required("ADMIN", "HR", "EMPLOYEE")
@require_POST
def delete_attendance(request, pk):

    attendance = get_object_or_404(
        Attendance,
        pk=pk
    )

    # ======================================================
    # EMPLOYEE OWNERSHIP CHECK
    # ======================================================

    if _is_employee(request.user):

        employee = _get_logged_in_employee(
            request.user
        )

        if employee is None:

            messages.error(
                request,
                "Your employee profile has not been created yet."
            )

            return redirect(
                "attendance_list"
            )

        if attendance.employee_id != employee.pk:

            messages.error(
                request,
                "You are not allowed to delete another employee's attendance."
            )

            return redirect(
                "attendance_list"
            )

    attendance.delete()

    messages.success(
        request,
        "Attendance deleted successfully."
    )

    return redirect(
        "attendance_list"
    )


# ==========================================================
# CHECK IN
# ==========================================================

@login_required
@role_required("ADMIN", "HR", "EMPLOYEE")
@require_POST
def check_in(request, employee_id):

    employee = get_object_or_404(
        Employee,
        id=employee_id,
        is_active=True
    )

    # ======================================================
    # EMPLOYEE OWNERSHIP CHECK
    # ======================================================

    if _is_employee(request.user):

        logged_in_employee = _get_logged_in_employee(
            request.user
        )

        if logged_in_employee is None:

            messages.error(
                request,
                "Your employee profile has not been created yet."
            )

            return redirect(
                "attendance_list"
            )

        if employee.pk != logged_in_employee.pk:

            messages.error(
                request,
                "You can only check in for yourself."
            )

            return redirect(
                "attendance_list"
            )

    today = timezone.localdate()

    # ======================================================
    # DUPLICATE CHECK
    # ======================================================

    existing = Attendance.objects.filter(
        employee=employee,
        date=today
    ).first()

    if existing:

        messages.warning(
            request,
            "Attendance has already been marked for today."
        )

        return redirect(
            "attendance_list"
        )

    # ======================================================
    # ACTUAL SERVER LIVE CHECK-IN TIME
    # ======================================================

    now = timezone.localtime()

    current_time = now.time().replace(
        second=0,
        microsecond=0
    )

    attendance = Attendance(
        employee=employee,
        date=today,
        check_in=current_time,
        check_out=None,
        status="Present",
        working_hours=Decimal(
            "0.00"
        ),
        created_by=request.user,
        updated_by=request.user,
    )

    attendance.full_clean()
    attendance.save()

    messages.success(
        request,
        f"{employee.first_name} checked in successfully at "
        f"{now.strftime('%I:%M %p')}."
    )

    return redirect(
        "attendance_list"
    )


# ==========================================================
# CHECK OUT
# ==========================================================

@login_required
@role_required("ADMIN", "HR", "EMPLOYEE")
@require_POST
def check_out(request, attendance_id):

    attendance = get_object_or_404(
        Attendance.objects.select_related(
            "employee",
            "employee__user"
        ),
        id=attendance_id
    )

    # ======================================================
    # EMPLOYEE OWNERSHIP CHECK
    # ======================================================

    if _is_employee(request.user):

        employee = _get_logged_in_employee(
            request.user
        )

        if employee is None:

            messages.error(
                request,
                "Your employee profile has not been created yet."
            )

            return redirect(
                "attendance_list"
            )

        if attendance.employee_id != employee.pk:

            messages.error(
                request,
                "You can only check out your own attendance."
            )

            return redirect(
                "attendance_list"
            )

    # ======================================================
    # ALREADY CHECKED OUT
    # ======================================================

    if attendance.check_out:

        messages.warning(
            request,
            "Already checked out."
        )

        return redirect(
            "attendance_list"
        )

    # ======================================================
    # CHECK-IN REQUIRED
    # ======================================================

    if not attendance.check_in:

        messages.error(
            request,
            "Cannot check out because Check-In time is missing."
        )

        return redirect(
            "attendance_list"
        )

    # ======================================================
    # ACTUAL SERVER LIVE CURRENT TIME
    # ======================================================

    now = timezone.localtime()

    current_datetime = now.replace(
        second=0,
        microsecond=0
    )

    checkin_datetime = timezone.make_aware(
        datetime.combine(
            attendance.date,
            attendance.check_in
        ),
        timezone.get_current_timezone()
    )

    # ======================================================
    # MINIMUM CHECKOUT
    # ======================================================

    if attendance.status == "Present":

        minimum_checkout = (
            checkin_datetime
            + timedelta(hours=7)
        )

    elif attendance.status == "Half Day":

        minimum_checkout = (
            checkin_datetime
            + timedelta(hours=3)
        )

    else:

        messages.error(
            request,
            "Invalid attendance status."
        )

        return redirect(
            "attendance_list"
        )

    # ======================================================
    # PREVENT EARLY CHECKOUT
    # ======================================================

    if current_datetime < minimum_checkout:

        remaining_seconds = (
            minimum_checkout
            - current_datetime
        ).total_seconds()

        remaining_minutes = int(
            (remaining_seconds + 59) // 60
        )

        minimum_time_display = (
            minimum_checkout.strftime(
                "%I:%M %p"
            )
        )

        required_hours = (
            "7"
            if attendance.status == "Present"
            else "3"
        )

        messages.error(
            request,
            f"Cannot check out yet. "
            f"{attendance.status} attendance requires "
            f"at least {required_hours} hours. "
            f"Earliest Check-Out is "
            f"{minimum_time_display}. "
            f"Please wait approximately "
            f"{remaining_minutes} minutes."
        )

        return redirect(
            "attendance_list"
        )

    # ======================================================
    # RECORD ACTUAL LIVE CHECKOUT TIME
    # ======================================================

    checkout_time = current_datetime.time()

    checkout_datetime = current_datetime

    duration = (
        checkout_datetime
        - checkin_datetime
    )

    total_hours = Decimal(
        str(
            duration.total_seconds()
            / 3600
        )
    )

    working_hours = total_hours.quantize(
        Decimal("0.01")
    )

    attendance.check_out = checkout_time
    attendance.working_hours = working_hours
    attendance.updated_by = request.user

    attendance.full_clean()
    attendance.save()

    messages.success(
        request,
        f"Checked out successfully at "
        f"{current_datetime.strftime('%I:%M %p')}. "
        f"Total working time: "
        f"{working_hours:.2f} hours."
    )

    return redirect(
        "attendance_list"
    )