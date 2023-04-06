"""
This module contains Django views used in the myCinema app.
"""

from datetime import date, datetime, timedelta
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DetailView, ListView, UpdateView
from mycinema import forms, models
from mycinema.models import Seance


class ProtectedTemplateView(UserPassesTestMixin):
    """
    A view that checks if the user is a superuser before allowing them to access a protected
    page. If the user is not a superuser, they will receive a 403 (Forbidden) error.
    """

    def test_func(self):
        """
        A function that checks whether the user is a superuser or not.

        Returns:
        --------
        bool:
            True if the user is a superuser, False otherwise.
        """
        return self.request.user.is_superuser

    def dispatch(self, request, *args, **kwargs):
        """
        Overrides the dispatch method to perform the user test before allowing access to the view.

        Parameters:
        -----------
        request : HttpRequest
            The request object.
        *args : list
            Arguments passed to the view.
        **kwargs : dict
            Keyword arguments passed to the view.

        Returns:
        --------
        super().dispatch(request, *args, **kwargs) : HttpResponse
            If the user is a superuser, the view is allowed to proceed.
            If the user is not a superuser, they receive a 403 (Forbidden) error.
        """
        if not self.test_func():
            return HttpResponseForbidden()
        return super().dispatch(request, *args, **kwargs)


class FilmCreateView(ProtectedTemplateView, CreateView):
    """
    View for creating a new film object. Inherits from ProtectedTemplateView
    to check if user is a superuser before allowing access to the view.
    Inherits from CreateView to provide form rendering and processing.
    """
    model = models.Film
    form_class = forms.FilmForm
    success_url = reverse_lazy('all_films')

    def form_valid(self, form):
        """
        Override the form_valid method to save the form data and create a new
        Film object. Displays a success message upon successful creation.
        """
        self.object = form.save(commit=False)
        self.object.save()
        messages.success(self.request, "Film was successfully created!")
        return super().form_valid(form)


class FilmDetailView(DetailView):
    """
    A Django DetailView that displays information about a specific Film object.

    Attributes:
        model: The Django model that this view displays. In this case, it's the `Film` model.
        template_name: The name of the template that will be used to render the view.

    Methods:
        get_context_data: Adds additional context to the view by finding the earliest and latest
        `Seance` objects associated with the `Film` and adding them to the context.

    Returns:
        The context dictionary to be used when rendering the template.
    """
    model = models.Film
    template_name = 'mycinema/film_by_id.html'

    def get_context_data(self, **kwargs):
        """
        Adds additional context to the view by finding the earliest and latest `Seance` objects
        associated with the `Film` and adding them to the context.

        Returns:
            The context dictionary to be used when rendering the template.
        """
        context = super().get_context_data(**kwargs)
        earliest_seance = Seance.objects.filter(film=self.object).order_by('start_time').first()
        latest_seance = Seance.objects.filter(film=self.object).order_by('-start_time').first()
        self.object.earliest_seance = earliest_seance
        self.object.latest_seance = latest_seance
        return context


class FilmListView(ListView):
    """
    A view that displays a list of all available films, with the earliest and latest
    showtimes for each film.

    Inherits from the built-in `ListView` class.

    Attributes:
        model: The model to use for this view (`Film`).
        ordering: The field(s) to use for ordering the films in the list (`release_date`).
        template_name: The name of the template to use for rendering the view
                (`mycinema/film_list.html`).
    """
    model = models.Film
    ordering = 'release_date'
    template_name = 'mycinema/film_list.html'

    def get_context_data(self, **kwargs):
        """
        Adds the earliest and latest showtimes for each film to the context.

        Returns:
            A dictionary containing the context data for the view.
        """
        context = super().get_context_data(**kwargs)
        for film in context['object_list']:
            earliest_seance = Seance.objects.filter(film=film).order_by('start_time').first()
            latest_seance = Seance.objects.filter(film=film).order_by('-start_time').first()
            film.earliest_seance = earliest_seance
            film.latest_seance = latest_seance
        return context


