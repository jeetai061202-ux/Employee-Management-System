
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import render, redirect

from .forms import RegisterForm


# ==========================================================
# REGISTER
# ==========================================================

def register_view(request):

    form = RegisterForm(
        request.POST or None
    )

    if form.is_valid():

        user = form.save()

        login(
            request,
            user
        )

        return redirect(
            "dashboard"
        )

    return render(

        request,

        "accounts/register.html",

        {
            "form": form
        }

    )


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

            login(

                request,

                form.get_user()

            )

            messages.success(

                request,

                "Login successful. Welcome back!"

            )

            return redirect(
                "dashboard"
            )

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

def logout_view(request):

    logout(request)

    messages.success(

        request,

        "You have been logged out successfully."

    )

    return redirect(
        "login"
    )


# ==========================================================
# TEST EMAIL
# ==========================================================

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

