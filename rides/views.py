#rides/views.py
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.contrib import messages
from .models import Trip, TripRequest
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
    
class TripRequestView(LoginRequiredMixin, View):
    """
    Handles a passenger’s request to join a trip.
    Only logged-in users can post.
    """
    login_url = '/accounts/login/'      # redirect here if not logged in
    redirect_field_name = 'next'

    def post(self, request, pk):
        # Look up the trip and ensure it’s still planned
        trip = get_object_or_404(Trip, pk=pk, status='P')

        # Prevent the driver from requesting their own trip
        if trip.driver == request.user:
            messages.error(request, "You can’t request your own trip.")
            return redirect('rides:trip-detail', pk=pk)

        # Create the request or show a message if it already exists
        req, created = TripRequest.objects.get_or_create(
            trip=trip,
            passenger=request.user,
            defaults={'status': 'P'}
        )

        if created:
            messages.success(request, "Your request has been sent.")
        else:
            messages.info(request, "You’ve already requested a seat on this trip.")

        return redirect('rides:trip-detail', pk=pk)