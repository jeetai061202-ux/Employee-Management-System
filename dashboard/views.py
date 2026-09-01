from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone

from employees.models import Employee
from attendance.models import Attendance


@login_required
def dashboard(request):

    today = timezone.localdate()

    # ============================================================
    # TOTAL ACTIVE EMPLOYEES
    # ============================================================

    total_employees = Employee.objects.filter(
        is_active=True
    ).count()

    # ============================================================
    # PRESENT EMPLOYEES TODAY
    # ============================================================

    present_today = Attendance.objects.filter(
        date=today,
        status="Present",
        employee__is_active=True
    ).count()

    context = {

        # Actual number of active employees
        "total_employees": total_employees,

        # Actual number of employees present today
        "present_today": present_today,

        # Temporary values - we will connect these later
        "absent_today": 15,

        "departments": 8,

        "pending_leave": 4,

        "monthly_salary": "₹8,50,000",

    }

    return render(
        request,
        "dashboard/dashboard.html",
        context
    )