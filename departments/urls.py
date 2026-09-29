from django.urls import path

from . import views


urlpatterns = [

    # ==========================================================
    # DEPARTMENT LIST
    # ==========================================================

    path(
        "",
        views.department_list,
        name="department_list"
    ),

    # ==========================================================
    # ADD DEPARTMENT
    # ==========================================================

    path(
        "add/",
        views.add_department,
        name="add_department"
    ),

    # ==========================================================
    # EDIT DEPARTMENT
    # ==========================================================

    path(
        "edit/<uuid:pk>/",
        views.edit_department,
        name="edit_department"
    ),

    # ==========================================================
    # DELETE DEPARTMENT - SOFT DELETE
    # ==========================================================

    path(
        "delete/<uuid:pk>/",
        views.delete_department,
        name="delete_department"
    ),

]