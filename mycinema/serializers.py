"""
This module contains Django REST Framework serializers for the models in the "mycinema" app,
which represent cinemas, films, halls, seances, and tickets.
"""
from datetime import timedelta

from django.core.validators import MinValueValidator
from django.utils import timezone
from django.utils.translation import gettext as _
from rest_framework import serializers

from mycinema import models


class HallSerializer(serializers.ModelSerializer):
    """
    Serializer class for the Hall model.

    Provides serialization and deserialization of Hall instances, as well as read-only
    access to the total_seats field.

    Attributes:
        total_seats (serializers.IntegerField): A read-only integer field representing
            the total number of seats in the hall.
    """
    total_seats = serializers.IntegerField(read_only=True)

    class Meta:
        """
        Meta class defining model and fields for serialization.
        """
        model = models.Hall
        fields = '__all__'
        read_only_fields = ['is_editable']


class FilmSerializer(serializers.ModelSerializer):
    """
    Serializer class for Film model.
    """
    film_duration = serializers.CharField(help_text='minutes')
    seance_start_time = serializers.SerializerMethodField()
    seance_finish_time = serializers.SerializerMethodField()

    class Meta:
        """
        Meta class defining model and fields for serialization.
        """
        model = models.Film
        fields = '__all__'

    def validate_film_duration(self, value):
        """
        Custom validation method for the film_duration field. Converts the duration
        to an integer, checks whether it's a positive number, and raises a ValidationError
        if not. Returns the duration as a string.

        Raises:
            ValidationError: If the duration is not a valid positive integer.

        Returns:
            str: The duration as a string.
        """
        try:
            duration = int(value)
            if duration <= 0:
                raise serializers.ValidationError('Duration must be a positive integer.')
        except ValueError:
            raise serializers.ValidationError('Duration must be a positive integer.')
        return str(duration)

    def create(self, validated_data):
        """
        Creates a Film instance with validated data, converting the film duration from minutes
        to a timedelta.

        Args:
            validated_data (dict): The validated data for creating a new Film.

        Returns:
            Film: The created Film instance.
        """
        duration_minutes = int(validated_data.get('film_duration'))
        duration_timedelta = timedelta(minutes=duration_minutes)
        validated_data['film_duration'] = duration_timedelta
        return super().create(validated_data)

    def get_seance_start_time(self, obj):
        """
        Returns the start time of the earliest seance for the film, as a formatted string.

        Args:
            obj (Film): The Film object being serialized.

        Returns:
            str: The start time of the earliest seance as a formatted string, or None if there are no seances.
        """
        seances = obj.seance_set.all()
        if seances:
            start_time = seances.order_by('start_time').first().start_time
            return start_time.strftime('%Y-%m-%d')
        return None

    def get_seance_finish_time(self, obj):
        """
        Returns the finish time of the latest seance for the film, as a formatted string.

        Args:
            obj (Film): The Film object being serialized.

        Returns:
            str: The finish time of the latest seance as a formatted string, or None if there are no seances.
        """
        seances = obj.seance_set.all()
        if seances:
            finish_time = seances.order_by('-start_time').first().start_time
            return finish_time.strftime('%Y-%m-%d')
        return None


class SeanceSerializer(serializers.ModelSerializer):
    """
    Serializer class for Seance model.

    Fields:
        All fields of the Seance model are included.

    Read-only fields:
        `seats` and `is_editable`.

    Methods:
        validate - validates the data and raises a validation error if necessary.

    """
    class Meta:
        model = models.Seance
        fields = '__all__'
        read_only_fields = ['seats', 'is_editable']

    def validate(self, data):
        """
        Validates the seance data.

        Parameters:
            data (dict): A dictionary containing the seance data to be validated.

        Returns:
            dict: The validated seance data.

        Raises:
            ValidationError: If the start time is earlier than the film release date or
            if the seance overlaps with an existing seance.
        """

        if 'start_time' in data and data['start_time'].date() < data['film'].release_date:
            raise serializers.ValidationError(_('Start time cannot be earlier than film release date'))

        hall = data['hall'] if 'hall' in data else self.instance.hall
        start_time = data['start_time'] if 'start_time' in data else self.instance.start_time
        film_duration = data['film'].film_duration if 'film' in data else self.instance.film.film_duration

        # Calculate finish_time based on start_time and film duration
        finish_time = start_time + film_duration

        # Check if there are any overlapping seances
        overlapping_seances = models.Seance.objects.filter(
            hall=hall,
            start_time__lt=finish_time,
            finish_time__gt=start_time
        ).exclude(pk=self.instance.pk if self.instance else None)

        if overlapping_seances.exists():
            raise serializers.ValidationError(_('Seances cannot overlap'))

        # Add finish_time to the data dictionary
        data['finish_time'] = finish_time

        return data


class TicketSerializer(serializers.ModelSerializer):
    """
    Serializer class for the Ticket model.

    Fields:
    - user: A hidden field that defaults to the currently authenticated user.
    - row: An integer field representing the row number of the ticket, with a minimum value of 1.
    - seat: An integer field representing the seat number of the ticket, with a minimum value of 1.

    Methods:
    - validate: Custom validation method for the serializer. Validates that the seance has not started yet,
        the seat is not already taken, and the requested seat and row are valid for the seance's hall. Also,
        decreases the number of available seats for the seance and saves it.
    """
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    row = serializers.IntegerField(validators=[MinValueValidator(1)])
    seat = serializers.IntegerField(validators=[MinValueValidator(1)])

    class Meta:
        model = models.Ticket
        fields = '__all__'

    def validate(self, data):
        """
        Custom validation method for the Ticket serializer. Validates that the seance has not started yet,
        the seat is not already taken, and the requested seat and row are valid for the seance's hall. Also,
        decreases the number of available seats for the seance and saves it.

        Args:
        - data: A dictionary containing the deserialized data for the Ticket object.

        Returns:
        - dict: The validated data dictionary, with the number of available seats for the seance decreased by 1.
        """
        seance = data['seance']
        if seance.start_time < timezone.now():
            raise serializers.ValidationError('Time is up! You can not byu ticket on this seance!')
        else:
            seat = data['seat']
            row = data['row']
            ticket_check = models.Ticket.objects.filter(seance=seance, row=row, seat=seat)
            if seance.seats == 0:
                raise serializers.ValidationError('Sorry, all seats already taken! Pick another seance!')
            elif ticket_check:
                serializers.ValidationError('seat %s in row %s is already taken! Pick another one!' % (seat, row))
            elif row > seance.hall.row or seat > seance.hall.seat:
                raise serializers.ValidationError('You can not chose this seat.'
                                                  ' In request hall %s rows and %s seats'
                                                  % (seance.hall.row, seance.hall.seat))
            else:
                seance.seats -= 1
                seance.save()
                return data
