"""
This module contains Django forms used for creating, editing, and validating
cinema-related objects such as films, halls, and seances. It defines the `FilmForm`,
`HallForm`, `SeanceForm`, and `SeanceUpdateForm` classes, each of
which is a subclass of Django's `ModelForm` or `Form` class.

The `FilmForm` class is used for creating film objects, while the `HallForm` class
is used for creating and editing hall objects. The `SeanceForm` class is used for
creating and validating seances, and the `SeanceUpdateForm` class is used for updating seances.

All of these forms use various widgets provided by Django and third-party libraries such as
`tempus_dominus` to improve the user experience. They also include custom validation logic
to ensure that the data entered by users is valid and consistent with the database schema.

Note that the `SeanceForm` and `SeanceUpdateForm` classes are particularly complex, as they
must ensure that new seances do not overlap with existing ones and that their start times are
consistent with the release date of the film being shown. This validation logic is implemented
in the `clean()` and `clean_start_time()` methods of these classes.
"""

import datetime
from datetime import date, timedelta
from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django.utils import timezone
from tempus_dominus.widgets import DatePicker, DateTimePicker

from mycinema.models import Film, Hall, Seance


class FilmForm(ModelForm):
    """
    A form for creating or updating a Film instance.

    This form extends Django's built-in `ModelForm` and provides a custom widget for the
    `release_date` field, as well as additional validation and processing for the
    `film_duration` field.

    Attributes:
        release_date (DateField): A form field for the film's release date, using the `DatePicker`
        widget.
        film_duration (CharField): A form field for the film's duration in minutes.

    Meta:
        model (Film): The model that this form is based on.
        fields (str): A special string that tells Django to include all fields from the model.
    """

    release_date = forms.DateField(widget=DatePicker)
    film_duration = forms.CharField(help_text='minutes')

    class Meta:
        model = Film
        fields = '__all__'

    def clean_film_duration(self):
        """
        Custom validation method for the film_duration field. Converts the duration
        to an integer, checks whether it's a positive number, and raises a ValidationError
        if not. Returns the duration as a string.

        Raises:
            ValidationError: If the duration is not a valid positive integer.

        Returns:
            str: The duration as a string.
        """
        duration = self.cleaned_data['film_duration']
        try:
            duration = int(duration)
            if duration <= 0:
                raise ValidationError('Duration must be a positive integer.')
        except ValueError:
            raise ValidationError('Duration must be a positive integer.')
        return str(duration)

    def save(self, commit=True):
        """
        Saves the form's data into a new or existing Film instance.

        If commit is True (the default), the instance is saved to the database. Otherwise,
        the returned instance has not been saved yet, and it's up to the caller to save it later.

        The film_duration field is converted from minutes (a string) to a timedelta object
        before being saved to the
        Film instance.

        Args:
            commit (bool): Whether to save the instance to the database or not.

        Returns:
            Film: The saved or updated Film instance.

        Raises:
            ValueError: If the film_duration field is not a valid integer or is negative.
        """

        film = super().save(commit=False)
        duration_minutes = int(self.cleaned_data.get('film_duration'))
        duration_timedelta = timedelta(minutes=duration_minutes)
        film.film_duration = duration_timedelta
        if commit:
            film.save()
        return film


