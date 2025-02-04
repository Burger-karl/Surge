from django.urls import path
from .views import (
    TruckCreateView, TruckListView, BookingCreateView, BookingListView, 
    TruckUpdateAvailabilityView, BookingUpdateDeliveryCostView, BookingAdminListView, 
    GenerateReceiptView, TruckOwnerTrucksView, PendingTrucksListView, AllTrucksView,
    TruckDeleteView
)

urlpatterns = [
    path('trucks/', TruckListView.as_view(), name='truck-list'),
    path('trucks/upload/', TruckCreateView.as_view(), name='truck-upload'),
    path('trucks/my-trucks/', TruckOwnerTrucksView.as_view(), name='my-trucks'),
    path('bookings/', BookingListView.as_view(), name='booking-list'),
    path('bookings/create/', BookingCreateView.as_view(), name='booking-create'),
    path('bookings/<str:booking_code>/receipt/', GenerateReceiptView.as_view(), name='generate-receipt'),
    path('trucks/all/', AllTrucksView.as_view(), name='all-trucks'),
    path('trucks/<int:pk>/delete/', TruckDeleteView.as_view(), name='delete-truck'),

    # For Superuser
    path('bookings/admin/', BookingAdminListView.as_view(), name='admin-booking-list'),  # View all bookings
    # path('bookings/<int:pk>/admin-update/', BookingAdminUpdateView.as_view(), name='admin-booking-update'),  # Update delivery cost and total cost
    path('bookings/<int:pk>/update-delivery-cost/', BookingUpdateDeliveryCostView.as_view(), name='booking-update-delivery-cost'),
    path('trucks/<int:pk>/update-availability/', TruckUpdateAvailabilityView.as_view(), name='truck-update-availability'),
    path('trucks/pending/', PendingTrucksListView.as_view(), name='pending-trucks'),
]
