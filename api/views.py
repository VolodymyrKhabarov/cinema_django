"""
This module defines the view classes for handling HTTP requests in the API.
"""

from datetime import datetime, timedelta

from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import filters
from rest_framework import permissions
from rest_framework import status
from rest_framework import views
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.generics import CreateAPIView
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from api.filters import TodaySeanceFilterBackend, DateRangeFilterBackend
from api.permissions import FilmPermission, HallPermission, NoDeletePermission, TicketPermission
from mycinema.serializers import FilmSerializer, SeanceSerializer, TicketSerializer, HallSerializer
from mycinema.models import Film, Hall, Seance, Ticket
from users.serializers import UserSerializer


class FilmViewSet(ModelViewSet):
    """
    A viewset for creating and viewing film instances.
    """

    serializer_class = FilmSerializer
    queryset = Film.objects.all()
    permission_classes = [FilmPermission]

    def create(self, request, *args, **kwargs):
        """
        Creates a new film instance.

        Args:
            request: The HTTP request.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            A Response object with the serialized data and status code.
        """

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class HallViewSet(ModelViewSet):
    """
    A viewset for creating, viewing and editing hall instances.
    """
    queryset = Hall.objects.all()
    serializer_class = HallSerializer
    permission_classes = [HallPermission]

    def update(self, request, *args, **kwargs):
        """
        Update a hall instance if it's editable.

        Returns:
            Response: A JSON response containing the updated hall data if the instance is editable.
                        Otherwise, a response with an error message and HTTP status code 400.
        """

        instance = self.get_object()
        if not instance.is_editable:
            return Response({'detail': 'This hall cannot be edited.'},
                            status=status.HTTP_400_BAD_REQUEST)
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        """
        Partially update a hall instance if it's editable.

        Returns:
            Response: A JSON response containing the updated hall data if the instance is editable.
                        Otherwise, a response with an error message and HTTP status code 400.
        """

        instance = self.get_object()
        if not instance.is_editable:
            return Response({'detail': 'This hall cannot be edited.'},
                            status=status.HTTP_400_BAD_REQUEST)
        return super().partial_update(request, *args, **kwargs)


