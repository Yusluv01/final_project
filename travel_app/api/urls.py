from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('stats/', views.stats_api, name='api_stats'),
    path('clients/', views.ClientsAPIView.as_view(), name='api_clients'),
    path('bookings/', views.BookingsAPIView.as_view(), name='api_bookings'),
    path('notifications/read/', views.mark_notifications_read, name='api_notifications_read'),
]