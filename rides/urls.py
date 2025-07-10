from django.urls import path
from .views import TripListView, TripDetailView

app_name = 'rides'

urlpatterns = [
    # List all planned trips
    path('trips/', TripListView.as_view(), name='trip-list'),
    # Show details for a single trip by its PK
    path('trips/<int:pk>/', TripDetailView.as_view(), name='trip-detail'),
]
