"""
This module defines the urlpatterns of the 'mycinema' app.

"""

from django.urls import path

from mycinema import views

urlpatterns = [
    path('films/create/', views.FilmCreateView.as_view(), name='add_film'),
    path('films/<int:pk>/', views.FilmDetailView.as_view(), name='film_by_id'),
    path('films/', views.FilmListView.as_view(), name='all_films'),
    path('halls/', views.HallListView.as_view(), name='all_halls'),
    path('halls/create/', views.HallCreateView.as_view(), name='add_hall'),
    path('halls/edit/<int:pk>/', views.HallUpdateView.as_view(), name='edit_hall'),
    path('halls/<int:pk>/', views.HallDetailView.as_view(), name='hall_by_id'),
    path('seances/', views.SeanceListView.as_view(), name='all_seances'),
    path('seances/tomorrow/<int:delta>/', views.SeancesTodayListView.as_view(), name='seances_tomorrow'),
    path('seances/sorted/<int:ord>/', views.SeanceListView.as_view(), name='seances_sorted'),
    path('seances/create/', views.SeanceCreateView.as_view(), name='add_seance'),
    path('seances/edit/<int:pk>/', views.SeanceUpdateView.as_view(), name='edit_seance'),
    path('seances/<int:pk>/', views.SeanceDetailView.as_view(), name='seance_by_id'),
    path('tickets/', views.TicketListView.as_view(), name='all_tickets'),
    path('tickets/<int:pk>/', views.TicketDetailView.as_view(), name='ticket_by_id')
]
