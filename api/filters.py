"""
This module contains custom filter backends for Django REST Framework.

The backends included in this module are:

- TodaySeanceFilterBackend: A filter backend that filters seances by the ones that occur today.
- DateRangeFilterBackend: A filter backend that filters seances by a date range.

"""

from datetime import datetime, date, time, timedelta
from django_filters import rest_framework as filters
from rest_framework.filters import BaseFilterBackend


class TodaySeanceFilterBackend(BaseFilterBackend):
    """
    A filter backend that filters seances by the ones that occur today.

    This filter backend retrieves the seances that occur on the current date. It does this by
    comparing the date of the seance with the current date. If a seance's date is equal to the current
    date, then it is included in the queryset.

    Attributes:
        None

    Methods:
        filter_queryset(request, queryset, view): Filters the queryset based on the query parameters
            provided in the request object. Returns the filtered queryset.
    """

    def filter_queryset(self, request, queryset, view):
        """
            Filters the queryset based on the query parameters provided in the request object.
            Returns the filtered queryset.

            Args:
                request (Request): The request object containing the query parameters.
                queryset (QuerySet): The queryset to filter.
                view (APIView): The view class that called the filter.

            Returns:
                QuerySet: The filtered queryset.
            """

        today = date.today()
        start_time__gte = datetime.combine(today, datetime.min.time())
        start_time__lte = datetime.combine(today, datetime.max.time())

        hall = request.query_params.get('hall')
        start_time = request.query_params.get('start_time')
        end_time = request.query_params.get('end_time')

        if hall:
            queryset = queryset.filter(hall=hall)

        if start_time and end_time:
            start_time = datetime.strptime(start_time, '%Y-%m-%dT%H:%M:%S')
            end_time = datetime.strptime(end_time, '%Y-%m-%dT%H:%M:%S')
            queryset = queryset.filter(start_time__range=(start_time, end_time))

        if start_time and not end_time:
            start_time_exact = datetime.strptime(start_time, '%Y-%m-%dT%H:%M:%S')
            queryset = queryset.filter(
                start_time__gte=start_time__gte,
                start_time__lte=start_time__lte,
                start_time__time__gte=start_time_exact.time()
            )

        return queryset


class DateRangeFilterBackend(BaseFilterBackend):
    """
    A filter backend that filters seances by a date range.

    This filter backend retrieves the seances that occur between two dates. It does this by
    filtering the queryset by the start_time that is greater than or equal to the start_time__gte
    parameter and less than or equal to the start_time__lte parameter.

    Attributes:
        None

    Methods:
        filter_queryset(request, queryset, view): Filters the queryset based on the query parameters
            provided in the request object. Returns the filtered queryset.
    """

    def filter_queryset(self, request, queryset, view):
        """
        Filters the queryset based on the query parameters provided in the request object.
        Returns the filtered queryset.

        Args:
            request (Request): The request object containing the query parameters.
            queryset (QuerySet): The queryset to filter.
            view (APIView): The view class that called the filter.

        Returns:
            QuerySet: The filtered queryset.
        """

        start_time__gte = request.query_params.get('start_time__gte')
        start_time__lte = request.query_params.get('start_time__lte')

        if start_time__gte and start_time__lte:
            start_time__gte = datetime.strptime(start_time__gte, '%Y-%m-%dT%H:%M:%S')
            start_time__lte = datetime.strptime(start_time__lte, '%Y-%m-%dT%H:%M:%S')
            queryset = queryset.filter(start_time__gte=start_time__gte, start_time__lte=start_time__lte)

        return queryset
