"""
Module for registration mycinema models
"""

from django.contrib import admin

from mycinema.models import Film, Hall, Seance, Ticket


@admin.register(Film)
class FilmAdmin(admin.ModelAdmin):
    pass


@admin.register(Seance)
class SeanceAdmin(admin.ModelAdmin):
    pass


@admin.register(Hall)
class HallAdmin(admin.ModelAdmin):
    pass


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    pass
