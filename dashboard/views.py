from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from users.models import User
from subscriptions.models import UserSubscription
from booking.models import Booking
from delivery.models import DeliverySchedule, DeliveryHistory
from payment.models import Payment
from payment.serializers import PaymentSerializer
from .serializers import (
    UserProfileSerializer, 
    SubscriptionSerializer, 
    UnpaidBookingSerializer, 
    DeliveryScheduleSerializer, 
    DeliveryHistorySerializer
)

# class ClientDashboardView(APIView):
#     permission_classes = [IsAuthenticated]

#     @swagger_auto_schema(
#         operation_description="Retrieve client dashboard data including profile, subscription, unpaid bookings, delivery schedules, delivery histories, and payment history.",
#         responses={200: "Dashboard data for the client", 403: "Permission denied"}
#     )
#     def get(self, request):
#         user = request.user

#         # Profile details
#         profile_data = UserProfileSerializer(user).data

#         # Current subscription details
#         try:
#             subscription = UserSubscription.objects.get(user=user, subscription_status='active')
#             subscription_data = SubscriptionSerializer(subscription).data
#         except UserSubscription.DoesNotExist:
#             subscription_data = None

#         # Unpaid bookings
#         unpaid_bookings = Booking.objects.filter(client=user, booking_status='inactive')
#         unpaid_bookings_data = UnpaidBookingSerializer(unpaid_bookings, many=True).data

#         # Delivery schedules
#         delivery_schedules = DeliverySchedule.objects.filter(booking__client=user)
#         delivery_schedules_data = DeliveryScheduleSerializer(delivery_schedules, many=True).data

#         # Delivery histories
#         delivery_histories = DeliveryHistory.objects.filter(booking__client=user)
#         delivery_histories_data = DeliveryHistorySerializer(delivery_histories, many=True).data

#         # Payment history
#         payment_history = Payment.objects.filter(user=user).order_by('-date_created')
#         payment_history_data = []
#         for payment in payment_history:
#             payment_data = PaymentSerializer(payment).data
#             if payment.subscription:
#                 payment_data['payment_for'] = 'Subscription'
#                 payment_data['subscription_plan'] = payment.subscription.name
#             elif payment.booking:
#                 payment_data['payment_for'] = 'Booking'
#                 payment_data['booking_details'] = {
#                     'truck_name': payment.booking.truck.name,
#                     'product_name': payment.booking.product_name,
#                     'pickup_state': payment.booking.pickup_state,
#                     'destination_state': payment.booking.destination_state,
#                     'delivery_cost': payment.booking.delivery_cost,
#                     'insurance_payment': payment.booking.insurance_payment,
#                     'total_delivery_cost': payment.booking.total_delivery_cost,
#                 }
#             payment_history_data.append(payment_data)

#         response_data = {
#             'profile': profile_data,
#             'subscription': subscription_data,
#             'unpaid_bookings': unpaid_bookings_data,
#             'delivery_schedules': delivery_schedules_data,
#             'delivery_histories': delivery_histories_data,
#             'payment_history': payment_history_data,
#         }

#         return Response(response_data, status=200)


class ClientDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Retrieve client dashboard data including profile, subscription, unpaid bookings, delivery schedules, delivery histories, and payment history.",
        responses={200: "Dashboard data for the client", 403: "Permission denied"}
    )
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
        unpaid_bookings = Booking.objects.filter(
            client=user,
            booking_status='inactive',
            delivery_cost__isnull=True  # Delivery cost not assigned
        ) | Booking.objects.filter(
            client=user,
            booking_status='inactive',
            delivery_cost__isnull=False,
            payment_completed=False  # Delivery cost assigned but payment not completed
        )
        unpaid_bookings_data = UnpaidBookingSerializer(unpaid_bookings, many=True).data

        # Delivery schedules
        delivery_schedules = DeliverySchedule.objects.filter(booking__client=user)
        delivery_schedules_data = DeliveryScheduleSerializer(delivery_schedules, many=True).data

        # Delivery histories
        delivery_histories = DeliveryHistory.objects.filter(booking__client=user)
        delivery_histories_data = DeliveryHistorySerializer(delivery_histories, many=True).data

        # Payment history
        payment_history = Payment.objects.filter(user=user).order_by('-date_created')
        payment_history_data = []
        for payment in payment_history:
            payment_data = PaymentSerializer(payment).data
            if payment.subscription:
                payment_data['payment_for'] = 'Subscription'
                payment_data['subscription_plan'] = payment.subscription.name
            elif payment.booking:
                payment_data['payment_for'] = 'Booking'
                payment_data['booking_details'] = {
                    'truck_name': payment.booking.truck.name,
                    'product_name': payment.booking.product_name,
                    'pickup_state': payment.booking.pickup_state,
                    'destination_state': payment.booking.destination_state,
                    'delivery_cost': payment.booking.delivery_cost,
                    'insurance_payment': payment.booking.insurance_payment,
                    'total_delivery_cost': payment.booking.total_delivery_cost,
                }
            payment_history_data.append(payment_data)

        response_data = {
            'profile': profile_data,
            'subscription': subscription_data,
            'unpaid_bookings': unpaid_bookings_data,
            'delivery_schedules': delivery_schedules_data,
            'delivery_histories': delivery_histories_data,
            'payment_history': payment_history_data,
        }

        return Response(response_data, status=200)


# Truck Owner Dashboard
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from users.models import User
from booking.models import Booking, Truck
from .serializers import (
    UserProfileSerializer,
    TruckSerializer,
    BookingSerializer
)

class TruckOwnerDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Retrieve truck owner's dashboard data including profile, pending trucks, available trucks, and booked trucks.",
        responses={200: "Dashboard data for the truck owner", 403: "Permission denied"}
    )
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


