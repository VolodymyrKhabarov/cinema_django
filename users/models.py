"""
This module defines the database models used for the user app.

It contains the User model which inherits from the Django built-in
AbstractUser model and adds additional fields like last_activity and wallet.
"""

from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    A custom user model that extends the built-in Django AbstractUser model
    to add additional fields like last_activity and wallet.

    Attributes:
        last_activity (DateTimeField): The date and time of the user's last activity.
        wallet (FloatField): The amount of money in the user's wallet.
    """

    last_activity = models.DateTimeField(auto_now=True)
    wallet = models.FloatField(default=10000.00)

    class Meta:
        db_table = "User"
