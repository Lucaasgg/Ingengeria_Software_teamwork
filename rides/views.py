from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.views import View
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Trip, TripRequest
from django.views.generic import TemplateView
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.views import LoginView
from .forms import SignupForm, EmailAuthenticationForm, ProfileForm
from django.views.generic import FormView

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
class ProfileView(LoginRequiredMixin, FormView):
    template_name = 'rides/profile.html'
    form_class    = ProfileForm
    success_url   = reverse_lazy('profile')

    def get_initial(self):
        user = self.request.user
        return {
          'first_name': user.first_name,
          'last_name':  user.last_name,
          'email':      user.email,
          'has_car':    hasattr(user, 'car'),
        }

    def form_valid(self, form):
        form.save(self.request.user)
        return super().form_valid(form)
    

class SignupView(CreateView):
    form_class = SignupForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('login')

class EmailLoginView(LoginView):
    authentication_form = EmailAuthenticationForm
    template_name = 'registration/login.html'