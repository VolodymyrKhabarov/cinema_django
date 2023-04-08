"""
This module defines the database models used for the user app.

It contains the User model which inherits from the Django built-in
AbstractUser model and adds additional fields like last_activity and wallet.
"""

from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser

from mycinema.models import Ticket


class User(AbstractUser):
    """
     A custom user model that extends the built-in Django AbstractUser model
    to add additional fields like wallet.

    Attributes:
        wallet (FloatField): The amount of money in the user's wallet.
    """

    wallet = models.FloatField(default=10000.00)

    class Meta:
        db_table = "User"

    @property
    def total_sum(self):
        """
        Calculates the amount spent on tickets by the user.

        Returns:
            float: The total sum spent on tickets by the user.
        """
        total_sum = 0
        tickets = Ticket.objects.filter(user=self)
        for ticket in tickets:
            total_sum += ticket.seance.price
        return total_sum

    def __str__(self):
        """
        Returns a string representation of the user object.

        Returns:
            str: The username of the user object.
        """
        return f"{self.username}"


class UserActivity(models.Model):
    """
    The UserActivity model represents the last activity of a user. It has two fields: user,
    which is a foreign key to the user model, and last_activity, which is a date and time field
    that automatically updates with the current date and time each time the model is saved.
    The __str__ method returns the username of the user associated with the model.

    This model can be used to track the last activity of users in an application, such as the last
    time they logged in or the last time they performed a specific action.
    """
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    last_activity = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}"
