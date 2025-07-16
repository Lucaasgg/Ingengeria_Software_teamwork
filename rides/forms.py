# rides/forms.py
from django.utils import timezone
from django.core.exceptions import ValidationError
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from .models import Profile
from .models import Car
from django.contrib.auth import get_user_model
from .models import Trip





User = get_user_model()


class UserForm(forms.ModelForm):
    """
    For editing first_name, last_name and email on the profile page.
    """
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


# rides/forms.py

from django import forms
from .models import Profile

class ProfileForm(forms.ModelForm):
    HAS_CAR_CHOICES = [
        ('True',  'Yes'),
        ('False', 'No'),
    ]
    has_car = forms.TypedChoiceField(
        choices=HAS_CAR_CHOICES,
        widget=forms.RadioSelect,
        label="Do you have a car?",
        coerce=lambda x: x == 'True'
    )

    class Meta:
        model  = Profile
        fields = ['has_car', 'make', 'model', 'plate', 'seats']
        widgets = {
            'make' : forms.TextInput(attrs={'placeholder': 'e.g. Toyota'}),
            'model': forms.TextInput(attrs={'placeholder': 'e.g. Corolla'}),
            'plate': forms.TextInput(attrs={'placeholder': 'e.g. AB123CD'}),
            'seats': forms.NumberInput(attrs={'min':1, 'max':8}),
        }



class SignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    make = forms.CharField(max_length=50, required=False)
    model = forms.CharField(max_length=50, required=False)
    plate = forms.CharField(max_length=15, required=False)
    seats = forms.IntegerField(min_value=1, required=False)
    HAS_CAR_CHOICES = [
        ('True', 'Yes'),
        ('False', 'No'),
    ]
    has_car = forms.ChoiceField(
        choices=HAS_CAR_CHOICES,
        widget=forms.RadioSelect,
        label="Do you have a car?"
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def clean(self):
        cleaned = super().clean()
        # SOLO si has_car == 'True', exige los campos del coche
        if cleaned.get('has_car') == 'True':
            for fld in ('make', 'model', 'plate', 'seats'):
                if not cleaned.get(fld):
                    self.add_error(fld, "This field is required if you have a car.")
        return cleaned

    def save(self, commit=True):
        user = User(
            username=self.cleaned_data['email'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            email=self.cleaned_data['email'],
        )
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            # Crear o actualizar Profile asociado
            profile, created = Profile.objects.get_or_create(user=user)
            profile.has_car = self.cleaned_data['has_car'] == 'True'
            if self.cleaned_data['has_car'] == 'True':
                profile.make = self.cleaned_data['make']
                profile.model = self.cleaned_data['model']
                profile.plate = self.cleaned_data['plate']
                profile.seats = self.cleaned_data['seats']
            else:
                profile.make = ''
                profile.model = ''
                profile.plate = ''
                profile.seats = None
            profile.save()
        return user

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise ValidationError("A user with this email already exists.")
        return email



class EmailAuthenticationForm(AuthenticationForm):
    """
    Override the login form to ask for Email + Password.
    """
    username = forms.EmailField(label="Email", widget=forms.EmailInput)

class TripCreateForm(forms.ModelForm):
    class Meta:
        model = Trip
        fields = ['route', 'departure', 'seats_available']
        widgets = {
            'departure': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        trip = super().save(commit=False)
        if self.user:
            trip.driver = self.user
        if commit:
            trip.save()
        return trip

    def clean(self):
        cleaned = super().clean()
        errors = {}

        departure = cleaned.get('departure')
        seats = cleaned.get('seats_available')
        user = self.user

        # Validate departure in future
        if departure and departure <= timezone.now():
            errors['departure'] = "Departure time must be in the future."

        # Validate seats vs car
        if user and hasattr(user, 'profile') and user.profile.has_car:
            max_seats = user.profile.seats or 1
            if seats is not None and seats > max_seats - 1:
                errors['seats_available'] = f"Seats cannot exceed your car's capacity."
        else:
            errors['seats_available'] = "You must have a registered car with valid seat number."

        if errors:
            raise ValidationError(errors)

        return cleaned