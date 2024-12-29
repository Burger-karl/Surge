from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from datetime import datetime

from .models import DeliverySchedule, DeliveryHistory, DeliveryDocument
from .serializers import DeliveryScheduleSerializer, DeliveryHistorySerializer, DeliveryDocumentSerializer
from booking.models import Booking


class DeliveryScheduleCreateView(generics.CreateAPIView):
    queryset = DeliverySchedule.objects.all()
    serializer_class = DeliveryScheduleSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Create a new delivery schedule for a confirmed booking.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['booking_id'],
            properties={
                'booking_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the confirmed booking'),
            },
        ),
        responses={
            201: openapi.Response('Delivery schedule created successfully.'),
            400: openapi.Response('Booking not confirmed or paid for.'),
            404: openapi.Response('Booking not found.'),
        }
    )
    def create(self, request, *args, **kwargs):
        booking_id = self.request.data.get('booking_id')
        if not booking_id:
            return Response({"detail": "booking_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            booking = Booking.objects.get(id=booking_id)
        except Booking.DoesNotExist:
            return Response({"detail": "Booking not found."}, status=status.HTTP_404_NOT_FOUND)

        if booking.booking_status != 'active' or not booking.payment_completed:
            return Response({"detail": "Booking is not confirmed or paid for."}, status=status.HTTP_400_BAD_REQUEST)

        scheduled_date = datetime.now().date()

        delivery_schedule = DeliverySchedule.objects.create(
            booking=booking,
            scheduled_date=scheduled_date
        )

        DeliveryHistory.objects.create(
            booking=booking,
            delivery_date=scheduled_date,
            status='pending'
        )

        response_data = {
            'truck_name': booking.truck.name,
            'product_name': booking.product_name,
            'total_delivery_cost': booking.total_delivery_cost,
            'destination_address': booking.destination_state,
            'scheduled_date': delivery_schedule.scheduled_date,
            'status': delivery_schedule.status
        }

        return Response(response_data, status=status.HTTP_201_CREATED)


class DeliveryScheduleListView(generics.ListAPIView):
    serializer_class = DeliveryScheduleSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="List all active delivery schedules for the authenticated client.",
        responses={200: DeliveryScheduleSerializer(many=True)}
    )
    def get_queryset(self):
        user = self.request.user
        return DeliverySchedule.objects.filter(booking__client=user, booking__booking_status='active')


class DeliveryHistoryView(generics.ListAPIView):
    serializer_class = DeliveryHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="List all delivery histories for the authenticated client with status 'delivered'.",
        responses={200: DeliveryHistorySerializer(many=True)}
    )
    def get_queryset(self):
        """
        Return delivery histories with status 'delivered' for the authenticated user.
        """
        user = self.request.user
        return DeliveryHistory.objects.filter(
            booking__client=user,
            status='delivered'
        )



class DeliveryDocumentView(generics.ListAPIView):
    queryset = DeliveryDocument.objects.all()
    serializer_class = DeliveryDocumentSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="List all delivery documents available for the authenticated user.",
        responses={200: DeliveryDocumentSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class UpdateDeliveryScheduleStatusView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Update the status of a delivery schedule to 'delivered'. Only superusers can perform this action.",
        responses={
            200: openapi.Response('Delivery schedule status updated to delivered.'),
            403: openapi.Response('Only superusers can update delivery status.'),
            404: openapi.Response('Delivery schedule not found.')
        }
    )
    def post(self, request, pk):
        if not request.user.is_superuser:
            raise PermissionDenied("Only superusers can update delivery status.")
        
        try:
            delivery_schedule = DeliverySchedule.objects.get(pk=pk)
        except DeliverySchedule.DoesNotExist:
            return Response({"detail": "Delivery schedule not found."}, status=status.HTTP_404_NOT_FOUND)
        
        delivery_schedule.status = 'delivered'
        delivery_schedule.save()

        # Update the corresponding DeliveryHistory status
        delivery_history = DeliveryHistory.objects.filter(booking=delivery_schedule.booking).first()
        if delivery_history:
            delivery_history.status = 'delivered'
            delivery_history.delivery_date = datetime.now().date()
            delivery_history.save()

        return Response({"detail": "Delivery schedule status updated to delivered."}, status=status.HTTP_200_OK)
