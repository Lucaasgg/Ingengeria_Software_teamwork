# rides/views.py

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


class TripListView(ListView):
    """
    Lista todos los viajes planificados (status='P').
    """
    model               = Trip
    template_name       = 'rides/trip_list.html'
    context_object_name = 'trips'
    queryset            = Trip.objects.filter(status='P')


class TripDetailView(DetailView):
    """
    Detalle de un viaje, junto con un flag si el usuario
    ya ha solicitado plaza.
    """
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
    """
    Gestiona la petición POST de solicitar plaza.
    Evita duplicados y que el conductor se solicite a sí mismo.
    """
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
    """
    Función que muestra y procesa simultáneamente el UserForm
    y el ProfileForm para que el usuario edite sus datos y coche.
    """
    # Garantiza que exista un Profile para este usuario
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        uform = UserForm(request.POST, instance=request.user)
        pform = ProfileForm(request.POST, instance=profile)
        if uform.is_valid() and pform.is_valid():
            uform.save()
            pform.save()
            messages.success(request, "Your profile has been updated.")
            return redirect('profile')         # debe coincidir con name="profile"
    else:
        uform = UserForm(instance=request.user)
        pform = ProfileForm(instance=profile)

    return render(request, 'rides/profile.html', {
        'uform': uform,
        'pform': pform,
    })


class ProfileView(View):
    """
    Envoltorio para poder usar as_view() en urls.py sin cambiar
    la lógica de profile_view().
    """
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
