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


paystack_client = PaystackClient()

class CreateSubscriptionPaymentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

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
        

import logging

logger = logging.getLogger(__name__)


class VerifyPaymentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, ref):
        response = paystack_client.verify_transaction(ref)

        # Log the response for debugging
        logger.debug('Paystack verification response: %s', response)

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

            return Response({'message': 'Payment successful'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Payment verification failed.'}, status=status.HTTP_400_BAD_REQUEST)


class CreateBookingPaymentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, booking_id):
        booking = get_object_or_404(Booking, id=booking_id)
        user = request.user

        if booking.payment_completed:
            return Response({'error': 'Payment already completed for this booking.'}, status=status.HTTP_400_BAD_REQUEST)

        amount = int(booking.delivery_cost * 100)  # Paystack expects amount in kobo
        email = user.email
        booking_code = str(uuid.uuid4())

        booking.payment_completed = False
        booking.booking_code = booking_code
        booking.save()

        callback_url = request.build_absolute_uri(reverse('verify-booking-payment', kwargs={'ref': booking_code}))

        response = paystack_client.initialize_transaction(email, amount, booking_code, callback_url)

        if response['status']:
            return Response({'authorization_url': response['data']['authorization_url']}, status=status.HTTP_200_OK)
        else:
            booking.booking_code = None
            booking.save()
            return Response({'error': 'Payment initialization failed.'}, status=status.HTTP_400_BAD_REQUEST)


import logging

logger = logging.getLogger(__name__)


class VerifyBookingPaymentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, ref):
        response = paystack_client.verify_transaction(ref)

        # Log the response for debugging
        logger.debug('Paystack verification response: %s', response)

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

            return Response({'message': 'Payment successful'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Payment verification failed.'}, status=status.HTTP_400_BAD_REQUEST)
