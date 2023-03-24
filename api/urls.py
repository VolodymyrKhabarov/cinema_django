"""
API application URL Configuration
"""

from django.urls import path

from api.views import UserCreateAPIView, LogoutView, LoginView


urlpatterns = [
    path('api/signup/', UserCreateAPIView.as_view(), name='signup'),
    path('api/signin/', LoginView.as_view(), name='login'),
    path('api/logout/', LogoutView.as_view(), name='logout')
]
