from functools import wraps

from django.http import HttpResponseForbidden
from django.shortcuts import redirect


def role_required(*allowed_roles):
    """
    Allow access only to users whose role is in allowed_roles.

    The application uses role codes such as:
        ADMIN
        HR
        EMPLOYEE

    The Role model stores readable names such as:
        Admin
        HR
        Employee

    This decorator supports the existing role codes while
    working with the new Role ForeignKey.
    """

    def decorator(view_func):

        @wraps(view_func)
        def wrapper(request, *args, **kwargs):

            # --------------------------------------------------
            # USER MUST BE LOGGED IN
            # --------------------------------------------------

            if not request.user.is_authenticated:
                return redirect("login")

            # --------------------------------------------------
            # USER MUST HAVE A ROLE
            # --------------------------------------------------

            if not request.user.role:
                return HttpResponseForbidden(
                    "Your account does not have a role assigned."
                )

            # --------------------------------------------------
            # GET ROLE NAME FROM ROLE TABLE
            # --------------------------------------------------

            user_role_name = request.user.role.name

            # --------------------------------------------------
            # SUPPORT EXISTING ROLE CODES
            # --------------------------------------------------

            role_mapping = {
                "ADMIN": "Admin",
                "HR": "HR",
                "EMPLOYEE": "Employee",
            }

            allowed_role_names = {
                role_mapping.get(
                    role,
                    role
                )
                for role in allowed_roles
            }

            # --------------------------------------------------
            # CHECK USER PERMISSION
            # --------------------------------------------------

            if user_role_name not in allowed_role_names:
                return HttpResponseForbidden(
                    "You do not have permission to access this page."
                )

            return view_func(
                request,
                *args,
                **kwargs
            )

        return wrapper

    return decorator