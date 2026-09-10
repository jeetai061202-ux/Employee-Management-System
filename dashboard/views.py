from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone

from employees.models import Employee
from attendance.models import Attendance
from departments.models import Department
from accounts.models import User

from accounts.decorators import role_required


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
        employee__is_active=True
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
        role="ADMIN"
    ).count()

    hr_users = User.objects.filter(
        role="HR"
    ).count()

    employee_users = User.objects.filter(
        role="EMPLOYEE"
    ).count()


    # ======================================================
    # DASHBOARD CONTEXT
    # ======================================================

    context = {

        # Existing dashboard data
        "total_employees": total_employees,

        "present_today": present_today,

        "absent_today": 15,

        "departments": total_departments,

        "pending_leave": 4,

        "monthly_salary": "₹8,50,000",


        # User management data
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
        context
    )