"""
This module provides a middleware that logs out authenticated users (excluding superusers)
after a certain period of inactivity. It checks the last login time of the user against the
current time and, if the elapsed time is greater than the specified AUTO_LOGOUT_DELAY in
settings.py, it logs the user out and redirects them to the login page.
"""

from django.conf import settings
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone


class AutoLogoutMiddleware:
    """
    Middleware that logs out a user (not an admin) if no requests have been received for a minute.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.user.is_authenticated and not request.user.is_superuser:
            current_time = timezone.now()
            if (current_time - request.user.last_login).total_seconds() < settings.AUTO_LOGOUT_DELAY:
                request.user.last_activity = current_time
            else:
                logout(request)
                return HttpResponseRedirect(reverse('login'))

            request.user.save()

        return response
