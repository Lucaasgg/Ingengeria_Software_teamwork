# rides/serializers.py

from rest_framework import serializers
from .models import Car, Route, Trip, TripRequest

class CarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = ['id', 'make', 'model', 'plate', 'seats']

class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ['id', 'origin', 'destination', 'distance_km', 'avg_time_minutes']

class TripSerializer(serializers.ModelSerializer):
    driver = serializers.StringRelatedField()
    route = RouteSerializer()

    class Meta:
        model = Trip
        fields = ['id', 'driver', 'route', 'departure', 'seats_available', 'status', 'created_at']

class TripRequestSerializer(serializers.ModelSerializer):
    passenger = serializers.StringRelatedField()
    trip = TripSerializer()

    class Meta:
        model = TripRequest
        fields = ['id', 'trip', 'passenger', 'requested_at', 'status']
