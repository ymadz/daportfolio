# tracker/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('add_transaction/', views.add_transaction, name='add_transaction'),
    path('set_budget/', views.set_budget, name='set_budget'),
    path('analytics/', views.analytics, name='analytics'),
]