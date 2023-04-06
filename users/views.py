"""
Module for handling user views.

This module contains views for handling user signup and profile pages.
"""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, TemplateView
from django.urls import reverse_lazy

from users.forms import SignUpForm


SUCCESS_REGISTRATION_MSG = "You have successfully registered!"


class SignUpView(CreateView):
    """
    View for user signup.

    Allows new users to register with the site using the SignUpForm form.
    On successful registration, redirects the user to the login page and displays a success message.

    Attributes:
        form_class (SignUpForm): The form class used for user registration.
        success_url (str): The URL to redirect to on successful registration.
        template_name (str): The name of the template to use for the signup page.

    Methods:
        form_valid(form): Called when the form is successfully validated. Saves the form data, adds
         a success message to the request, and redirects the user to the success URL.
    """

    form_class = SignUpForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"

    def form_valid(self, form):
        """
        Called when the form is successfully validated.

        Args:
            form (SignUpForm): The validated form.

        Returns:
            super().form_valid(form) (HttpResponse): A redirect to the success URL.
        """
        messages.success(self.request, SUCCESS_REGISTRATION_MSG)
        return super().form_valid(form)


class ProfileView(LoginRequiredMixin, TemplateView):
    """
    View for user profile page.

    Displays the user's profile page.

    Attributes:
        template_name (str): The name of the template to use for the profile page.
    """

    template_name = 'registration/profile.html'
    login_url = 'login'
    redirect_field_name = 'next'
