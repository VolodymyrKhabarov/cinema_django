"""
API application URL Configuration
"""

from django.urls import include, path
from rest_framework import routers

from api.views import FilmViewSet, HallViewSet, SeanceViewSet, TicketViewSet, UserCreateAPIView, LogoutView, LoginView, \
    ProfileView, TomorrowSeanceView, TodaySeanceView

router = routers.DefaultRouter()
router.register(r'films', FilmViewSet)
router.register(r'halls', HallViewSet)
router.register(r'seances', SeanceViewSet)
router.register(r'tickets', TicketViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/signup/', UserCreateAPIView.as_view(), name='signup'),
    path('api/signin/', LoginView.as_view(), name='login'),
    path('api/logout/', LogoutView.as_view(), name='logout'),
    path('api/profile/', ProfileView.as_view(), name='profile'),
    path('api/seance/today/', TodaySeanceView.as_view(), name='all_seances'),
    path('api/seance/tomorrow/', TomorrowSeanceView.as_view(), name='seances_tomorrow')
]