class SeanceViewSet(ModelViewSet):
    """
    A viewset for creating, viewing and editing seance instances.

    Attributes:
        queryset: A queryset containing all `Seance` instances.
        serializer_class: The serializer class used for this viewset.
        filter_backends: A tuple of filter backends used for filtering querysets.
        filterset_fields: A list of fields that are allowed to be filtered in the queryset.
        permission_classes: A list of permission classes used for this viewset.
        ordering_fields: A list of fields that can be used for ordering the queryset.

    Methods:
        get_permissions:
            Instantiates and returns the list of permissions that this view requires.
        create:
            Creates a new `Seance` instance for a specified range of dates.
        update:
            Updates an existing `Seance` instance, if it is editable.
        partial_update:
            Partially updates an existing `Seance` instance, if it is editable.
    """

    queryset = Seance.objects.all()
    serializer_class = SeanceSerializer
    filter_backends = (TodaySeanceFilterBackend, DateRangeFilterBackend, filters.OrderingFilter)
    filterset_fields = ['hall', 'start_time', 'end_time']

    ordering_fields = ['price', 'start_time']

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """

        if self.action == 'create':
            permission_classes = [permissions.IsAdminUser]
        elif self.action == 'partial_update':
            permission_classes = [permissions.IsAdminUser | permissions.DjangoObjectPermissions]
        elif self.action in ['list', 'retrieve']:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAdminUser]

        permission_classes.append(NoDeletePermission)

        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        """
        Creates a new `Seance` instance for a specified range of dates.

        Args:
            request: The HTTP request that triggered this view.
            args: Additional positional arguments.
            kwargs: Additional keyword arguments.

        Returns:
            A HTTP response with a status code of 201 CREATED if the request was successful,
            or a HTTP response with a status code of 400 BAD REQUEST if the request was unsuccessful.
        """

        start_iteration_date = request.data.get('start_iteration_date')
        if start_iteration_date is None:
            return Response(
                {'error': 'start_iteration_date cannot be empty'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            start_iteration_date = datetime.strptime(start_iteration_date, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'start_iteration_date must be in the format "YYYY-MM-DD"'},
                status=status.HTTP_400_BAD_REQUEST
            )

        end_iteration_date = request.data.get('end_iteration_date')
        if end_iteration_date is None:
            return Response(
                {'error': 'end_iteration_date cannot be empty'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            end_iteration_date = datetime.strptime(end_iteration_date, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'end_iteration_date must be in the format "YYYY-MM-DD"'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if end_iteration_date < start_iteration_date:
            return Response(
                {'error': 'end_iteration_date cannot be earlier than start_iteration_date'},
                status=status.HTTP_400_BAD_REQUEST
            )

        start_time = request.data.get('start_time')
        if not start_time:
            return Response(
                {'error': 'start_time cannot be empty'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            start_time = datetime.strptime(start_time, '%Y-%m-%dT%H:%M:%S')
        except ValueError:
            return Response(
                {'error': 'start_time should be in format %Y-%m-%dT%H:%M:%S'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if start_iteration_date != start_time.date():
            return Response(
                {'error': 'start_iteration_date must be equal to start_time'},
                status=status.HTTP_400_BAD_REQUEST
            )

        while start_iteration_date <= end_iteration_date:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            start_iteration_date += timedelta(days=1)
            request.data['start_time'] = (
                datetime.combine(start_iteration_date, serializer.validated_data['start_time'].time()))
            request.data['finish_time'] = (
                datetime.combine(start_iteration_date, serializer.validated_data['finish_time'].time()))
            serializer.validated_data['start_time'] = request.data['start_time']
            serializer.validated_data['finish_time'] = request.data['finish_time']

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        """
        Updates an existing `Seance` instance, if it is editable.

        Args:
            request: The HTTP request that triggered this view.
            args: Additional positional arguments.
            kwargs: Additional keyword arguments.

        Returns:
            A HTTP response with a status code of 200 OK if the request was successful,
            or a HTTP response with a status code of 400 BAD REQUEST if the request was unsuccessful.
        """

        instance = self.get_object()
        if not instance.is_editable:
            return Response(
                {'error': 'Cannot edit this seance'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if seance has not started yet
        if instance.start_time <= timezone.now():
            return Response(
                {'error': 'Cannot edit a past seance'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if there are no related tickets
        if instance.tickets.exists():
            return Response(
                {'error': 'Cannot edit a seance with sold tickets'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        """
        Partially updates an existing `Seance` instance, if it is editable.

        Args:
            request: The HTTP request that triggered this view.
            args: Additional positional arguments.
            kwargs: Additional keyword arguments.

        Returns:
            A HTTP response with a status code of 200 OK if the request was successful,
            or a HTTP response with a status code of 400 BAD REQUEST if the request was unsuccessful.
        """

        instance = self.get_object()
        if not instance.is_editable:
            return Response(
                {'error': 'Cannot edit this seance'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if seance has not started yet
        if instance.start_time <= timezone.now():
            return Response(
                {'error': 'Cannot edit a past seance'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if there are no related tickets
        if instance.tickets.exists():
            return Response(
                {'error': 'Cannot edit a seance with sold tickets'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return super().partial_update(request, *args, **kwargs)


class TicketViewSet(ModelViewSet):
    """
    A viewset for viewing Ticket instances.

    Methods:
    1. list(self, request) -> Response:
        Returns a list of Ticket instances that belong to the authenticated user.

    2. retrieve(self, request, pk=None) -> Response:
        Returns a single Ticket instance with the specified pk that belongs to the authenticated user.
    """

    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = (TicketPermission,)

    def list(self, request):
        """
        Returns a list of Ticket instances that belong to the authenticated user.
        """

        tickets = self.queryset.filter(user=request.user)
        serializer = self.serializer_class(tickets, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """
        Returns a single Ticket instance with the specified pk that belongs to the authenticated user.
        """

        ticket = get_object_or_404(self.queryset, pk=pk, user=request.user)
        serializer = self.serializer_class(ticket)
        return Response(serializer.data)


class UserCreateAPIView(CreateAPIView):
    """
    A view for creating new user accounts.

    Uses the UserSerializer to validate and create new user instances.
    """

    serializer_class = UserSerializer


class LogoutView(views.APIView):
    """
    API view to handle user logout by deleting their authentication token.
    """

    permission_classes = (IsAuthenticated,)

    def post(self, request):
        """
        Handle HTTP POST requests to logout the authenticated user.

        Deletes the user's authentication token, effectively logging them out.

        Returns:
            A Response object with an HTTP 200 OK status code.
        """

        request.user.auth_token.delete()
        return Response(status=status.HTTP_200_OK)


class LoginView(ObtainAuthToken):
    """
    Obtain an authentication token for a user.

    Extends the ObtainAuthToken view provided by Django REST framework
    to return a token key upon successful authentication.

    Request Parameters:
    - username (str): Required. The username of the user to authenticate.
    - password (str): Required. The password of the user to authenticate.

    Returns:
    - token (str): The authentication token for the authenticated user.

    Raises:
    - AuthenticationFailed: If the provided credentials are invalid or the user is inactive.
    """

    def post(self, request, *args, **kwargs):
        """
        Authenticate a user and return an authentication token.

        Args:
        - request (Request): The HTTP request object.

        Returns:
        - response (Response): The HTTP response object containing the authentication token.

        Raises:
        - AuthenticationFailed: If the provided credentials are invalid or the user is inactive.
        """

        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key}, status=status.HTTP_200_OK)


class ProfileView(APIView):
    """
    A view for retrieving the profile of the authenticated user.

    Only authenticated users can access this view.

    Methods:
    --------
    get(self, request):
        Retrieve the profile of the authenticated user.

    Attributes:
    -----------
    None
    """

    def get(self, request):
        """
        Retrieve the profile of the authenticated user.

        Parameters:
        -----------
        request: rest_framework.request.Request
            The HTTP request sent to the server.

        Returns:
        --------
        rest_framework.response.Response:
            A JSON response containing the serialized data of the authenticated user.
        """

        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)


class TodaySeanceView(ListAPIView):
    """
    API view to get all the seances scheduled for today
    """
    serializer_class = SeanceSerializer

    def get_queryset(self):
        """
        Get the queryset for the seances scheduled for today

        :return: Queryset containing the seances scheduled for today
        """
        now = timezone.now()
        return Seance.objects.filter(start_time__date=now.date())


class TomorrowSeanceView(ListAPIView):
    """
    API view to get all the seances scheduled for tomorrow
    """
    serializer_class = SeanceSerializer

    def get_queryset(self):
        """
        Get the queryset for the seances scheduled for tomorrow

        :return: Queryset containing the seances scheduled for tomorrow
        """
        tomorrow = timezone.now() + timezone.timedelta(days=1)
        return Seance.objects.filter(start_time__date=tomorrow.date())
