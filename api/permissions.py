"""
Module for custom permissions.

"""

from rest_framework import permissions
from rest_framework.permissions import BasePermission, SAFE_METHODS


class NoDeletePermission(permissions.BasePermission):
    """
    Custom permission class that denies DELETE requests for all users.
    """

    def has_permission(self, request, view):
        """
        Check if the user is allowed to perform the requested action.

        Parameters:
        -----------
        request: Request object
            The incoming request.
        view: View object
            The view that the request was made to.

        Returns:
        --------
        bool:
            True if the request method is not DELETE, else False.
        """
        return request.method != 'DELETE'


class FilmPermission(BasePermission):
    """
    Custom permission class that allows staff users to create new Film objects.

    This permission class only allows GET, HEAD, and OPTIONS requests to be performed by any user,
    while POST requests are only allowed for staff users.

    Additionally, object-level permissions are not implemented, so only safe methods can be performed
    on individual Film instances.

    """

    def has_permission(self, request, view):
        """
        Check if the user is allowed to perform the requested action.

        Parameters:
        -----------
        request: Request object
            The incoming request.
        view: View object
            The view that the request was made to.

        Returns:
        --------
        bool:
            True if the request method is safe (GET, HEAD, or OPTIONS), or if it's a POST request and the
            user is a staff member, else False.
        """

        if request.method in SAFE_METHODS:
            return True
        elif request.method == 'POST' and request.user.is_staff:
            return True
        else:
            return False

    def has_object_permission(self, request, view, obj):
        """
        Check if the user is allowed to perform the requested action on a Film object.

        Since object-level permissions are not implemented, only safe methods can be performed
        on individual Film instances.

        Parameters:
        -----------
        request: Request object
            The incoming request.
        view: View object
            The view that the request was made to.
        obj: Film object
            The Film instance being accessed.

        Returns:
        --------
        bool:
            True if the request method is safe (GET, HEAD, or OPTIONS), else False.
        """

        if request.method in SAFE_METHODS:
            return True
        else:
            return False


class HallPermission(BasePermission):
    """
    Permissions for cinema halls.

    Only superusers are allowed to create or modify cinema halls.
    """

    def has_permission(self, request, view):
        """
        Return True if the user has permission to access the view.

        Allow all users to access the view for GET, HEAD or OPTIONS methods.
        """
        if request.method in SAFE_METHODS:
            return True

        # Allow only admin to create or modify cinema halls.
        return request.user.is_superuser and request.method not in ['DELETE']


class TicketPermission(BasePermission):
    """
    Permissions for tickets.

    Only authenticated non-superuser users are allowed to access the view.
    """

    def has_permission(self, request, view):
        """
        Return True if the user has permission to access the view.
        """
        if request.user.is_authenticated and not request.user.is_superuser:
            return True
        return False
