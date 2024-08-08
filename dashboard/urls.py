
from django.urls import path
from .views import ClientDashboardView, TruckOwnerDashboardView

urlpatterns = [
    path('client-dashboard/', ClientDashboardView.as_view(), name='client-dashboard'),
    path('truck-owner-dashboard/', TruckOwnerDashboardView.as_view(), name='truck_owner_dashboard'),
    # path('admin-dashboard/', AdminDashboardView.as_view(), name='admin-dashboard'),
]
