from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.core.mail import send_mail
from django.conf import settings

from .models import Leave
from .forms import LeaveForm


def leave_list(request):

    leaves = Leave.objects.select_related(
        "employee"
    ).all().order_by("-applied_on")

    search = request.GET.get("search")
    status = request.GET.get("status")

    if search:

        leaves = leaves.filter(

            Q(employee__first_name__icontains=search) |

            Q(employee__last_name__icontains=search) |

            Q(employee__employee_id__icontains=search)

        )

    if status:

        leaves = leaves.filter(
            status=status
        )

    context = {

        "leaves": leaves,

        "search": search,

        "status": status,

        "total": Leave.objects.count(),

        "pending": Leave.objects.filter(
            status="Pending"
        ).count(),

        "approved": Leave.objects.filter(
            status="Approved"
        ).count(),

        "rejected": Leave.objects.filter(
            status="Rejected"
        ).count(),

    }

    return render(
        request,
        "leave_management/leave_list.html",
        context
    )


def add_leave(request):

    if request.method == "POST":

        form = LeaveForm(request.POST)

        if form.is_valid():

            leave = form.save()

            messages.success(
                request,
                "Leave applied successfully."
            )

            return redirect("leave_list")

    else:

        form = LeaveForm()

    return render(
        request,
        "leave_management/add_leave.html",
        {
            "form": form
        }
    )


def edit_leave(request, pk):

    leave = get_object_or_404(
        Leave,
        pk=pk
    )

    if request.method == "POST":

        form = LeaveForm(
            request.POST,
            instance=leave
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Leave updated successfully."
            )

            return redirect("leave_list")

    else:

        form = LeaveForm(
            instance=leave
        )

    return render(
        request,
        "leave_management/edit_leave.html",
        {
            "form": form
        }
    )


def delete_leave(request, pk):

    leave = get_object_or_404(
        Leave,
        pk=pk
    )

    if request.method == "POST":

        leave.delete()

        messages.success(
            request,
            "Leave deleted successfully."
        )

        return redirect("leave_list")

    return render(
        request,
        "leave_management/delete_leave.html",
        {
            "leave": leave
        }
    )


# ==========================================================
# APPROVE LEAVE
# ==========================================================

def approve_leave(request, pk):

    leave = get_object_or_404(
        Leave,
        pk=pk
    )

    leave.status = "Approved"

    leave.save()

    # Send approval email
    if leave.employee.email:

        try:

            send_mail(

                subject="Leave Request Approved - Employee Management System",

                message=f"""
Dear {leave.employee.first_name},

Your leave request has been reviewed and approved.

Leave Details
----------------------------

Employee ID : {leave.employee.employee_id}

Leave Type  : {leave.leave_type}

Start Date  : {leave.start_date}

End Date    : {leave.end_date}

Reason      : {leave.reason}

Status      : APPROVED

Your leave has been approved by the HR department.

Regards,
HR Department
Employee Management System
                """,

                from_email=settings.DEFAULT_FROM_EMAIL,

                recipient_list=[
                    leave.employee.email
                ],

                fail_silently=True,

            )

        except Exception:

            pass

    messages.success(
        request,
        "Leave approved successfully and notification email sent."
    )

    return redirect("leave_list")


# ==========================================================
# REJECT LEAVE
# ==========================================================

def reject_leave(request, pk):

    leave = get_object_or_404(
        Leave,
        pk=pk
    )

    leave.status = "Rejected"

    leave.save()

    # Send rejection email
    if leave.employee.email:

        try:

            send_mail(

                subject="Leave Request Rejected - Employee Management System",

                message=f"""
Dear {leave.employee.first_name},

Your leave request has been reviewed.

Unfortunately, your leave request has been rejected.

Leave Details
----------------------------

Employee ID : {leave.employee.employee_id}

Leave Type  : {leave.leave_type}

Start Date  : {leave.start_date}

End Date    : {leave.end_date}

Reason      : {leave.reason}

Status      : REJECTED

Please contact the HR department if you require
further information regarding this decision.

Regards,
HR Department
Employee Management System
                """,

                from_email=settings.DEFAULT_FROM_EMAIL,

                recipient_list=[
                    leave.employee.email
                ],

                fail_silently=True,

            )

        except Exception:

            pass

    messages.success(
        request,
        "Leave rejected successfully and notification email sent."
    )

    return redirect("leave_list")