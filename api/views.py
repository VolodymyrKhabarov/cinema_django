"""
This module contains views for user authentication and authorization for the 'api' app in this Django project.
"""

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView
from rest_framework.authtoken.models import Token
from rest_framework import status
from rest_framework import views
from rest_framework.authtoken.views import ObtainAuthToken

from users.serializers import UserSerializer


class UserCreateAPIView(CreateAPIView):
    """
    View for creating a new user.

    This class-based view extends Django Rest Framework's `CreateAPIView` class and sets
    the serializer class to `UserSerializer`.

    Attributes:
        serializer_class (Serializer): The serializer class used to validate user data and
            create a new user.

    Methods:
        None
    """
    serializer_class = UserSerializer


class LogoutView(views.APIView):
    """
    View for user logout.

    This class-based view extends Django Rest Framework's `APIView` class and requires the
    user to be authenticated (`IsAuthenticated` permission class). When a user logs out,
    their authentication token is deleted from the database.

    Attributes:
        permission_classes (list): A list of permission classes that a user must satisfy in
            order to access this view. In this case, `IsAuthenticated`.

    Methods:
        post(request): Deletes the user's authentication token and returns a `HTTP_200_OK`
            response if the user is authenticated.
    """
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        """
        Delete the user's authentication token and return a `HTTP_200_OK` response if the
        user is authenticated.

        Args:
            request (HttpRequest): The HTTP request object.

        Returns:
            Response: A `HTTP_200_OK` response if the user is authenticated and their token
                is successfully deleted.

        Raises:
            None
        """
        request.user.auth_token.delete()
        return Response(status=status.HTTP_200_OK)


class LoginView(ObtainAuthToken):
    """
    View for user login.

    This class-based view extends Django Rest Framework's `ObtainAuthToken` class and allows
    users to log in with their username and password. If the login is successful, a new
    authentication token is generated and returned in the response.

    Attributes:
        None

    Methods:
        post(request, *args, **kwargs): Authenticate the user and return a response with
            the new authentication token if the login is successful.
    """
    def post(self, request, *args, **kwargs):
        """
        Authenticate the user and return a response with the new authentication token if
        the login is successful.

        Args:
            request (HttpRequest): The HTTP request object.
            args (tuple): Additional positional arguments.
            kwargs (dict): Additional keyword arguments.

        Returns:
            Response: A `HTTP_200_OK` response with the new authentication token if the
                login is successful.

        Raises:
            None
        """
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key}, status=status.HTTP_200_OK)
