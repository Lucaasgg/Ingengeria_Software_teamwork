from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Trip

class TripListView(ListView):
    """
    Displays a list of all upcoming trips.
    """
    model = Trip
    template_name = 'rides/trip_list.html'   # you will create this template
    context_object_name = 'trips'
    queryset = Trip.objects.filter(status='P')  # only planned trips

class TripDetailView(DetailView):
    """
    Shows the details for a single trip.
    """
    model = Trip
    template_name = 'rides/trip_detail.html'  # you will create this template
    context_object_name = 'trip'
