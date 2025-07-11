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
]