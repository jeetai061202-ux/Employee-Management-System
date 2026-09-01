
from django.urls import path

from . import views


urlpatterns = [

    # ======================================================
    # LOGIN
    # ======================================================

    path(
        "login/",
        views.login_view,
        name="login",
    ),


    # ======================================================
    # REGISTER
    # ======================================================

    path(
        "register/",
        views.register_view,
        name="register",
    ),


    # ======================================================
    # LOGOUT
    # ======================================================

    path(
        "logout/",
        views.logout_view,
        name="logout",
    ),


    # ======================================================
    # TEST EMAIL
    # ======================================================

    path(
        "test-email/",
        views.test_email,
        name="test_email",
    ),

]

