from rest_framework.views import APIView
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Truck, Booking
from .serializers import TruckSerializer, BookingSerializer
from users.models import User
from subscriptions.models import UserSubscription

class TruckCreateView(generics.CreateAPIView):
    queryset = Truck.objects.all()
    serializer_class = TruckSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

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

    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'truck_owner':
            return Truck.objects.filter(owner=user)
        return Truck.objects.filter(available=True)


class BookingCreateView(generics.CreateAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        if user.user_type != 'client':
            raise PermissionDenied("Only clients can book trucks.")

        # Check if the client has an active subscription (excluding free subscription)
        active_subscription = UserSubscription.objects.filter(
            user=user,
            subscription_status='active',
            is_active=True
        ).exclude(plan__name='free').exists()

        if not active_subscription:
            raise PermissionDenied("You must have an active paid subscription to book a truck.")

        serializer.save(client=user)


class BookingListView(generics.ListAPIView):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'client':
            return Booking.objects.filter(client=user)
        elif user.user_type == 'truck_owner':
            return Booking.objects.filter(truck__owner=user)
        return Booking.objects.none()

# FOR SUPERUSER

class TruckUpdateAvailabilityView(APIView):
    permission_classes = [permissions.IsAuthenticated]

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
