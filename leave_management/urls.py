from django.urls import path

from . import views

urlpatterns = [

    path("", views.leave_list, name="leave_list"),

    path("add/", views.add_leave, name="add_leave"),

    path("edit/<int:pk>/", views.edit_leave, name="edit_leave"),

    path("delete/<int:pk>/", views.delete_leave, name="delete_leave"),

    path("approve/<int:pk>/", views.approve_leave, name="approve_leave"),

    path("reject/<int:pk>/", views.reject_leave, name="reject_leave"),

]