"""
Cinema URL Configuration

"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from mycinema import views


urlpatterns = [
    path('', include('api.urls')),
    path('', views.SeancesTodayListView.as_view(), name='seances_today'),
    path('admin/', admin.site.urls),
    path('', include('mycinema.urls')),
    path('', include('users.urls')),
    path('__debug__/', include('debug_toolbar.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
