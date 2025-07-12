from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.views.generic import ListView
from .models import Trip

UserModel = get_user_model()

class EmailBackend(ModelBackend):
    """
    Authenticate using email instead of username.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        # Here 'username' will actually be the email from the form
        try:
            user = UserModel.objects.get(email__iexact=username)
        except UserModel.DoesNotExist:
            return None
        else:
            if user.check_password(password):
                return user
        return None
class TripListView(ListView):
    model = Trip
    template_name = 'rides/trip_list.html'
    context_object_name = 'trips'

    def get_queryset(self):
        qs = Trip.objects.filter(status='P')
        if self.request.user.is_authenticated:
            qs = qs.exclude(driver=self.request.user)
        return qs
