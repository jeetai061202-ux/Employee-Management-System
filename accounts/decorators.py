from functools import wraps

from django.http import HttpResponseForbidden
from django.shortcuts import redirect


def role_required(*allowed_roles):
    """
    Allow access only to users whose role is in allowed_roles.
    """

    def decorator(view_func):

        @wraps(view_func)
        def wrapper(request, *args, **kwargs):

            # User must be logged in
            if not request.user.is_authenticated:
                return redirect("login")

            # Check user's role
            if request.user.role not in allowed_roles:
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