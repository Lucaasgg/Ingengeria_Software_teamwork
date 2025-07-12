from django.urls import path
from .views import (
    TripListView, TripDetailView, TripRequestView
)
from . import views


app_name = 'rides'

urlpatterns = [
    path('trips/',           TripListView.as_view(),    name='trip-list'),
    path('trips/<int:pk>/',  TripDetailView.as_view(),  name='trip-detail'),
    path('trips/<int:pk>/request/', TripRequestView.as_view(), name='trip-request'),
    path('trips/create/', views.create_trip, name='trip-create'),
    path('mytrips/', views.my_trips, name='my-trips'),
    path('trips/<int:trip_id>/update-status/', views.update_trip_status, name='update-trip-status'),
    path('requests/<int:request_id>/manage/', views.manage_participation_request, name='manage-participation-request'),
]