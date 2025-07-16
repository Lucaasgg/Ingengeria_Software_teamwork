
from django.contrib import admin
from .models import Car, Route, Trip, TripRequest, City

@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('owner', 'make', 'model', 'plate', 'seats')
    search_fields = ('make', 'model', 'plate', 'owner__username')

@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ('origin', 'destination', 'distance_km', 'avg_time_minutes')
    search_fields = ('origin', 'destination')

@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ('id', 'driver', 'route', 'departure', 'seats_available', 'status')
    list_filter = ('status', 'departure')
    search_fields = ('driver__username',)

@admin.register(TripRequest)
class TripRequestAdmin(admin.ModelAdmin):
    list_display = ('trip', 'passenger', 'status', 'requested_at')
    list_filter = ('status',)
    search_fields = ('passenger__username',)
    
@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'latitude', 'longitude')
    search_fields = ('name', 'address')