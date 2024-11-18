from rest_framework.views import APIView
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import MultiPartParser, FormParser
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Truck, Booking
from django.shortcuts import get_object_or_404
from .serializers import TruckSerializer, BookingSerializer
from users.models import User
from subscriptions.models import UserSubscription, SubscriptionPlan


class TruckCreateView(generics.CreateAPIView):
    queryset = Truck.objects.all()
    serializer_class = TruckSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    @swagger_auto_schema(
        operation_description="Truck owner uploads a truck",
        responses={201: TruckSerializer(), 403: "Only truck owners can upload trucks"}
    )
    def perform_create(self, serializer):
        user = self.request.user
        if user.user_type == 'truck_owner':
            serializer.save(owner=user)
        else:
            raise PermissionDenied("Only truck owners can upload trucks.")


class TruckListView(generics.ListAPIView):
    queryset = Truck.objects.filter(available=True)
    serializer_class = TruckSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="List all available trucks for clients or list trucks for a specific truck owner",
        responses={200: TruckSerializer(many=True)}
    )
    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'truck_owner':
            return Truck.objects.filter(owner=user)
        return Truck.objects.filter(available=True)


class BookingCreateView(generics.CreateAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Client creates a booking for a truck",
        responses={
            201: BookingSerializer(),
            403: "Only clients with active paid subscriptions can book trucks"
        }
    )
    def perform_create(self, serializer):
        user = self.request.user

        # Ensure only clients can make a booking
        if user.user_type != 'client':
            raise PermissionDenied("Only clients can book trucks.")

        # Retrieve the active subscription for the user, excluding the 'free' plan
        active_subscription = UserSubscription.objects.filter(
            user=user,
            subscription_status='active',
            is_active=True
        ).exclude(plan__name=SubscriptionPlan.FREE).first()

        if not active_subscription:
            raise PermissionDenied("You must have an active paid subscription to book a truck.")

        # Determine the insurance payment based on the subscription plan
        if active_subscription.plan.name == SubscriptionPlan.PREMIUM:
            insurance_payment = 150000  # Insurance payment for premium clients
        else:
            insurance_payment = 0  # No insurance payment for basic clients

        # Save the booking with the calculated insurance payment
        booking = serializer.save(client=user, insurance_payment=insurance_payment)

        # Calculate the total delivery cost for premium clients
        if active_subscription.plan.name == SubscriptionPlan.PREMIUM:
            booking.total_delivery_cost = booking.delivery_cost + insurance_payment
        else:
            booking.total_delivery_cost = booking.delivery_cost  # For basic clients, total delivery cost is the same as delivery cost

        # Save the total delivery cost to the booking
        booking.save()


class BookingListView(generics.ListAPIView):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="List all bookings for the client or truck owner",
        responses={200: BookingSerializer(many=True)}
    )
    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'client':
            return Booking.objects.filter(client=user)
        elif user.user_type == 'truck_owner':
            return Booking.objects.filter(truck__owner=user)
        return Booking.objects.none()


class GenerateReceiptView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Generate a receipt for a booking",
        responses={
            200: "Receipt data returned",
            403: "You do not have permission to view this receipt"
        }
    )
    def get(self, request, booking_code):
        booking = get_object_or_404(Booking, booking_code=booking_code)
        user = request.user

        if booking.client != user:
            return Response({'error': 'You do not have permission to view this receipt.'}, status=status.HTTP_403_FORBIDDEN)

        truck_name = booking.truck.name  # Use truck name instead of truck ID

        receipt_data = {
            'client_name': booking.client.username,
            'truck_name': truck_name,  # Use the truck name
            'product_name': booking.product_name,
            'product_weight': booking.product_weight,
            'product_value': booking.product_value,
            'pickup_state': booking.pickup_state,
            'destination_state': booking.destination_state,
            'delivery_cost': booking.delivery_cost,
            'insurance_payment': booking.insurance_payment,
            'total_delivery_cost': booking.total_delivery_cost,
            'booked_at': booking.booked_at
        }

        return Response(receipt_data, status=status.HTTP_200_OK)


# Superuser-specific views

class TruckUpdateAvailabilityView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Superuser updates truck availability to true",
        responses={200: "Truck availability updated", 404: "Truck not found"}
    )
    def post(self, request, pk):
        if not request.user.is_superuser:
            raise PermissionDenied("Only superusers can update truck availability.")
        
        try:
            truck = Truck.objects.get(pk=pk)
        except Truck.DoesNotExist:
            return Response({"detail": "Truck not found."}, status=404)
        
        truck.available = True
        truck.save()
        return Response({"detail": "Truck availability updated to true."})


class BookingUpdateDeliveryCostView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Superuser updates the delivery cost of a booking",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'delivery_cost': openapi.Schema(type=openapi.TYPE_NUMBER, description='New delivery cost'),
            },
            required=['delivery_cost'],
        ),
        responses={200: "Booking delivery cost updated", 404: "Booking not found"}
    )
    def post(self, request, pk):
        if not request.user.is_superuser:
            raise PermissionDenied("Only superusers can update delivery cost.")
        
        try:
            booking = Booking.objects.get(pk=pk)
        except Booking.DoesNotExist:
            return Response({"detail": "Booking not found."}, status=404)

        delivery_cost = request.data.get("delivery_cost")
        if delivery_cost is None:
            return Response({"detail": "Delivery cost is required."}, status=400)

        booking.delivery_cost = delivery_cost
        booking.save()
        return Response({"detail": "Booking delivery cost updated."})


class BookingAdminUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Superuser updates the delivery cost and total delivery cost of a booking",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'delivery_cost': openapi.Schema(type=openapi.TYPE_NUMBER, description='New delivery cost'),
            },
            required=['delivery_cost'],
        ),
        responses={200: "Booking details updated", 404: "Booking not found"}
    )
    def post(self, request, pk):
        if not request.user.is_superuser:
            raise PermissionDenied("Only superusers can update booking details.")

        try:
            booking = Booking.objects.get(pk=pk)
        except Booking.DoesNotExist:
            return Response({"detail": "Booking not found."}, status=404)

        delivery_cost = request.data.get("delivery_cost")
        if delivery_cost is None:
            return Response({"detail": "Delivery cost is required."}, status=400)

        # Update delivery cost
        booking.delivery_cost = delivery_cost

        # Update total delivery cost (insurance + delivery cost) if applicable
        if booking.insurance_payment > 0:
            booking.total_delivery_cost = booking.insurance_payment + delivery_cost
        booking.save()

        return Response({"detail": "Booking delivery cost and total delivery cost updated."})


class BookingAdminListView(generics.ListAPIView):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Superuser views all bookings with client subscription details",
        responses={200: "List of all bookings with subscription details", 403: "Permission denied"}
    )
    def get_queryset(self):
        if not self.request.user.is_superuser:
            raise PermissionDenied("Only superusers can view all bookings.")
        return Booking.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        response_data = []

        for booking in queryset:
            # Get client subscription details
            client_subscription = UserSubscription.objects.filter(
                user=booking.client, subscription_status='active', is_active=True
            ).first()
            client_subscription_name = client_subscription.plan.name if client_subscription else "No active subscription"

            # Prepare booking data with client subscription details
            booking_data = {
                "booking_details": BookingSerializer(booking).data,
                "client_details": {
                    "username": booking.client.username,
                    "email": booking.client.email,
                    "current_subscription_plan": client_subscription_name,
                },
            }
            response_data.append(booking_data)

        return Response(response_data, status=status.HTTP_200_OK)
