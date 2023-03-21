"""
This module defines the URL patterns for the users app.
"""

from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from users.views import SignUpView, ProfileView

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('signin/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),
]