class HallForm(ModelForm):
    """
    The HallForm is a ModelForm for creating and updating Hall instances. It inherits from
    Django's ModelForm class and is used to validate and render HTML forms based on the Hall model.

    Attributes:

    model (Hall): The Hall model this form is associated with.
    exclude (tuple): A list of fields to exclude from the form. In this case, is_editable field
    is excluded.
    labels (dict): A dictionary that maps the field names to the corresponding human-readable labels
    This form doesn't have any custom methods, and it uses the default save() method inherited
    from the parent class.
    """
    class Meta:
        model = Hall
        exclude = ('is_editable',)
        labels = {
            'name': 'Hall name',
            'row': 'Rows',
            'seat': 'Seats in a row'
        }

    def clean(self):
        """
        The clean method is a built-in method of Django's ModelForm class. It is called when the
        form is submitted, after the form data has been validated and cleaned up. This method performs
        additional validation on the form data and raises a ValidationError if the data is invalid.

        In this specific implementation, the clean method checks if the is_editable field of the
        associated Hall instance is set to True. If it is not, it raises a ValidationError with the
        message "This hall cannot be edited." Otherwise, the method returns the cleaned data.

        Parameters:
            self: The instance of the HallForm object.

        Returns:
            The cleaned form data. If the form data is invalid, it raises a ValidationError.
        """
        cleaned_data = super().clean()
        hall = self.instance
        if not hall.is_editable:
            raise ValidationError('This hall cannot be edited.')
        return cleaned_data


class SeanceForm(forms.ModelForm):
    """
    A ModelForm used for creating instances of the Seance model.

    Fields:
    - start_time: a DateTimeField that uses a customized DateTimePicker widget
    to select the start time of the seance.
    - start_iteration_date: a DateField that uses a customized DatePicker widget
    to select the start date of the seance iteration.
    - end_iteration_date: a DateField that uses a customized DatePicker widget
    to select the end date of the seance iteration.

    The form has a clean method that checks for overlapping seances in the same hall,
    ensures that the start iteration date is the same as the start time, and that the
    start date is not earlier than the release date of the film or later than the end date.

    Methods:
    - clean(): validates the form data and returns a cleaned_data dictionary.
    - clean_start_iteration_date(): validates the start_iteration_date field and raises
    a ValidationError if the date is earlier than the current date.
    - clean_end_iteration_date(): validates the end_iteration_date field and raises
    a ValidationError if the date is earlier than the current date.
    - save(commit=True): saves the seance data to the database by creating a list of
    Seance objects based on the start_iteration_date and end_iteration_date fields,
    and using the bulk_create method of the Seance model. Returns the list of created seances.
    """

    start_time = forms.DateTimeField(widget=DateTimePicker)
    start_iteration_date = forms.DateField(widget=DatePicker, label='Date of first seance beginning')
    end_iteration_date = forms.DateField(widget=DatePicker, label='Date of last seance beginning')

    class Meta:
        model = Seance
        fields = ['film', 'hall', 'start_time', 'price']

    def clean(self):
        """
        Validates the form data and returns a cleaned_data dictionary.

        Checks for overlapping seances in the same hall, ensures that the start
        iteration date is the same as the start time, and that the start date is not
        earlier than the release date of the film or later than the end date.

        Returns:
        - cleaned_data: a dictionary containing the validated and cleaned form data.
        """
        cleaned_data = super().clean()
        start_iteration_date = cleaned_data.get('start_iteration_date')
        start_time = cleaned_data.get('start_time')
        finish_time = start_time + cleaned_data['film'].film_duration
        hall = cleaned_data.get('hall')

        seances = Seance.objects.filter(
            hall=hall,
            start_time__lt=finish_time,
            finish_time__gt=start_time,
        )

        if seances.exists():
            self.add_error('hall', 'This seance overlaps with another seance in the same hall')

        if start_iteration_date and start_time and start_iteration_date != start_time.date():
            self.add_error('start_iteration_date',
                           'Start iteration date should be the same as the start time')

        end_iteration_date = cleaned_data.get('end_iteration_date')

        if start_iteration_date and end_iteration_date and start_iteration_date > end_iteration_date:
            self.add_error('start_iteration_date', 'Start date cannot be later than end date.')

        film = cleaned_data.get('film')
        release_date = film.release_date if film else None

        if start_time is not None and release_date and start_time.date() < release_date:
            self.add_error('start_time',
                           'Start date cannot be earlier than the release date of the film')

        return cleaned_data

    def clean_start_iteration_date(self):
        """
        Validates the start_iteration_date field and raises a ValidationError
        if the date is earlier than the current date.

        Returns:
        - start_iteration_date: the validated start_iteration_date field value.
        """
        start_iteration_date = self.cleaned_data['start_iteration_date']
        if start_iteration_date < timezone.now().date():
            raise ValidationError('Start iteration date cannot be earlier than current date')
        return start_iteration_date

    def clean_end_iteration_date(self):
        """
        Validates the end_iteration_date field and raises a ValidationError
        if the date is earlier than the current date.

        Returns:
        - end_iteration_date: the validated end_iteration_date field value.
        """
        end_iteration_date = self.cleaned_data['end_iteration_date']
        if end_iteration_date < timezone.now().date():
            raise ValidationError('End iteration date cannot be earlier than current date')
        return end_iteration_date

    def save(self, commit=True):
        """
        Saves the form data to the database by creating a list of Seance objects
        based on the start_iteration_date and end_iteration_date fields, and using
        the bulk_create method of the Seance model. If the commit argument is True,
        saves the created Seance objects to the database and returns the list of created seances.

        Args:
        - commit (bool): a boolean value indicating whether to save the created seances
        to the database.

        Returns:
        - seances (list): a list of Seance objects that were created based on the form data.
        """
        seances = []
        start_iteration_date = self.cleaned_data['start_iteration_date']
        end_iteration_date = self.cleaned_data['end_iteration_date']
        hall = self.cleaned_data['hall']
        film = self.cleaned_data['film']
        start_time = self.cleaned_data['start_time']
        finish_time = start_time + film.film_duration

        while start_iteration_date <= end_iteration_date:
            seance = Seance(
                hall=hall,
                film=film,
                start_time=datetime.datetime.combine(start_iteration_date, start_time.time()),
                finish_time=datetime.datetime.combine(start_iteration_date, finish_time.time()),
                price=self.cleaned_data['price'],
                seats=hall.total_seats
            )
            seances.append(seance)
            start_iteration_date += datetime.timedelta(days=1)

        if commit:
            Seance.objects.bulk_create(seances)

        return seances


