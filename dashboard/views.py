from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone

from accounts.decorators import role_required
from accounts.models import User
from attendance.models import Attendance
from departments.models import Department
from employees.models import Employee


@login_required
@role_required("ADMIN", "HR", "EMPLOYEE")
def dashboard(request):

    # ======================================================
    # TODAY
    # ======================================================

    today = timezone.localdate()

    # ======================================================
    # EMPLOYEE DATA
    # ======================================================

    total_employees = Employee.objects.filter(
        is_active=True
    ).count()

    # ======================================================
    # ATTENDANCE DATA
    # ======================================================

    present_today = Attendance.objects.filter(
        date=today,
        status="Present",
        employee__is_active=True,
    ).count()

    # ======================================================
    # DEPARTMENT DATA
    # ======================================================

    total_departments = Department.objects.filter(
        is_active=True
    ).count()

    # ======================================================
    # USER / ROLE DATA
    # ======================================================

    total_users = User.objects.count()

    admin_users = User.objects.filter(
        role__name="Admin"
    ).count()

    hr_users = User.objects.filter(
        role__name="HR"
    ).count()

    employee_users = User.objects.filter(
        role__name="Employee"
    ).count()

    # ======================================================
    # DASHBOARD CONTEXT
    # ======================================================

    context = {
        "total_employees": total_employees,
        "present_today": present_today,
        "absent_today": 15,
        "departments": total_departments,
        "pending_leave": 4,
        "monthly_salary": "₹8,50,000",

        "total_users": total_users,
        "admin_users": admin_users,
        "hr_users": hr_users,
        "employee_users": employee_users,
    }

    # ======================================================
    # RENDER DASHBOARD
    # ======================================================

    return render(
        request,
        "dashboard/dashboard.html",
        context,
    )