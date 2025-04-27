# tracker/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Home page
    path('manage_budget/', views.create_or_edit_budget, name='manage_budget'),
    path('signup/', views.signup, name='signup'),  # Signup page
    path('dashboard/', views.dashboard, name='dashboard'),  # Dashboard page
    path('logout/', views.logout_view, name='logout'),  # Logout functionality
    path('transactions/', views.transaction_list, name='transaction_list'),
    path('create_transaction/', views.create_transaction, name='create_transaction'),
    path('delete_transaction/<int:pk>/', views.delete_transaction, name='delete_transaction'),
    path('create_category/', views.create_category, name='create_category'),
    path('summary/', views.summary_view, name='summary'),
    path('transaction_summary/', views.transaction_summary, name='transaction_summary'),
]
