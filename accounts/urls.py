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

    # ======================================================
    # ADMIN USER MANAGEMENT
    # ======================================================

    path(
        "users/",
        views.user_management,
        name="user_management",
    ),

    # ======================================================
    # ADMIN CREATE USER
    # ======================================================

    path(
        "users/create/",
        views.create_user,
        name="create_user",
    ),

    # ======================================================
    # EDIT USER ROLE / STATUS
    # ======================================================

    path(
        "users/<int:user_id>/edit/",
        views.edit_user,
        name="edit_user",
    ),

    # ======================================================
    # ACTIVATE / DEACTIVATE USER
    # ======================================================

    path(
        "users/<int:user_id>/toggle-status/",
        views.toggle_user_status,
        name="toggle_user_status",
    ),
]