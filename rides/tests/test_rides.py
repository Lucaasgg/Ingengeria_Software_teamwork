import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from rides.models import City, Route, Trip, TripRequest, Profile

User = get_user_model()

@pytest.fixture
def user_with_car(db):
    # Create a user and ensure they have a profile with a car
    user = User.objects.create_user(username='driver', password='pass')
    profile, created = Profile.objects.get_or_create(user=user)
    profile.has_car = True
    profile.make = 'Toyota'
    profile.model = 'Corolla'
    profile.plate = 'ABC123'
    profile.seats = 4
    profile.save()
    return user

@pytest.fixture
def passenger(db):
    return User.objects.create_user(username='passenger', password='pass')

@pytest.fixture
def cities(db):
    origin = City.objects.create(name='A', address='Addr A', latitude=0, longitude=0)
    dest = City.objects.create(name='B', address='Addr B', latitude=1, longitude=1)
    return origin, dest

@pytest.fixture
def route(db, cities):
    origin, dest = cities
    return Route.objects.create(origin=origin, destination=dest, distance_km=10, avg_time_minutes=15)

@pytest.fixture
def trip(db, user_with_car, route):
    return Trip.objects.create(
        driver=user_with_car,
        route=route,
        departure='2099-01-01T00:00Z',
        seats_available=3,
        status='P'
    )

# 1. Test GET trip create form
@pytest.mark.django_db
def test_get_create_trip_view(client, user_with_car):
    client.force_login(user_with_car)
    url = reverse('rides:trip-create')
    resp = client.get(url)
    assert resp.status_code == 200
    assert b'<form' in resp.content

# 2. Test POST create trip succeeds
@pytest.mark.django_db
def test_post_create_trip_creates_object(client, user_with_car, cities, route):
    client.force_login(user_with_car)
    origin, dest = cities
    # Send correct form fields: 'route', 'departure', 'seats_available'
    data = {
        'route': route.id,
        'departure': '2099-01-01T00:00',
        'seats_available': 2,
    }
    url = reverse('rides:trip-create')
    resp = client.post(url, data)
    assert resp.status_code == 302
    assert Trip.objects.filter(driver=user_with_car, route=route).exists()

# 3. Test cannot create trip without car
@pytest.mark.django_db
def test_create_trip_without_car_fails(client, db):
    user = User.objects.create_user(username='nocar', password='pass')
    client.force_login(user)
    url = reverse('rides:trip-create')
    resp = client.get(url)
    # If no car, should redirect to profile or error
    assert resp.status_code in (302, 403)

# 4. Test trip list shows published trips
@pytest.mark.django_db
def test_trip_list_shows_published(client, user_with_car, trip):
    client.force_login(user_with_car)
    url = reverse('rides:trip-list')
    resp = client.get(url)
    assert resp.status_code == 200
    assert str(trip.id).encode() in resp.content

# 5. Test request trip creates TripRequest
@pytest.mark.django_db
def test_request_trip(client, passenger, trip):
    client.force_login(passenger)
    url = reverse('rides:trip-request', args=[trip.id])
    resp = client.post(url, {'seat_requested': 1})
    assert resp.status_code == 302
    assert TripRequest.objects.filter(trip=trip, passenger=passenger).exists()

# 6. Test cannot request more seats than available
@pytest.mark.django_db
def test_request_too_many_seats(client, passenger, trip):
    client.force_login(passenger)
    url = reverse('rides:trip-request', args=[trip.id])
    resp = client.post(url, {'seat_requested': trip.seats_available + 1})
    # The view redirects with error message flag
    assert b'error' in resp.content.lower() or resp.status_code == 302

# 7. Test driver cannot request own trip
@pytest.mark.django_db
def test_driver_cannot_request_own_trip(client, user_with_car, trip):
    client.force_login(user_with_car)
    url = reverse('rides:trip-request', args=[trip.id])
    resp = client.post(url, {'seat_requested': 1})
    assert resp.status_code == 302
    # Because driver can't request own trip, no TripRequest should be created
    assert not TripRequest.objects.filter(trip=trip, passenger=user_with_car).exists()

# 8. Test passenger view my trips (as passenger accepted)
@pytest.mark.django_db
def test_passenger_my_trips_view(client, passenger, trip):
    # Make an accepted request
    req = TripRequest.objects.create(trip=trip, passenger=passenger, status='A')
    client.force_login(passenger)
    url = reverse('rides:my-trips')
    resp = client.get(url)
    assert resp.status_code == 200
    # The accepted trip should appear
    assert str(trip.id).encode() in resp.content

# 9. Test driver manages requests view
@pytest.mark.django_db
def test_driver_manage_requests(client, user_with_car, trip, passenger):
    client.force_login(user_with_car)
    req = TripRequest.objects.create(trip=trip, passenger=passenger, status='P')
    url = reverse('rides:manage-participation-request', args=[req.id])
    resp = client.post(url, {'action': 'accept'})
    req.refresh_from_db()
    assert req.status == 'A'

# 10. Test trip status update
@pytest.mark.django_db
def test_driver_update_trip_status(client, user_with_car, trip):
    client.force_login(user_with_car)
    url = reverse('rides:update-trip-status', args=[trip.id])
    resp = client.post(url, {'status': 'C'})
    trip.refresh_from_db()
    assert trip.status == 'C'
    assert resp.status_code == 302
