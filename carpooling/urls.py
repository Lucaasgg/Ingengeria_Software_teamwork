"""
URL configuration for carpooling project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# carpooling/urls.py

from django.views.generic import TemplateView
from django.contrib import admin
from django.urls import path, include
from rides.views import SignupView, EmailLoginView, ProfileView
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', TemplateView.as_view(template_name='rides/home.html'), name='home'),
    path('admin/', admin.site.urls),

    # --- Authentication URLs under /accounts/ ---
    path('accounts/signup/', SignupView.as_view(),      name='signup'),
    path('accounts/login/',  EmailLoginView.as_view(),  name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
   path('accounts/profile/', ProfileView.as_view(), name='profile'),


    # --- Rides URLs under /rides/ ---
    path('rides/', include('rides.urls', namespace='rides')),
]