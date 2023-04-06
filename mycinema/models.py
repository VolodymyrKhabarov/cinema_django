"""
This module contains the Django models used for the mycinema application.

Models:

Hall: Represents a cinema hall with a name, number of rows, number of seats,
and a flag to indicate whether it can be edited.
Film: Represents a film with a title, description, release date, duration, and images.
Seance: Represents a screening of a film in a hall with a start and end time, price,
number of available seats, and a flag to indicate whether it can be edited.
Ticket: Represents a ticket purchased by a user for a specific seance, with a row and seat number.

Functions:

total_seats: A property of the Hall model that calculates the total number of seats in the hall.
get_duration: A function of the Film model that converts the duration of the film to minutes.
seat_list: A property of the Seance model that generates a list of seat numbers for display
in the template.
row_list: A property of the Seance model that generates a list of row numbers for display
in the template.

"""

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

USER_MODEL = settings.AUTH_USER_MODEL


class Hall(models.Model):
    """
    This class represents a movie theater hall with a name, number of rows, number of seats per row,
    and an editable flag. It also includes a method to calculate the total number of seats in the
    hall based on the number of rows and seats per row.
    """

    name = models.CharField(max_length=80, unique=True)
    row = models.IntegerField(validators=[MinValueValidator(1)])
    seat = models.IntegerField(validators=[MinValueValidator(1)])
    is_editable = models.BooleanField(default=True)

    class Meta:
        db_table = "Hall"

    @property
    def total_seats(self):
        """
        Returns the total number of seats in the hall by multiplying the number of rows
        and the number of seats per row.
        """
        total = self.row * self.seat
        return total

    def __str__(self):
        return f"{self.name}"


class Film(models.Model):
    """
    A class representing a film in the cinema.

    Attributes:
    - title (str): The title of the film.
    - description (str): The description of the film.
    - release_date (datetime.date): The date of release of the film.
    - film_duration (datetime.timedelta): The duration of the film.
    - image (str): The path to the image of the film.
    - image_title (str): The path to the image of the film's title.
    """

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    release_date = models.DateField()
    film_duration = models.DurationField()
    image = models.ImageField(blank=True, upload_to='')
    image_title = models.ImageField(blank=True, upload_to='')

    class Meta:
        db_table = "Film"
        ordering = ("title",)
        unique_together = (('title', 'release_date'),)

    def __str__(self):
        """
        Returns a string representation of the film, which is the film's title.
        """
        return f"{self.title}"


class Seance(models.Model):
    """
    The Seance class represents a movie screening in a particular hall.

    Attributes:
    - hall: a foreign key to the Hall model indicating which hall the seance is taking place in.
    - film: a foreign key to the Film model indicating which movie is being screened.
    - start_time: a DateTimeField indicating the start time of the seance.
    - finish_time: a DateTimeField indicating the finish time of the seance.
    - price: a DecimalField indicating the price of a ticket for the seance.
    - seats: an IntegerField indicating the number of seats available in the hall for this seance.
    - is_editable: a BooleanField indicating whether the seance can be edited.
    """

    hall = models.ForeignKey(Hall, on_delete=models.CASCADE)
    film = models.ForeignKey(Film, on_delete=models.CASCADE)
    start_time = models.DateTimeField(validators=[MinValueValidator(timezone.now())])
    finish_time = models.DateTimeField(blank=True, null=True, validators=[MinValueValidator(timezone.now())])
    price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    seats = models.IntegerField()
    is_editable = models.BooleanField(default=True)

    class Meta:
        db_table = "Seance"
        ordering = ('start_time',)
        permissions = [
            ("can_edit_seance", "Can edit seance"),
            ("can_edit_seance_partially", "Can partially edit seance"),
            ("can_view_seance", "Can view seance"),
            ("can_view_seance_list", "Can view seance list"),
        ]

    @property
    def seat_list(self):
        """Generating a list of seats to display in the template"""
        return [i for i in range(1, self.hall.seat + 1)]

    @property
    def row_list(self):
        """Generating a list of rows to display in the template"""
        return [i for i in range(1, self.hall.row + 1)]

    def save(self, *args, **kwargs):
        """
        Saves the seance instance to the database.
        If the seance is not yet saved, it sets the `seats` attribute to the total
        number of seats in the hall.
        """
        if self.pk is None:
            self.seats = self.hall.total_seats
            self.is_editable = True
        super().save(*args, **kwargs)

    def __str__(self):
        """
        Returns a string representation of the seance, consisting of the movie title and start time.
        """
        return f"{self.film.title} ({self.start_time.strftime('%H:%M')})"


class Ticket(models.Model):
    """
    Represents a ticket purchased by a user for a specific seance in a particular row and seat.

    Attributes:
        user (ForeignKey): A foreign key to the user who purchased the ticket.
        seance (ForeignKey): A foreign key to the seance for which the ticket was purchased.
        row (PositiveIntegerField): The row number in which the seat is located.
        seat (PositiveIntegerField): The seat number of the ticket.
        created_at (DateTimeField): The date and time when the ticket was created.

    Meta:
        db_table (str): The name of the database table to use for storing the model's data.
        unique_together (tuple): A tuple of fields that must be unique for each ticket,
        namely seat, row and seance.
    """

    user = models.ForeignKey(USER_MODEL, on_delete=models.CASCADE)
    seance = models.ForeignKey(Seance, on_delete=models.CASCADE, related_name='tickets')
    row = models.PositiveIntegerField()
    seat = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        db_table = "Ticket"
        """seats must be unique for one seance"""
        unique_together = ("seat", "row", "seance")

    def save(self, *args, **kwargs):
        """
        Save the ticket and update the number of available seats for the seance.

        If the ticket is saved for the first time, the number of seats for the seance is updated.

        Args:
            args: positional arguments passed to the parent method.
            kwargs: keyword arguments passed to the parent method.

        Returns:
            None.
        """
        seance = self.seance
        selected_seats_count = seance.tickets.count()
        seance.seats = seance.hall.total_seats - selected_seats_count
        seance.save()
        super().save(*args, **kwargs)

    def __str__(self):
        """
        Return the string representation of the Ticket instance.

        Returns:
            A string containing the film title, seance start time and ticket row and seat numbers.
        """
        return f"{self.seance.film} {self.seance.start_time}"