class SeanceUpdateForm(forms.ModelForm):
    """
    The SeanceUpdateForm class is a Django form used to update an existing Seance instance.
    It has a start_time field of type DateTimeField which uses the DateTimePicker widget.
    The form is used to update the film, hall, price, and start_time fields of the Seance model.
    """
    start_time = forms.DateTimeField(widget=DateTimePicker)

    class Meta:
        """
        Class Meta is used to specify metadata.
        """

        model = Seance
        fields = ("film", "hall", "price", "start_time")

    def clean(self):
        """
        The clean method is used to validate the form data. It first calls the parent class's
        clean method to get the cleaned form data. It then checks if the start_time is earlier
        than the release date of the film being shown at the seance, and raises a validation
        error if it is. It also checks if the seance overlaps with any existing seances, and
        raises a validation error if it does. If there are no errors, it returns the cleaned data.
        """
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        film = cleaned_data.get('film')
        release_date = film.release_date if film else None

        if start_time is not None and release_date and start_time.date() < release_date:
            self.add_error('start_time',
                           'Start date cannot be earlier than the release date of the film')

        # Check if the seance overlaps with existing seances
        seances = Seance.objects.exclude(pk=self.instance.pk)  # exclude the current instance if it's being edited
        for seance in seances:
            if start_time < seance.finish_time and seance.start_time < start_time:
                self.add_error('start_time', "The seance overlaps with an existing seance")

        return cleaned_data

    def clean_start_time(self):
        """
        The clean_start_time method is used to validate the start_time field specifically.
        It gets the cleaned start_time from the form data and checks if it is earlier than
        the current time. If it is, it raises a validation error. If there are no errors,
        it returns the cleaned start_time.
        """
        start_time = self.cleaned_data['start_time']
        if start_time < timezone.now():
            self.add_error('start_time', 'Start time cannot be earlier than the current time')
        if not self.instance.is_editable:
            self.add_error('start_time', 'Seance is not editable')
        return start_time
