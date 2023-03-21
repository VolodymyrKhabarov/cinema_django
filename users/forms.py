"""
This module is used for the cinema site's registration and authentication system,
it allows users to create a new account on the site.
"""

from django.contrib.auth.forms import UserCreationForm

from users.models import User


class SignUpForm(UserCreationForm):
    """
    A form for user registration.

    Extends Django's built-in "UserCreationForm".
    The form takes the user's username, email, password and password confirmation as input.
    """

    class Meta:
        """
        Class Meta is used to specify metadata.
        """
        model = User
        fields = ["username", "email", "password1", "password2"]
