# tracker/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('add_transaction/', views.add_transaction, name='add_transaction'),
    path('set_budget/', views.set_budget, name='set_budget'),
    path('analytics/', views.analytics, name='analytics'),path('transaction_list/', views.transaction_list, name='transaction_list'),  # <-- NEW
    path('edit_transaction/<int:pk>/', views.edit_transaction, name='edit_transaction'),  # <-- NEW
    path('delete_transaction/<int:pk>/', views.delete_transaction, name='delete_transaction'),  # <-- NEW
    path('transactions/export/', views.export_transactions, name='export_transactions'),
    path('transactions/import/', views.import_transactions, name='import_transactions'),
]