
from django.contrib import messages
from django.db.models import Q
from django.db.models.deletion import ProtectedError
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)

from .forms import DepartmentForm
from .models import Department


# ==========================================================
# DEPARTMENT LIST
# ==========================================================

def department_list(request):

    departments = (
        Department.objects
        .prefetch_related("employees")
        .all()
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
            Q(description__icontains=search)

        )

    # ======================================================
    # CONTEXT
    # ======================================================

    context = {

        "departments": departments,

        "search": search,

        "total_departments": Department.objects.count(),

    }

    return render(
        request,
        "departments/department_list.html",
        context
    )


# ==========================================================
# ADD DEPARTMENT
# ==========================================================

def add_department(request):

    if request.method == "POST":

        form = DepartmentForm(
            request.POST
        )

        if form.is_valid():

            form.save()

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
# ==========================================================

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

            form.save()

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
# DELETE DEPARTMENT
# ==========================================================

def delete_department(request, pk):

    department = get_object_or_404(
        Department,
        pk=pk
    )

    if request.method == "POST":

        try:

            department.delete()

            messages.success(
                request,
                "Department deleted successfully."
            )

        except ProtectedError:

            messages.error(
                request,
                "This department cannot be deleted because employees are assigned to it."
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

