"""
Configuration module for the 'api' app in this Django project.
This module defines the `ApiConfig` class which extends Django's `AppConfig` class.

"""

from django.apps import AppConfig


class ApiConfig(AppConfig):
    """
    The `ApiConfig` class specifies the app's default auto field as `BigAutoField`, and
    sets the name of the app as 'api'.

    Attributes:
    default_auto_field (str): The default auto field for the app. In this case, it is 'django.db.models.BigAutoField'.
    name (str): The name of the app. In this case, it is 'api'.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'
