from django import forms
from django.contrib.auth.models import User
from .models import Car
from django.contrib.auth.forms import AuthenticationForm
from django import forms

class SignupForm(forms.ModelForm):
    """
    User registers with: first_name, last_name, email (as username), password,
    and optionally car details (make, model, plate, seats).
    """
    password = forms.CharField(widget=forms.PasswordInput)
    has_car = forms.BooleanField(
        label="I have a car",
        required=False
    )

    # Car detail fields (only saved if has_car is True)
    make = forms.CharField(max_length=50, required=False)
    model = forms.CharField(max_length=50, required=False)
    plate = forms.CharField(max_length=15, required=False)
    seats = forms.IntegerField(min_value=1, required=False)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('has_car'):
            # require all car fields
            for fld in ('make','model','plate','seats'):
                if not cleaned.get(fld):
                    self.add_error(fld, "This field is required if you have a car.")
        return cleaned

    def save(self, commit=True):
        # create the user
        user = User(
            username=self.cleaned_data['email'],  # email as username
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            email=self.cleaned_data['email'],
        )
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()

            # if user has car, create it
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
    Ask for email and password (instead of username).
    """
    username = forms.EmailField(label="Email", widget=forms.EmailInput)