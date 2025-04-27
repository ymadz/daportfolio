# finance_tracker/urls.py (Project-level URL configuration)
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('myapp.urls')),  # Include the app URLs here
]
