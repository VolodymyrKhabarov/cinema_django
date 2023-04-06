"""
Module for custom middleware classes used in the mycinema app.

"""
from django.db.models import Count, Sum
from django.utils import timezone

from mycinema import models


class SeanceNotEditable:
    """
    Middleware class to set 'is_editable' attribute of the seances that are no longer editable.
    Checks whether a seance has already started or all seats have been reserved and sets
    'is_editable' attribute to False accordingly.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request, *args, **kwargs):
        """
        Method called for each request to set 'is_editable' attribute of the seances that are no longer editable.

        Args:
            request: The request object.
            *args: Additional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            The response object.
        """
        if request.user.is_superuser:
            seances = models.Seance.objects.filter(is_editable=True)
            for seance in seances:
                if seance.seats < seance.hall.total_seats or seance.start_time < timezone.now():
                    seance.is_editable = False
                    seance.save()
        response = self.get_response(request)
        return response


class HallEditableMiddleware:
    """
    Middleware class to set 'is_editable' attribute of the halls that are no longer editable.
    Checks whether a hall has at least one seance and whether all of its seats have been reserved,
    and sets 'is_editable' attribute to False accordingly.

    Args:
        get_response (callable): A callable that takes a request and returns a response.

    Attributes:
        get_response (callable): A callable that takes a request and returns a response.

    Methods:
        __call__(self, request): Processes the request and sets the 'is_editable' attribute
            of the halls that are no longer editable. Returns the response object.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        """
        Processes the request and sets the 'is_editable' attribute of the halls that are no longer editable.

        Args:
            request (HttpRequest): The request object.

        Returns:
            HttpResponse: The response object.
        """
        halls = models.Hall.objects.all()

        for hall in halls:
            if hall.is_editable:
                seances_count = models.Seance.objects.filter(hall=hall).count()
                tickets_count = models.Seance.objects.filter(hall=hall) \
                    .annotate(num_tickets=Count('tickets')) \
                    .aggregate(total_tickets=Sum('num_tickets'))['total_tickets']
                if seances_count > 0 and tickets_count > 0:
                    hall.is_editable = False
                    hall.save()

        response = self.get_response(request)
        return response