class SeancesTodayListView(ListView):
    """
    List of seances for today and tomorrow.

    Attributes:
        model: A Film model object.
        ordering: A string indicating the ordering of the films based on release date.
        template_name: A string representing the name of the template to render.
    """
    model = models.Film
    ordering = '-release_date'
    template_name = 'mycinema/seances_list.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        """
        Return the context data for the view.

        The context contains the set of films, the list of seances, the view date, the current
        date and time, the choice of showing seances for today or tomorrow, and the delta.

        Returns:
            A dictionary of values that will be available in the template context.
        """
        film = []
        """we get data from the user from the template (show the list of sessions for today or tomorrow)"""
        delta = self.kwargs.get('delta' or None)
        choice = 'today'
        if delta:
            choice = 'tomorrow'
            seances = Seance.objects.filter(
                start_time__range=(date.today() + timedelta(days=1),
                                   date.today() + timedelta(days=2)))
            view_date = date.today() + timedelta(days=1)
            for seance in seances:
                film.append(seance.film)
        else:
            seances = Seance.objects.filter(
                start_time__range=(date.today(),
                                   date.today() + timedelta(days=1)))
            for seance in seances:
                film.append(seance.film)
            view_date = date.today()
        today = datetime.now()
        context = super().get_context_data()
        """we make a set so that the films do not repeat"""
        film_list = set(film)
        context.update(dict(film_list=film_list, seances=seances, view_date=view_date,
                            today=today, delta=delta, choice=choice))
        return context


class HallCreateView(ProtectedTemplateView, CreateView):
    """
    View for creating a new Hall object. Subclasses ProtectedTemplateView
    to ensure that only superusers can create halls.
    """
    model = models.Hall
    form_class = forms.HallForm
    success_url = reverse_lazy('all_halls')

    def form_valid(self, form):
        """
        If the form is valid, save the Hall object and display a success message.
        """
        messages.success(self.request, "Hall was successfully created!")
        return super().form_valid(form)


class HallUpdateView(ProtectedTemplateView, UpdateView):
    """
    A view to update a hall instance in the database and redirect to the all_halls view.
    """

    model = models.Hall
    form_class = forms.HallForm
    success_url = reverse_lazy('all_halls')

    def form_valid(self, form):
        """
        Called when the form is successfully validated. Sends a success message and then calls
        the parent class' form_valid method.

        Args:
            form (HallForm): The validated form.

        Returns:
            HttpResponseRedirect: A response to redirect to the success URL.
        """
        messages.success(self.request, "Hall was successfully updated!")
        return super().form_valid(form)


class HallListView(ListView):
    """A view that displays a list of all halls in the system"""
    model = models.Hall
    queryset = models.Hall.objects.all()
    ordering = '-name'


class HallDetailView(DetailView):
    """
    A view that displays the details of a single hall, including lists of seat and row numbers
    for drawing in the template.
    """
    model = models.Hall
    template_name = 'mycinema/hall_by_id.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        """
        the get_context_data method is used to generate lists of seat and row numbers
        for the hall that will be displayed in the template.
        """
        hall = self.model.objects.get(id=self.kwargs['pk'])
        seats = [i for i in range(1, hall.seat + 1)]
        rows = [i for i in range(1, hall.row + 1)]
        context = super().get_context_data()
        context.update(dict(seats=seats, rows=rows))
        return context


class SeanceCreateView(ProtectedTemplateView, CreateView):
    """
    A view for creating a new seance, using a form to gather information from the user.
    """
    model = models.Seance
    form_class = forms.SeanceForm
    template_name = "mycinema/seance_form.html"
    success_url = reverse_lazy('all_seances')

    def form_valid(self, form):
        """
        Method called when form data is valid. It creates a new seance, adds a success message
        and returns the response.
        """
        messages.success(self.request, "Seance has been successfully created.")
        return super().form_valid(form)

    def get_success_url(self):
        """
        Returns the URL to redirect to when the form is successfully submitted.
        """
        return self.success_url


class SeanceUpdateView(ProtectedTemplateView, UpdateView):
    """
    A view that allows updating an existing movie screening (seance). Updates the finish time and
    the number of available seats according to the selected hall's total number of seats.
    """
    model = models.Seance
    form_class = forms.SeanceUpdateForm
    success_url = reverse_lazy('all_seances')

    def form_valid(self, form):
        """
        A method that sets the updated seance's finish time, number of seats, and saves
        the updated Seance instance. Returns a success message and calls the parent method to
        redirect to the success URL.
        """
        self.object = form.save(commit=False)

        film_duration = self.object.film.get_duration()
        end_time = self.object.start_time + timedelta(minutes=film_duration)
        self.object.finish_time = end_time

        self.object.seats = self.object.hall.total_seats
        self.object.save()
        messages.success(self.request, "Seance was successfully updated!")
        return super().form_valid(form)


class SeanceDetailView(DetailView):
    """
    A view that displays the details of a single seance and the tickets purchased for it.
    Allows authenticated users to buy tickets for the seance and deduct the ticket price from
    their wallet.
    """
    model = models.Seance
    template_name = 'mycinema/seance_by_id.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        """
        Get the data about the tickets purchased for this seance in order to draw the occupied seats
        """
        seance = self.model.objects.get(id=self.kwargs['pk'])
        tickets = models.Ticket.objects.filter(seance=seance)
        context = super().get_context_data()
        context.update(dict(tickets=tickets))
        return context

    def post(self, request, *args, **kwargs):
        """
        Allow authenticated users to buy tickets for the seance and deduct the ticket price
        from their wallet.
        """
        user = self.request.user
        if not user.is_authenticated:
            messages.warning(request, 'You need to login first to buy a ticket.')
            return redirect('login')

        seance_id = request.POST.get('seance_id')
        seance = models.Seance.objects.get(id=seance_id)
        ticket_price = seance.price
        selected_seats = []
        for key, value in request.POST.items():
            if key.startswith('seat'):
                row, seat = key.split('-')[-2:]
                selected_seats.append((int(row), int(seat)))

        total_price = ticket_price * len(selected_seats)

        if user.wallet < total_price:
            messages.error(request, 'Not enough funds in the wallet! Please recharge your account!')
            return redirect('seance_by_id', pk=self.kwargs['pk'])

        if seance.start_time < timezone.now():
            messages.error(request, 'Time is up! You can not buy ticket on this seance!')
        elif seance.seats == 0:
            messages.error(request, 'Sorry, all seats already taken! Pick another seance!')
        elif not selected_seats:
            messages.error(request, 'Please select a seat.')
        else:
            for row, seat in selected_seats:
                """check the seats marked by the user"""
                ticket_check = models.Ticket.objects.filter(seance=seance, row=row, seat=seat)
                if ticket_check:
                    """check if the selected seats are free"""
                    messages.error(request,
                                   'seat %s in row %s is already taken! Pick another one!'
                                   % (seat, row))
                else:
                    """if everything is OK, create the ticket and deduct the ticket price from user's wallet"""
                    ticket = models.Ticket(user=user, seance=seance, row=row, seat=seat)
                    ticket.save()
                    seance.seats -= 1
                    seance.save()
                    user.wallet = Decimal(str(user.wallet)) - ticket_price
                    user.save()
            messages.success(request, 'Congratulations! You have successfully purchased the tickets!')

        return redirect('seance_by_id', pk=self.kwargs['pk'])


