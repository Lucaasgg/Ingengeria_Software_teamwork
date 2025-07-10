#rides/views.py


from django.views.generic import ListView, DetailView
from .models import Trip

class TripListView(ListView):
    """
    Show a list of all upcoming (planned) trips.
    """
    model = Trip
    template_name = 'rides/trip_list.html'
    context_object_name = 'trips'
    queryset = Trip.objects.filter(status='P')

class TripDetailView(DetailView):
    """
    Show the full details of a single trip.
    """
    model = Trip
    template_name = 'rides/trip_detail.html'
    context_object_name = 'trip'