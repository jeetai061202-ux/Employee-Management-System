from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)

from .decorators import role_required
from .forms import (
    AdminUserCreationForm,
    UserManagementForm,
)
from .models import User


# ==========================================================
# ROLE BASED REDIRECT
# ==========================================================

def redirect_by_role(user):

    if user.role and user.role.name == "Admin":
        return redirect("dashboard")

    elif user.role and user.role.name == "HR":
        return redirect("employee_list")

    elif user.role and user.role.name == "Employee":
        return redirect("employee_list")

    return redirect("login")


# ==========================================================
# LOGIN
# ==========================================================

def login_view(request):

    form = AuthenticationForm(
        request,
        data=request.POST or None
    )

    if request.method == "POST":

        if form.is_valid():

            user = form.get_user()

            login(
                request,
                user
            )

            messages.success(
                request,
                "Login successful. Welcome back!"
            )

            return redirect_by_role(user)

    return render(
        request,
        "accounts/login.html",
        {
            "form": form
        }
    )


# ==========================================================
# LOGOUT
# ==========================================================

@login_required
def logout_view(request):

    logout(request)

    messages.success(
        request,
        "You have been logged out successfully."
    )

    return redirect("login")


# ==========================================================
# TEST EMAIL
# ADMIN ONLY
# ==========================================================

@login_required
@role_required("ADMIN")
def test_email(request):

    send_mail(

        subject="Employee Management System",

        message=(
            "Congratulations! "
            "Email configuration is working."
        ),

        from_email=settings.DEFAULT_FROM_EMAIL,

        recipient_list=[
            settings.EMAIL_HOST_USER
        ],

        fail_silently=False,
    )

    return HttpResponse(
        "Email Sent Successfully!"
    )


# ==========================================================
# CREATE USER
# ADMIN ONLY
# ==========================================================

@login_required
@role_required("ADMIN")
def create_user(request):

    form = AdminUserCreationForm(
        request.POST or None
    )

    if form.is_valid():

        user = form.save()

        messages.success(
            request,
            (
                f"User '{user.username}' "
                "was created successfully."
            )
        )

        return redirect(
            "user_management"
        )

    return render(
        request,
        "accounts/create_user.html",
        {
            "form": form,
            "title": "Create User",
        }
    )


# ==========================================================
# ADMIN USER MANAGEMENT
# ADMIN ONLY
# ==========================================================

@login_required
@role_required("ADMIN")
def user_management(request):

    users = User.objects.select_related(
        "role"
    ).all().order_by(
        "username"
    )

    return render(
        request,
        "accounts/user_management.html",
        {
            "users": users
        }
    )


# ==========================================================
# EDIT USER ROLE / STATUS
# ADMIN ONLY
# ==========================================================

@login_required
@role_required("ADMIN")
def edit_user(request, user_id):

    user = get_object_or_404(
        User,
        id=user_id
    )

    form = UserManagementForm(
        request.POST or None,
        instance=user
    )

    if form.is_valid():

        updated_user = form.save()

        messages.success(
            request,
            (
                f"User '{updated_user.username}' "
                "was updated successfully."
            )
        )

        return redirect(
            "user_management"
        )

    return render(
        request,
        "accounts/user_form.html",
        {
            "form": form,
            "title": "Update User",
            "user_account": user,
        }
    )


# ==========================================================
# ACTIVATE / DEACTIVATE USER
# ADMIN ONLY
# ==========================================================

@login_required
@role_required("ADMIN")
def toggle_user_status(request, user_id):

    user = get_object_or_404(
        User,
        id=user_id
    )

    # ------------------------------------------------------
    # ADMIN CANNOT DEACTIVATE THEIR OWN ACCOUNT
    # ------------------------------------------------------

    if user == request.user:

        messages.error(
            request,
            "You cannot deactivate your own account."
        )

        return redirect(
            "user_management"
        )

    user.is_active = not user.is_active

    user.save(
        update_fields=["is_active"]
    )

    if user.is_active:

        messages.success(
            request,
            f"User '{user.username}' has been activated."
        )

    else:

        messages.success(
            request,
            f"User '{user.username}' has been deactivated."
        )

    return redirect(
        "user_management"
    )