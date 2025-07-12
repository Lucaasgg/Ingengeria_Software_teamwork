from django.conf import settings
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

User = settings.AUTH_USER_MODEL

class Car(models.Model):
    owner = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='car'
    )
    make = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    plate = models.CharField(max_length=15, unique=True)
    seats = models.PositiveSmallIntegerField()

    def __str__(self):
        return f"{self.make} {self.model} ({self.plate})"

class Route(models.Model):
    origin = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    distance_km = models.DecimalField(max_digits=6, decimal_places=2)
    avg_time_minutes = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.origin} → {self.destination}"

class Trip(models.Model):
    STATUS_CHOICES = [
        ('P', 'Planned'),
        ('C', 'Completed'),
        ('A', 'Aborted'),
    ]
    driver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='driven_trips'
    )
    route = models.ForeignKey(
        Route,
        on_delete=models.PROTECT,
        related_name='trips'
    )
    departure = models.DateTimeField()
    seats_available = models.PositiveSmallIntegerField()
    status = models.CharField(
        max_length=1,
        choices=STATUS_CHOICES,
        default='P'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        dt = self.departure.strftime('%Y-%m-%d %H:%M')
        return f"Trip {self.id} by {self.driver} on {dt}"

    def clean(self):
        from django.core.exceptions import ValidationError
        if not self.driver_id:
            return
        if self.departure <= timezone.now():
            raise ValidationError("Departure time must be in the future.")
        if hasattr(self.driver, 'car') and self.seats_available > self.driver.car.seats:
            raise ValidationError("Seats available exceed your car's capacity.")

class TripRequest(models.Model):
    STATUS_CHOICES = [
        ('P', 'Pending'),
        ('A', 'Accepted'),
        ('R', 'Rejected'),
    ]
    trip = models.ForeignKey(
        Trip,
        on_delete=models.CASCADE,
        related_name='requests'   # OJO, esto es lo importante
    )
    passenger = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='trip_requests'
    )
    requested_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=1,
        choices=STATUS_CHOICES,
        default='P'
    )
    class Meta:
        unique_together = ('trip', 'passenger')

    def __str__(self):
        return f"{self.passenger} → Trip {self.trip.id} [{self.get_status_display()}]"

class Profile(models.Model):
    user    = models.OneToOneField(User, on_delete=models.CASCADE)
    has_car = models.BooleanField(default=False)
    make    = models.CharField(max_length=50, blank=True)
    model   = models.CharField(max_length=50, blank=True)
    plate   = models.CharField(max_length=20, blank=True)
    seats   = models.PositiveSmallIntegerField(null=True, blank=True)

@receiver(post_save, sender=User)
def ensure_profile_exists(sender, instance, **kwargs):
    Profile.objects.get_or_create(user=instance)
