"""
Module for registration users models
"""

from django.contrib import admin

from users.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """
    A Django ModelAdmin class that provides custom behavior for the User model in the admin interface
    """
    pass
