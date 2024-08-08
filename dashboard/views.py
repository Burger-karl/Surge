from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from users.models import User
from subscriptions.models import UserSubscription
from booking.models import Booking
from delivery.models import DeliverySchedule, DeliveryHistory
from .serializers import (
    UserProfileSerializer, 
    SubscriptionSerializer, 
    UnpaidBookingSerializer, 
    DeliveryScheduleSerializer, 
    DeliveryHistorySerializer
)

# Create your views here.

class ClientDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Profile details
        profile_data = UserProfileSerializer(user).data

        # Current subscription details
        try:
            subscription = UserSubscription.objects.get(user=user, subscription_status='active')
            subscription_data = SubscriptionSerializer(subscription).data
        except UserSubscription.DoesNotExist:
            subscription_data = None

        # Unpaid bookings
        unpaid_bookings = Booking.objects.filter(client=user, booking_status='inactive')
        unpaid_bookings_data = UnpaidBookingSerializer(unpaid_bookings, many=True).data

        # Delivery schedules
        delivery_schedules = DeliverySchedule.objects.filter(booking__client=user)
        delivery_schedules_data = DeliveryScheduleSerializer(delivery_schedules, many=True).data

        # Delivery histories
        delivery_histories = DeliveryHistory.objects.filter(booking__client=user)
        delivery_histories_data = DeliveryHistorySerializer(delivery_histories, many=True).data

        response_data = {
            'profile': profile_data,
            'subscription': subscription_data,
            'unpaid_bookings': unpaid_bookings_data,
            'delivery_schedules': delivery_schedules_data,
            'delivery_histories': delivery_histories_data,
        }

        return Response(response_data, status=200)
    


# dashboard/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from users.models import User
from booking.models import Booking, Truck
from .serializers import (
    UserProfileSerializer,
    TruckSerializer,
    BookingSerializer
)

class TruckOwnerDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Profile details
        profile_data = UserProfileSerializer(user).data

        # Pending trucks
        pending_trucks = Truck.objects.filter(owner=user, available=False)
        pending_trucks_data = TruckSerializer(pending_trucks, many=True).data

        # Available trucks
        available_trucks = Truck.objects.filter(owner=user, available=True)
        available_trucks_data = TruckSerializer(available_trucks, many=True).data

        # Trucks that have been successfully booked and paid for by a client
        booked_trucks = Booking.objects.filter(truck__owner=user, booking_status='active', payment_completed=True)
        booked_trucks_data = BookingSerializer(booked_trucks, many=True).data

        response_data = {
            'profile': profile_data,
            'pending_trucks': pending_trucks_data,
            'available_trucks': available_trucks_data,
            'booked_trucks': booked_trucks_data,
        }

        return Response(response_data, status=200)



