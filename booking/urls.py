from django.urls import path
from .views import (
    TruckCreateView, TruckListView, BookingCreateView, BookingListView, 
    TruckUpdateAvailabilityView, BookingUpdateDeliveryCostView, BookingAdminListView, BookingAdminUpdateView, GenerateReceiptView
)

urlpatterns = [
    path('trucks/', TruckListView.as_view(), name='truck-list'),
    path('trucks/upload/', TruckCreateView.as_view(), name='truck-upload'),
    path('bookings/', BookingListView.as_view(), name='booking-list'),
    path('bookings/create/', BookingCreateView.as_view(), name='booking-create'),
    path('bookings/<str:booking_code>/receipt/', GenerateReceiptView.as_view(), name='generate-receipt'),

    # For Superuser
    path('bookings/admin/', BookingAdminListView.as_view(), name='admin-booking-list'),  # View all bookings
    path('bookings/<int:pk>/admin-update/', BookingAdminUpdateView.as_view(), name='admin-booking-update'),  # Update delivery cost and total cost
    path('bookings/<int:pk>/update-delivery-cost/', BookingUpdateDeliveryCostView.as_view(), name='booking-update-delivery-cost'),
    path('trucks/<int:pk>/update-availability/', TruckUpdateAvailabilityView.as_view(), name='truck-update-availability'),
]
