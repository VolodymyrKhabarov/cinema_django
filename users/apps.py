"""
Apps module is used to provide configuration for the users app within the Django project.
"""

from django.apps import AppConfig


class UsersConfig(AppConfig):
    """
    The UsersConfig class is defined to configure the settings for the users app.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
