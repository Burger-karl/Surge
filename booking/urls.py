from django.urls import path
from .views import TruckCreateView, TruckListView, BookingCreateView, BookingListView, TruckUpdateAvailabilityView, BookingUpdateDeliveryCostView

urlpatterns = [
    path('trucks/', TruckListView.as_view(), name='truck-list'),
    path('trucks/upload/', TruckCreateView.as_view(), name='truck-upload'),
    path('bookings/', BookingListView.as_view(), name='booking-list'),
    path('bookings/create/', BookingCreateView.as_view(), name='booking-create'),

    # For Superuser
    path('bookings/<int:pk>/update-delivery-cost/', BookingUpdateDeliveryCostView.as_view(), name='booking-update-delivery-cost'),
    path('trucks/<int:pk>/update-availability/', TruckUpdateAvailabilityView.as_view(), name='truck-update-availability'),
]
