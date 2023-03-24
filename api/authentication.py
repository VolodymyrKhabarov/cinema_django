"""
This module contains custom authentication classes for the 'api' app in this Django project.
"""

from django.utils import timezone
from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication

from cinema.settings import DRF_AUTH_TOKEN_EXPIRATION_TIME


class TokenWithLifeTimeAuthentication(TokenAuthentication):
    """
    Custom token authentication class with token expiration.

    This class extends Django Rest Framework's `TokenAuthentication` class to add token
    expiration functionality. It checks if a token has expired by comparing the token's
    creation time with the current time, plus the expiration time defined in the project's
    settings. If the token has expired, it is deleted and an `AuthenticationFailed` exception
    is raised.

    Attributes:
        None

    Methods:
        authenticate_credentials(key): Authenticates the provided token key and returns
            the user and token if successful. Otherwise, raises an `AuthenticationFailed`
            exception with an appropriate error message.
    """
    def authenticate_credentials(self, key):
        """
        Authenticate the provided token key and return the user and token if successful.
        Otherwise, raise an `AuthenticationFailed` exception with an appropriate error message.

        Args:
            key (str): The authentication token key.

        Returns:
            tuple: A tuple containing the authenticated user and the token.

        Raises:
            AuthenticationFailed: If authentication fails, an `AuthenticationFailed` exception
                with an appropriate error message is raised.
        """
        user, token = super().authenticate_credentials(key=key)

        if (token.created + DRF_AUTH_TOKEN_EXPIRATION_TIME) < timezone.now():
            token.delete()
            raise exceptions.AuthenticationFailed("Token expired")

        return user, token
