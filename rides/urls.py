from django.urls import path
from .views import TripListView, TripDetailView
from .views import TripRequestView
from .views import SignupView, EmailLoginView

app_name = 'rides'

urlpatterns = [
    # List all planned trips
    path('trips/', TripListView.as_view(), name='trip-list'),
    # Show details for a single trip by its PK
    path('trips/<int:pk>/', TripDetailView.as_view(), name='trip-detail'),
    path('trips/<int:pk>/request/', TripRequestView.as_view(), name='trip-request'),
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', EmailLoginView.as_view(), name='login'),
]
