from django.urls import path
from . import views

urlpatterns = [
    path('', views.portfolio_home, name='portfolio_home'),
    path('mean_variance_calculator/', views.mean_variance_calculator, name='mean_variance_calculator'),
    path("demographic-analyzer/", views.demographic_analyzer, name="demographic-analyzer"),
    path("medical-visualizer/", views.medical_visualizer, name="medical_visualizer"),
    path('time-series-visualizer/', views.time_series_visualizer, name='time_series_visualizer'),
    path('sea-level-predictor/', views.sea_level_predictor, name='sea_level_predictor'),
]
