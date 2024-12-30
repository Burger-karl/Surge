from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.urls import reverse
from .models import Payment
from subscriptions.models import SubscriptionPlan, UserSubscription
from .paystack_client import PaystackClient
from .serializers import PaymentSerializer
import uuid
from booking.models import Booking
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

paystack_client = PaystackClient()

class CreateSubscriptionPaymentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Create a payment for a subscription plan",
        responses={200: 'Success', 400: 'Failed'},
        tags=['Payment']
    )
    def post(self, request, plan_id):
        plan = get_object_or_404(SubscriptionPlan, id=plan_id)
        user = request.user

        if UserSubscription.objects.filter(user=user, subscription_status='active').exists():
            return Response({'error': 'You already have an active subscription.'}, status=status.HTTP_400_BAD_REQUEST)

        amount = int(plan.price * 100)  # Paystack expects amount in kobo
        email = user.email
        subscription_code = str(uuid.uuid4())

        user_subscription = UserSubscription.objects.create(
            user=user,
            plan=plan,
            start_date=timezone.now(),
            end_date=timezone.now() + plan.duration,
            is_active=False,
            payment_completed=False,
            subscription_status='pending',
            subscription_code=subscription_code
        )

        callback_url = request.build_absolute_uri(reverse('verify-payment', kwargs={'ref': subscription_code}))

        response = paystack_client.initialize_transaction(email, amount, subscription_code, callback_url)

        if response['status']:
            return Response({'authorization_url': response['data']['authorization_url']}, status=status.HTTP_200_OK)
        else:
            user_subscription.delete()
            return Response({'error': 'Payment initialization failed.'}, status=status.HTTP_400_BAD_REQUEST)

class VerifyPaymentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Verify a subscription payment",
        responses={200: 'Payment Verified', 400: 'Payment Failed'},
        tags=['Payment']
    )
    def get(self, request, ref):
        response = paystack_client.verify_transaction(ref)

        if response['status'] and response['data']['status'] == 'success':
            user_subscription = get_object_or_404(UserSubscription, subscription_code=ref)
            user_subscription.payment_completed = True
            user_subscription.is_active = True
            user_subscription.subscription_status = 'active'
            user_subscription.save()

            Payment.objects.create(
                user=request.user,
                subscription=user_subscription.plan,
                amount=user_subscription.plan.price,
                ref=ref,
                email=request.user.email,
                verified=True
            )

            return Response({'message': 'Subscription Payment successful'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Payment verification failed.'}, status=status.HTTP_400_BAD_REQUEST)


class CreateBookingPaymentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Create a payment for a booking",
        responses={200: 'Success', 400: 'Failed'},
        tags=['Payment']
    )
    def post(self, request, booking_id):
        # Fetch the booking object or return 404
        booking = get_object_or_404(Booking, id=booking_id)
        user = request.user

        # Check if the payment is already completed
        if booking.payment_completed:
            return Response({'error': 'Payment already completed for this booking.'}, status=status.HTTP_400_BAD_REQUEST)

        # Ensure the total_delivery_cost is not None
        if not booking.total_delivery_cost:
            return Response({'error': 'Total delivery cost is not calculated for this booking.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            amount = int(booking.total_delivery_cost * 100)  # Convert amount to kobo
            email = user.email
            booking_code = str(uuid.uuid4())  # Generate a unique booking code

            # Update the booking with the new booking code
            booking.payment_completed = False
            booking.booking_code = booking_code
            booking.save()

            # Generate callback URL
            callback_url = request.build_absolute_uri(reverse('verify-booking-payment', kwargs={'ref': booking_code}))

            # Call Paystack API for payment initialization
            response = paystack_client.initialize_transaction(email, amount, booking_code, callback_url)

            if response.get('status'):
                return Response(
                    {'authorization_url': response['data']['authorization_url'], 'booking_code': booking.booking_code},
                    status=status.HTTP_200_OK
                )
            else:
                booking.booking_code = None
                booking.save()
                return Response({'error': 'Payment initialization failed.'}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)



class VerifyBookingPaymentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Verify a booking payment",
        responses={200: 'Payment Verified', 400: 'Payment Failed'},
        tags=['Payment']
    )
    def get(self, request, ref):
        response = paystack_client.verify_transaction(ref)

        if response['status'] and response['data']['status'] == 'success':
            booking = get_object_or_404(Booking, booking_code=ref)
            booking.payment_completed = True
            booking.booking_status = 'active'
            booking.save()

            Payment.objects.create(
                user=request.user,
                booking=booking,
                amount=booking.delivery_cost,
                ref=ref,
                email=request.user.email,
                verified=True
            )

            return Response({'message': 'Booking Payment successful'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Payment verification failed.'}, status=status.HTTP_400_BAD_REQUEST)


class PaymentHistoryView(ListAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get payment history",
        responses={200: PaymentSerializer(many=True)},
        tags=['Payment']
    )
    def get_queryset(self):
        user = self.request.user
        return Payment.objects.filter(user=user).order_by('-created_at')
