import pytest
import datetime
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from rides.models import City, Route, Trip, TripRequest, Profile
from django.test import Client

User = get_user_model()

@pytest.fixture
def setup_route(db):
    # Create two cities and a route between them
    origin = City.objects.create(name='CityA', address='AddrA', latitude=0, longitude=0)
    destination = City.objects.create(name='CityB', address='AddrB', latitude=1, longitude=1)
    return Route.objects.create(origin=origin, destination=destination, distance_km=5, avg_time_minutes=10)

# 1. Driver creates a trip and sees it in their "My Trips" page
@pytest.mark.django_db
def test_driver_end_to_end_flow(setup_route):
    client = Client()
    # Create and login driver
    driver = User.objects.create_user(username='enddriver', password='pass')
    profile, _ = Profile.objects.get_or_create(user=driver)
    profile.has_car = True
    profile.make = 'Ford'
    profile.model = 'Fiesta'
    profile.plate = 'XYZ789'
    profile.seats = 3
    profile.save()
    client.force_login(driver)

    # Driver posts new trip using aware datetime
    departure_dt = timezone.make_aware(datetime.datetime(2099, 1, 2, 12, 0), timezone.get_current_timezone())
    url_create = reverse('rides:trip-create')
    resp = client.post(
        url_create,
        {
            'route': setup_route.id,
            'departure': departure_dt.isoformat(),
            'seats_available': 2
        },
        follow=True
    )
    assert resp.status_code == 200

    # Driver sees the trip in their "My Trips" listing
    url_mytrips = reverse('rides:my-trips')
    myresp = client.get(url_mytrips)
    assert myresp.status_code == 200
    # Check that both city names appear
    assert b'CityA' in myresp.content and b'CityB' in myresp.content

# 2. Passenger requests a trip and sees confirmation flag in context
@pytest.mark.django_db
def test_passenger_request_shows_indicator(setup_route):
    client = Client()
    # Setup driver and trip with aware datetime
    driver = User.objects.create_user(username='drv', password='pass')
    prof, _ = Profile.objects.get_or_create(user=driver)
    prof.has_car = True
    prof.make = 'M'
    prof.model = 'M'
    prof.plate = 'P'
    prof.seats = 4
    prof.save()
    departure_dt = timezone.make_aware(datetime.datetime(2099, 1, 3, 8, 0), timezone.get_current_timezone())
    trip = Trip.objects.create(
        driver=driver,
        route=setup_route,
        departure=departure_dt,
        seats_available=2,
        status='P'
    )

    # Create and login passenger
    passenger = User.objects.create_user(username='passend', password='pass')
    client.force_login(passenger)

    # Passenger requests a seat, follow redirect to detail
    url_request = reverse('rides:trip-request', args=[trip.id])
    resp = client.post(url_request, {'seat_requested': 1}, follow=True)
    assert resp.status_code == 200
    # Confirm the context flag is True
    assert resp.context.get('seat_requested') is True

    # The detail page shows origin and destination
    assert f"{setup_route.origin} → {setup_route.destination}".encode() in resp.content

# 3. Driver accepts a passenger request and passenger sees accepted trip
@pytest.mark.django_db
def test_driver_accepts_and_passenger_sees_in_my_trips(setup_route):
    client = Client()
    # Setup driver, trip, and passenger request with aware datetime
    driver = User.objects.create_user(username='drv2', password='pass')
    prof, _ = Profile.objects.get_or_create(user=driver)
    prof.has_car = True
    prof.make = 'X'
    prof.model = 'Y'
    prof.plate = 'Z'
    prof.seats = 3
    prof.save()
    departure_dt = timezone.make_aware(datetime.datetime(2099, 1, 4, 9, 0), timezone.get_current_timezone())
    trip = Trip.objects.create(
        driver=driver,
        route=setup_route,
        departure=departure_dt,
        seats_available=3,
        status='P'
    )

    passenger = User.objects.create_user(username='pend2', password='pass')
    req = TripRequest.objects.create(trip=trip, passenger=passenger, status='P')

    # Driver logs in and accepts the request
    client.force_login(driver)
    url_manage = reverse('rides:manage-participation-request', args=[req.id])
    resp = client.post(url_manage, {'action': 'accept'}, follow=True)
    assert resp.status_code == 200
    req.refresh_from_db()
    assert req.status == 'A'

    # Passenger logs in and sees the accepted trip in "My Trips"
    client.logout()
    client.force_login(passenger)
    url_mytrips = reverse('rides:my-trips')
    myresp = client.get(url_mytrips)
    assert b'Accepted' in myresp.content or str(trip.id).encode() in myresp.content
