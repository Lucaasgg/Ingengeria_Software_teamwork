from django.test import TestCase, Client
# tests de tus vistas
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Route, Trip

User = get_user_model()

class TripRequestTests(TestCase):
    def setUp(self):
        self.driver = User.objects.create_user('d', 'd@x.com', 'pass')
        self.passenger = User.objects.create_user('p', 'p@x.com', 'pass')
        route = Route.objects.create(origin='A', destination='B', distance_km=10, avg_time_minutes=60)
        self.trip = Trip.objects.create(driver=self.driver, route=route,
                                        departure='2100-01-01T12:00', seats_available=3)
    def test_request_seat_creates_triprequest(self):
        self.client.login(username='p', password='pass')
        url = reverse('rides:trip-request', args=[self.trip.pk])
        resp = self.client.post(url)
        self.assertRedirects(resp, reverse('rides:trip-detail', args=[self.trip.pk]))
        self.assertTrue(self.trip.requests.filter(passenger=self.passenger).exists())
