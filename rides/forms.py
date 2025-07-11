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


# rides/forms.py

from django import forms
from .models import Profile

class ProfileForm(forms.ModelForm):
    HAS_CAR_CHOICES = [
        (True,  'Yes'),
        (False, 'No'),
    ]
    has_car = forms.ChoiceField(
        choices=HAS_CAR_CHOICES,
        widget=forms.RadioSelect,
        label="Do you have a car?"
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

    def clean_has_car(self):
        # convierte el string 'True' / 'False' a booleano
        return self.cleaned_data['has_car'] == 'True'


class SignupForm(forms.ModelForm):
    """
    User registers with: first_name, last_name, email (as username), password,
    and optionally car details (make, model, plate, seats).
    """
    password = forms.CharField(widget=forms.PasswordInput)
    HAS_CAR_CHOICES = [
        ('True',  'Yes'),
        ('False', 'No'),
    ]
    has_car = forms.ChoiceField(
        label="Do you have a car?",
        choices=HAS_CAR_CHOICES,
        widget=forms.RadioSelect
    )

    # Car detail fields (only saved if has_car == True)
    make  = forms.CharField(max_length=50, required=False)
    model = forms.CharField(max_length=50, required=False)
    plate = forms.CharField(max_length=15, required=False)
    seats = forms.IntegerField(min_value=1, required=False)

    class Meta:
        model  = User
        fields = ['first_name', 'last_name', 'email']

    def clean(self):
        cleaned = super().clean()
        has_car = cleaned.get('has_car') == 'True'
        if has_car:
            # require all car fields
            for fld in ('make','model','plate','seats'):
                if not cleaned.get(fld):
                    self.add_error(fld, "This field is required if you have a car.")
        return cleaned

    def clean_has_car(self):
        # convierte el string a booleano
        return self.cleaned_data['has_car'] == 'True'

    def save(self, commit=True):
        # creamos el usuario
        user = User(
            username=self.cleaned_data['email'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            email=self.cleaned_data['email'],
        )
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            # si tiene coche, lo guardamos
            if self.cleaned_data['has_car']:
                Car.objects.create(
                    owner=user,
                    make=self.cleaned_data['make'],
                    model=self.cleaned_data['model'],
                    plate=self.cleaned_data['plate'],
                    seats=self.cleaned_data['seats'],
                )
        return user


class EmailAuthenticationForm(AuthenticationForm):
    """
    Override the login form to ask for Email + Password.
    """
    username = forms.EmailField(label="Email", widget=forms.EmailInput)
