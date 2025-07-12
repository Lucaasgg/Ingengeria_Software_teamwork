# rides/views.py

from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView
from django.views import View
from django.contrib.auth.views import LoginView
from django.urls   import reverse_lazy
from django.contrib.auth import login, get_backends
from .models import Trip, TripRequest, Profile
from .forms import (
    SignupForm,
    EmailAuthenticationForm,
    UserForm,
    ProfileForm,
)
from .forms import TripCreateForm

class TripListView(ListView):
    model = Trip
    template_name = 'rides/trip_list.html'
    context_object_name = 'trips'

    def get_queryset(self):
        qs = Trip.objects.filter(status='P')
        if self.request.user.is_authenticated:
            qs = qs.exclude(driver=self.request.user)
        return qs



class TripDetailView(DetailView):
    
    model               = Trip
    template_name       = 'rides/trip_detail.html'
    context_object_name = 'trip'

    def get_context_data(self, **kwargs):
        ctx  = super().get_context_data(**kwargs)
        user = self.request.user
        ctx['already_requested'] = (
            user.is_authenticated and
            TripRequest.objects.filter(trip=self.object, passenger=user).exists()
        )
        return ctx


class TripRequestView(LoginRequiredMixin, View):
    
    login_url          = '/accounts/login/'
    redirect_field_name = 'next'

    def post(self, request, pk):
        trip = get_object_or_404(Trip, pk=pk, status='P')

        if trip.driver == request.user:
            messages.error(request, "You can’t request your own trip.")
            return redirect('rides:trip-detail', pk=pk)

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


@login_required
def profile_view(request):
   
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        uform = UserForm(request.POST, instance=request.user)
        pform = ProfileForm(request.POST, instance=profile)
        if uform.is_valid() and pform.is_valid():
            uform.save()
            pform.save()
            messages.success(request, "Your profile has been updated.")
            return redirect('profile')
    else:
        uform = UserForm(instance=request.user)
        pform = ProfileForm(instance=profile)

    return render(request, 'rides/profile.html', {
        'uform': uform,
        'pform': pform,
    })


class ProfileView(View):
    
    def get(self,  request, *args, **kwargs):
        return profile_view(request)

    def post(self, request, *args, **kwargs):
        return profile_view(request)


class SignupView(CreateView):
    form_class = SignupForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('profile')  

    def form_valid(self, form):
        response = super().form_valid(form)
        
        user = self.object  
        login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')
        return response

class EmailLoginView(LoginView):
    """
    Login using email and password.
    """
    authentication_form = EmailAuthenticationForm
    template_name       = 'registration/login.html'

@login_required
def create_trip(request):
    profile = request.user.profile
    if not profile.has_car:
        messages.error(request, "You must have a car to create a trip.")
        return redirect('profile')

    if request.method == 'POST':
        form = TripCreateForm(request.POST)
        if form.is_valid():
            trip = form.save(commit=False)
            trip.driver = request.user
            trip.save()
            messages.success(request, "Trip created successfully!")
            return redirect('rides:trip-list')  # Cambia según tu namespace
    else:
        form = TripCreateForm()

    return render(request, 'rides/trip_create.html', {'form': form})

@login_required
def my_trips(request):
    # All trips where the logged-in user is the driver
    trips = Trip.objects.filter(driver=request.user).order_by('-departure')
    return render(request, 'rides/my_trips.html', {'trips': trips})

@login_required
def update_trip_status(request, trip_id):
    trip = get_object_or_404(Trip, id=trip_id, driver=request.user)
    if request.method == 'POST':
        status = request.POST.get('status')
        if status in dict(Trip.STATUS_CHOICES):
            trip.status = status
            trip.save()
            messages.success(request, "Trip status updated.")
        else:
            messages.error(request, "Invalid status.")
    return redirect('my-trips')


@login_required
def manage_participation_request(request, request_id):
    # Only the driver can manage requests for their trip
    req = get_object_or_404(
        TripRequest,
        id=request_id,
        trip__driver=request.user  # Double underscore to traverse relation
    )
    action = request.POST.get('action')
    if action == 'accept' and req.status == 'P':
        if req.trip.seats_available > 0:
            req.status = 'A'
            req.trip.seats_available -= 1
            req.trip.save()
            req.save()
            messages.success(request, "Passenger accepted.")
        else:
            messages.error(request, "No seats available!")
    elif action == 'reject' and req.status == 'P':
        req.status = 'R'
        req.save()
        messages.success(request, "Passenger rejected.")
    return redirect('rides:my-trips')
