from django.urls import path
from . import views

urlpatterns = [
    path('', views.portfolio_home, name='portfolio_home'),
    path('mean_variance_calculator/', views.mean_variance_calculator, name='mean_variance_calculator'),
    path("demographic-analyzer/", views.demographic_analyzer, name="demographic-analyzer"),
]
