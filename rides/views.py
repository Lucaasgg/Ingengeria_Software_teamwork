from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.views import View
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Trip, TripRequest

class TripListView(ListView):
    """
    Show a list of all upcoming trips (status='P').
    """
    model = Trip
    template_name = 'rides/trip_list.html'
    context_object_name = 'trips'
    queryset = Trip.objects.filter(status='P')

class TripDetailView(DetailView):
    """
    Show details for a single Trip.
    """
    model = Trip
    template_name = 'rides/trip_detail.html'
    context_object_name = 'trip'

class TripRequestView(LoginRequiredMixin, View):
    """
    Handle a user POSTing to request a seat on a Trip.
    Only logged-in users can post.
    """
    login_url = '/accounts/login/'
    redirect_field_name = 'next'

    def post(self, request, pk):
        # Fetch only planned trips
        trip = get_object_or_404(Trip, pk=pk, status='P')

        # Prevent driver from requesting their own trip
        if trip.driver == request.user:
            messages.error(request, "You can’t request your own trip.")
            return redirect('rides:trip-detail', pk=pk)

        # Create the TripRequest if it doesn’t exist
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
