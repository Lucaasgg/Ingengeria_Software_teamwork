# rides/urls.py

from django.urls import path
from .views import TripListView, TripDetailView

app_name = 'rides'

urlpatterns = [
    # List all trips
    path('trips/', TripListView.as_view(), name='trip-list'),
    # Detail view for a single trip (by PK)
    path('trips/<int:pk>/', TripDetailView.as_view(), name='trip-detail'),
]
