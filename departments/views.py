from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)

from accounts.decorators import role_required

from .forms import DepartmentForm
from .models import Department


# ==========================================================
# DEPARTMENT LIST
# ADMIN + HR + EMPLOYEE
# ==========================================================

@login_required
@role_required("ADMIN", "HR", "EMPLOYEE")
def department_list(request):

    # ======================================================
    # SHOW ONLY ACTIVE DEPARTMENTS
    # ======================================================

    departments = (
        Department.objects
        .filter(is_active=True)
        .prefetch_related("employees")
        .order_by("name")
    )

    search = request.GET.get(
        "search",
        ""
    ).strip()

    # ======================================================
    # SEARCH
    # ======================================================

    if search:

        departments = departments.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search) |
            Q(code__icontains=search)
        )

    # ======================================================
    # CONTEXT
    # ======================================================

    context = {
        "departments": departments,
        "search": search,

        "total_departments": Department.objects.filter(
            is_active=True
        ).count(),
    }

    return render(
        request,
        "departments/department_list.html",
        context
    )


# ==========================================================
# ADD DEPARTMENT
# ADMIN + HR + EMPLOYEE
# ==========================================================

@login_required
@role_required("ADMIN", "HR", "EMPLOYEE")
def add_department(request):

    if request.method == "POST":

        form = DepartmentForm(
            request.POST
        )

        if form.is_valid():

            department = form.save(
                commit=False
            )

            # New departments are active.
            department.is_active = True

            # Audit information.
            department.created_by = request.user
            department.updated_by = request.user

            department.save()

            messages.success(
                request,
                "Department added successfully."
            )

            return redirect(
                "department_list"
            )

    else:

        form = DepartmentForm()

    return render(
        request,
        "departments/add_department.html",
        {
            "form": form
        }
    )


# ==========================================================
# EDIT DEPARTMENT
# ADMIN + HR + EMPLOYEE
# ==========================================================

@login_required
@role_required("ADMIN", "HR", "EMPLOYEE")
def edit_department(request, pk):

    department = get_object_or_404(
        Department,
        pk=pk
    )

    if request.method == "POST":

        form = DepartmentForm(
            request.POST,
            instance=department
        )

        if form.is_valid():

            department = form.save(
                commit=False
            )

            # Audit information.
            department.updated_by = request.user

            department.save()

            messages.success(
                request,
                "Department updated successfully."
            )

            return redirect(
                "department_list"
            )

    else:

        form = DepartmentForm(
            instance=department
        )

    return render(
        request,
        "departments/edit_department.html",
        {
            "form": form,
            "department": department,
        }
    )


# ==========================================================
# DELETE DEPARTMENT - SOFT DELETE
# ADMIN + HR + EMPLOYEE
# ==========================================================

@login_required
@role_required("ADMIN", "HR", "EMPLOYEE")
def delete_department(request, pk):

    department = get_object_or_404(
        Department,
        pk=pk
    )

    if request.method == "POST":

        # ==================================================
        # SOFT DELETE
        # ==================================================
        # Do NOT permanently delete the department.
        #
        # The department remains in the database.
        #
        # True -> False
        #
        # This preserves historical department information.
        # ==================================================

        department.is_active = False
        department.updated_by = request.user

        department.save(
            update_fields=[
                "is_active",
                "updated_by",
                "updated_at",
            ]
        )

        messages.success(
            request,
            "Department deleted successfully."
        )

        return redirect(
            "department_list"
        )

    return render(
        request,
        "departments/delete_department.html",
        {
            "department": department,
        }
    )