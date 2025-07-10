# rides/forms.py

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from .models import Profile

User = get_user_model()


class UserForm(forms.ModelForm):
    """
    For editing first_name, last_name and email on the profile page.
    """
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class ProfileForm(forms.ModelForm):
    """
    For editing the Profile model: do you have a car? and (optionally) its details.
    """
    HAS_CAR_CHOICES = [
        (True,  'Yes'),
        (False, 'No'),
    ]

    has_car = forms.TypedChoiceField(
        label="Do you have a car?",
        choices=HAS_CAR_CHOICES,
        widget=forms.RadioSelect,
        coerce=lambda v: v == 'True'
    )

    class Meta:
        model = Profile
        fields = ['has_car', 'make', 'model', 'plate', 'seats']
        widgets = {
            'make':  forms.TextInput(attrs={'placeholder': 'e.g. Toyota'}),
            'model': forms.TextInput(attrs={'placeholder': 'e.g. Corolla'}),
            'plate': forms.TextInput(attrs={'placeholder': 'e.g. AB123CD'}),
            'seats': forms.NumberInput(attrs={'min': 1, 'max': 8}),
        }

    def clean(self):
        cleaned = super().clean()
        has_car = cleaned.get('has_car')
        if not has_car:
            # If user said "No", clear all the car fields
            for fld in ('make', 'model', 'plate', 'seats'):
                cleaned[fld] = None
        return cleaned


class SignupForm(forms.ModelForm):
    """
    For new user registration:
    - email is used as username
    - password
    - optional car info
    """
    password = forms.CharField(widget=forms.PasswordInput)
    has_car = forms.BooleanField(label="I have a car", required=False)

    make  = forms.CharField(max_length=50, required=False)
    model = forms.CharField(max_length=50, required=False)
    plate = forms.CharField(max_length=15, required=False)
    seats = forms.IntegerField(min_value=1, required=False)

    class Meta:
        model = User
        # We collect first_name, last_name, email (and password + car fields separately)
        fields = ['first_name', 'last_name', 'email']

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('has_car'):
            # require all car fields if they said yes
            for fld in ('make', 'model', 'plate', 'seats'):
                if not cleaned.get(fld):
                    self.add_error(fld, "This is required if you have a car.")
        return cleaned

    def save(self, commit=True):
        # Create the user first
        user = User(
            username=self.cleaned_data['email'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            email=self.cleaned_data['email'],
        )
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()

            # Now create a matching Profile row
            Profile.objects.create(
                user=user,
                has_car=self.cleaned_data['has_car'],
                make=self.cleaned_data.get('make') or '',
                model=self.cleaned_data.get('model') or '',
                plate=self.cleaned_data.get('plate') or '',
                seats=self.cleaned_data.get('seats') or 0,
            )

        return user


class EmailAuthenticationForm(AuthenticationForm):
    """
    Override the login form to ask for Email + Password.
    """
    username = forms.EmailField(label="Email", widget=forms.EmailInput)
