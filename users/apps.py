"""
Apps module is used to provide configuration for the users app within the Django project.
"""

from django.apps import AppConfig


class UserConfig(AppConfig):
    """
    The UsersConfig class is defined to configure the settings for the users app.
    """
    name = 'users'