class SeanceListView(ListView):
    """
    A view that lists all the seances in the database. It can be sorted by price, starting
    time or film's title.
    """
    model = models.Seance

    def get_context_data(self, *, object_list=None, **kwargs):
        """
        Get the context for this view.

        If a sorting option is provided in the URL, it sorts the seances accordingly.

        Returns:
            A dictionary with the context data for the template.
        """
        ordering = self.kwargs.get('ord' or None)
        choice = ''
        seance_list = models.Seance.objects.all().order_by('film__title')
        if ordering == 1:
            seance_list = models.Seance.objects.all().order_by('price')
            choice = 'Price: low to high'
        elif ordering == 2:
            seance_list = models.Seance.objects.all().order_by('-price')
            choice = 'Price: high to low'
        elif ordering == 3:
            seance_list = models.Seance.objects.all().order_by('start_time')
            choice = 'Beginning: low to high'
        elif ordering == 4:
            seance_list = models.Seance.objects.all().order_by('-start_time')
            choice = 'Beginning: high to low'
        context = super().get_context_data()
        context.update(dict(seance_list=seance_list, choice=choice))
        return context


class TicketListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """
    A view that displays the list of tickets purchased by the user, grouped by seance.

    Attributes:
        model (class): The model that the view will display.
        ordering (list): A list of ordering fields that will be used to order the queryset.
        login_url (str): The URL where users will be redirected to login.
        redirect_field_name (str): The name of the redirect field.

    Methods:
        get_context_data(**kwargs): Overrides the default get_context_data method
        to add extra context data.
    """
    model = models.Ticket
    ordering = ['seance__film__title']
    login_url = 'login'
    redirect_field_name = 'next'

    def get_context_data(self, **kwargs):
        """
        Overrides the default get_context_data method to add extra context data.

        Args:
            **kwargs: A dictionary of context data.

        Returns:
            dict: A dictionary containing the context data that will be used to render the view.
        """
        tickets = models.Ticket.objects.all()
        user = self.request.user
        seances = []
        for ticket in tickets:
            if ticket.user == user:
                seances.append(models.Seance.objects.get(id=ticket.seance.id))
        seance_list = set(seances)
        context = super().get_context_data(**kwargs)
        context.update(dict(seance_list=seance_list))
        return context

    def test_func(self):
        """
        Check whether the user is authorized to access the view.

        Returns:
            bool: True if the user is authorized, False otherwise.
        """
        return not self.request.user.is_superuser


class TicketDetailView(LoginRequiredMixin, DetailView):
    """
    This class-based view displays a detailed view of a single ticket object.
    It inherits from Django's DetailView class and adds login required functionality.
    """
    model = models.Ticket
    template_name = 'mycinema/ticket_by_id.html'
    login_url = 'login'
    redirect_field_name = 'next'

    def get_queryset(self):
        """
        This method returns the queryset of tickets that should be displayed in the view.
        It filters the tickets by the current user and returns only the ticket with the id specified in the URL.

        Returns:
            A queryset of tickets.
        """
        queryset = super().get_queryset()
        return queryset.filter(user=self.request.user, id=self.kwargs['pk'])

