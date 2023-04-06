"""
This module provides a middleware that logs out authenticated users (excluding superusers)
after a certain period of inactivity. It checks the last login time of the user against the
current time and, if the elapsed time is greater than the specified AUTO_LOGOUT_DELAY in
settings.py, it logs the user out and redirects them to the login page.
"""

from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth import logout
from django.contrib.sessions.middleware import SessionMiddleware
from django.core.cache import cache
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin


class AutoLogoutMiddleware(MiddlewareMixin):
    """
    Middleware class for automatic user logout after a certain amount of inactivity.
    """

    def process_request(self, request):
        """
        Checks if the user is authenticated and not a staff member. If the user
        is authenticated and the last request time is greater than the allowed
        inactivity period, logs out the user.

        Args:
            request (HttpRequest): The current HTTP request object.

        Returns:
            None
        """
        if request.user.is_authenticated and not request.user.is_staff:
            last_activity = cache.get('last_request')
            if last_activity:
                if timezone.now() > (last_activity + settings.AUTO_LOGOUT_DELAY):
                    logout(request)
            cache.set('last_request', timezone.now())
