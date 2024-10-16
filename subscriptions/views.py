# from rest_framework import status, permissions, generics
# from rest_framework.response import Response
# from django.shortcuts import get_object_or_404
# from django.utils import timezone
# from django.urls import reverse
# from .models import SubscriptionPlan, UserSubscription
# from payment.models import Payment
# from payment.paystack_client import PaystackClient
# from .serializers import SubscriptionPlanSerializer, UserSubscriptionSerializer
# import uuid

# paystack_client = PaystackClient()

# class SubscriptionPlanListView(generics.ListAPIView):
#     queryset = SubscriptionPlan.objects.all()
#     serializer_class = SubscriptionPlanSerializer
#     permission_classes = [permissions.IsAuthenticated]


# class UserSubscriptionListView(generics.ListAPIView):
#     serializer_class = UserSubscriptionSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     def get_queryset(self):
#         return UserSubscription.objects.filter(user=self.request.user)


# class SubscribeView(generics.CreateAPIView):
#     serializer_class = UserSubscriptionSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     def post(self, request, pk):
#         user = request.user
#         if user.user_type != 'client':
#             return Response({'error': 'Only clients can subscribe.'}, status=status.HTTP_403_FORBIDDEN)
        
#         plan = get_object_or_404(SubscriptionPlan, pk=pk)
#         existing_subscription = UserSubscription.objects.filter(user=user).first()

#         if existing_subscription:
#             if existing_subscription.is_active and existing_subscription.plan.name in [SubscriptionPlan.BASIC, SubscriptionPlan.PREMIUM]:
#                 return Response({'error': 'You already have an active subscription.'}, status=status.HTTP_400_BAD_REQUEST)
#             else:
#                 existing_subscription.plan = plan
#                 existing_subscription.start_date = timezone.now()
#                 existing_subscription.end_date = timezone.now() + plan.duration if plan.name != SubscriptionPlan.FREE else None
#                 existing_subscription.is_active = False
#                 existing_subscription.payment_completed = False
#                 existing_subscription.subscription_status = 'pending'
#                 existing_subscription.subscription_code = str(uuid.uuid4())
#                 existing_subscription.save()

#                 callback_url = request.build_absolute_uri(reverse('payment-callback', kwargs={'ref': existing_subscription.subscription_code}))
#                 response = paystack_client.initialize_transaction(user.email, int(plan.price * 100), existing_subscription.subscription_code, callback_url)

#                 if response['status']:
#                     return Response({'authorization_url': response['data']['authorization_url'], 'subscription_code': existing_subscription.subscription_code}, status=status.HTTP_200_OK)
#                 else:
#                     existing_subscription.delete()
#                     return Response({'error': 'Payment initialization failed.'}, status=status.HTTP_400_BAD_REQUEST)
#         else:
#             user_subscription = UserSubscription.objects.create(
#                 user=user,
#                 plan=plan,
#                 start_date=timezone.now(),
#                 end_date=timezone.now() + plan.duration if plan.name != SubscriptionPlan.FREE else None,
#                 is_active=False,
#                 payment_completed=False,
#                 subscription_status='pending',
#                 subscription_code=str(uuid.uuid4())
#             )

#             callback_url = request.build_absolute_uri(reverse('payment-callback', kwargs={'ref': user_subscription.subscription_code}))
#             response = paystack_client.initialize_transaction(user.email, int(plan.price * 100), user_subscription.subscription_code, callback_url)

#             if response['status']:
#                 return Response({'authorization_url': response['data']['authorization_url'], 'subscription_code': user_subscription.subscription_code}, status=status.HTTP_200_OK)
#             else:
#                 user_subscription.delete()
#                 return Response({'error': 'Payment initialization failed.'}, status=status.HTTP_400_BAD_REQUEST)


# class PaymentCallbackView(generics.GenericAPIView):
#     permission_classes = [permissions.IsAuthenticated]

#     def get(self, request, ref):
#         response = paystack_client.verify_transaction(ref)

#         if response['status'] and response['data']['status'] == 'success':
#             user_subscription = get_object_or_404(UserSubscription, subscription_code=ref)
#             user_subscription.payment_completed = True
#             user_subscription.is_active = True
#             user_subscription.subscription_status = 'active'
#             user_subscription.save()

#             Payment.objects.create(
#                 user=request.user,
#                 subscription=user_subscription.plan,
#                 amount=user_subscription.plan.price,
#                 ref=ref,
#                 email=request.user.email,
#                 verified=True
#             )

#             # If the plan is upgraded to premium, update the subscription type
#             if user_subscription.plan.name == SubscriptionPlan.PREMIUM:
#                 user_subscription.subscription_type = SubscriptionPlan.PREMIUM
#                 user_subscription.save()

#             return Response({'message': 'Payment successful'}, status=status.HTTP_200_OK)
#         else:
#             return Response({'error': 'Payment verification failed.'}, status=status.HTTP_400_BAD_REQUEST)


# class RenewSubscriptionView(generics.CreateAPIView):
#     permission_classes = [permissions.IsAuthenticated]

#     def post(self, request):
#         user = request.user
#         if user.user_type != 'client':
#             return Response({'error': 'Only clients can renew subscriptions.'}, status=status.HTTP_403_FORBIDDEN)

#         user_subscription = get_object_or_404(UserSubscription, user=user, is_active=True)
#         plan = user_subscription.plan

#         user_subscription.end_date = user_subscription.end_date + plan.duration
#         user_subscription.is_active = False
#         user_subscription.payment_completed = False
#         user_subscription.subscription_status = 'pending'
#         user_subscription.subscription_code = str(uuid.uuid4())
#         user_subscription.save()

#         callback_url = request.build_absolute_uri(reverse('payment-callback', kwargs={'ref': user_subscription.subscription_code}))
#         response = paystack_client.initialize_transaction(user.email, int(plan.price * 100), user_subscription.subscription_code, callback_url)

#         if response['status']:
#             return Response({'authorization_url': response['data']['authorization_url'], 'subscription_code': user_subscription.subscription_code}, status=status.HTTP_200_OK)
#         else:
#             user_subscription.delete()
#             return Response({'error': 'Payment initialization failed.'}, status=status.HTTP_400_BAD_REQUEST)


# class UpgradeSubscriptionView(generics.CreateAPIView):
#     permission_classes = [permissions.IsAuthenticated]

#     def post(self, request, pk):
#         user = request.user
#         if user.user_type != 'client':
#             return Response({'error': 'Only clients can upgrade subscriptions.'}, status=status.HTTP_403_FORBIDDEN)

#         plan = get_object_or_404(SubscriptionPlan, pk=pk)
#         user_subscription = get_object_or_404(UserSubscription, user=user, is_active=True)

#         if user_subscription.plan.name == SubscriptionPlan.PREMIUM:
#             return Response({'error': 'You already have the highest subscription plan.'}, status=status.HTTP_400_BAD_REQUEST)

#         user_subscription.plan = plan
#         user_subscription.end_date = timezone.now() + plan.duration
#         user_subscription.is_active = False
#         user_subscription.payment_completed = False
#         user_subscription.subscription_status = 'pending'
#         user_subscription.subscription_code = str(uuid.uuid4())
#         user_subscription.save()

#         callback_url = request.build_absolute_uri(reverse('payment-callback', kwargs={'ref': user_subscription.subscription_code}))
#         response = paystack_client.initialize_transaction(user.email, int(plan.price * 100), user_subscription.subscription_code, callback_url)

#         if response['status']:
#             return Response({'authorization_url': response['data']['authorization_url'], 'subscription_code': user_subscription.subscription_code}, status=status.HTTP_200_OK)
#         else:
#             user_subscription.delete()
#             return Response({'error': 'Payment initialization failed.'}, status=status.HTTP_400_BAD_REQUEST)


# class CancelSubscriptionView(generics.DestroyAPIView):
#     permission_classes = [permissions.IsAuthenticated]

#     def delete(self, request):
#         user = request.user
#         if user.user_type != 'client':
#             return Response({'error': 'Only clients can cancel subscriptions.'}, status=status.HTTP_403_FORBIDDEN)

#         user_subscription = get_object_or_404(UserSubscription, user=user, is_active=True)
#         user_subscription.deactivate_subscription()

#         # Change the subscription type to free when the client subscription is canceled
#         free_plan = get_object_or_404(SubscriptionPlan, name=SubscriptionPlan.FREE)
#         user_subscription.plan = free_plan
#         user_subscription.is_active = False
#         user_subscription.subscription_status = 'inactive'
#         user_subscription.save()

#         return Response({'message': 'Subscription canceled successfully.'}, status=status.HTTP_200_OK)





from rest_framework import status, permissions, generics
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.urls import reverse
from .models import SubscriptionPlan, UserSubscription
from payment.models import Payment
from payment.paystack_client import PaystackClient
from .serializers import SubscriptionPlanSerializer, UserSubscriptionSerializer
import uuid
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

paystack_client = PaystackClient()

class SubscriptionPlanListView(generics.ListAPIView):
    queryset = SubscriptionPlan.objects.all()
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="List all available subscription plans.",
        responses={200: SubscriptionPlanSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class UserSubscriptionListView(generics.ListAPIView):
    serializer_class = UserSubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="List the current user's subscriptions.",
        responses={200: UserSubscriptionSerializer(many=True)}
    )
    def get_queryset(self):
        return UserSubscription.objects.filter(user=self.request.user)


class SubscribeView(generics.CreateAPIView):
    serializer_class = UserSubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Subscribe to a new plan",
        responses={
            200: openapi.Response('Subscription created and payment initialized.', UserSubscriptionSerializer),
            400: 'Bad request or payment initialization failed.',
            403: 'Forbidden for non-client users.'
        }
    )
    def post(self, request, pk):
        user = request.user
        if user.user_type != 'client':
            return Response({'error': 'Only clients can subscribe.'}, status=status.HTTP_403_FORBIDDEN)
        
        plan = get_object_or_404(SubscriptionPlan, pk=pk)
        existing_subscription = UserSubscription.objects.filter(user=user).first()

        if existing_subscription:
            if existing_subscription.is_active and existing_subscription.plan.name in [SubscriptionPlan.BASIC, SubscriptionPlan.PREMIUM]:
                return Response({'error': 'You already have an active subscription.'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                existing_subscription.plan = plan
                existing_subscription.start_date = timezone.now()
                existing_subscription.end_date = timezone.now() + plan.duration if plan.name != SubscriptionPlan.FREE else None
                existing_subscription.is_active = False
                existing_subscription.payment_completed = False
                existing_subscription.subscription_status = 'pending'
                existing_subscription.subscription_code = str(uuid.uuid4())
                existing_subscription.save()

                callback_url = request.build_absolute_uri(reverse('payment-callback', kwargs={'ref': existing_subscription.subscription_code}))
                response = paystack_client.initialize_transaction(user.email, int(plan.price * 100), existing_subscription.subscription_code, callback_url)

                if response['status']:
                    return Response({'authorization_url': response['data']['authorization_url'], 'subscription_code': existing_subscription.subscription_code}, status=status.HTTP_200_OK)
                else:
                    existing_subscription.delete()
                    return Response({'error': 'Payment initialization failed.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            user_subscription = UserSubscription.objects.create(
                user=user,
                plan=plan,
                start_date=timezone.now(),
                end_date=timezone.now() + plan.duration if plan.name != SubscriptionPlan.FREE else None,
                is_active=False,
                payment_completed=False,
                subscription_status='pending',
                subscription_code=str(uuid.uuid4())
            )

            callback_url = request.build_absolute_uri(reverse('payment-callback', kwargs={'ref': user_subscription.subscription_code}))
            response = paystack_client.initialize_transaction(user.email, int(plan.price * 100), user_subscription.subscription_code, callback_url)

            if response['status']:
                return Response({'authorization_url': response['data']['authorization_url'], 'subscription_code': user_subscription.subscription_code}, status=status.HTTP_200_OK)
            else:
                user_subscription.delete()
                return Response({'error': 'Payment initialization failed.'}, status=status.HTTP_400_BAD_REQUEST)


class PaymentCallbackView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Verify payment via the callback reference.",
        responses={
            200: 'Payment verified and subscription activated.',
            400: 'Payment verification failed.'
        }
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

            if user_subscription.plan.name == SubscriptionPlan.PREMIUM:
                user_subscription.subscription_type = SubscriptionPlan.PREMIUM
                user_subscription.save()

            return Response({'message': 'Payment successful'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Payment verification failed.'}, status=status.HTTP_400_BAD_REQUEST)


class RenewSubscriptionView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Renew an existing subscription plan.",
        responses={
            200: 'Renewal successful and payment initialized.',
            400: 'Bad request or payment initialization failed.',
            403: 'Forbidden for non-client users.'
        }
    )
    def post(self, request):
        user = request.user
        if user.user_type != 'client':
            return Response({'error': 'Only clients can renew subscriptions.'}, status=status.HTTP_403_FORBIDDEN)

        user_subscription = get_object_or_404(UserSubscription, user=user, is_active=True)
        plan = user_subscription.plan

        user_subscription.end_date = user_subscription.end_date + plan.duration
        user_subscription.is_active = False
        user_subscription.payment_completed = False
        user_subscription.subscription_status = 'pending'
        user_subscription.subscription_code = str(uuid.uuid4())
        user_subscription.save()

        callback_url = request.build_absolute_uri(reverse('payment-callback', kwargs={'ref': user_subscription.subscription_code}))
        response = paystack_client.initialize_transaction(user.email, int(plan.price * 100), user_subscription.subscription_code, callback_url)

        if response['status']:
            return Response({'authorization_url': response['data']['authorization_url'], 'subscription_code': user_subscription.subscription_code}, status=status.HTTP_200_OK)
        else:
            user_subscription.delete()
            return Response({'error': 'Payment initialization failed.'}, status=status.HTTP_400_BAD_REQUEST)


class UpgradeSubscriptionView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Upgrade the user's subscription plan.",
        responses={
            200: 'Upgrade successful and payment initialized.',
            400: 'Bad request or payment initialization failed.',
            403: 'Forbidden for non-client users.'
        }
    )
    def post(self, request, pk):
        user = request.user
        if user.user_type != 'client':
            return Response({'error': 'Only clients can upgrade subscriptions.'}, status=status.HTTP_403_FORBIDDEN)

        plan = get_object_or_404(SubscriptionPlan, pk=pk)
        user_subscription = get_object_or_404(UserSubscription, user=user, is_active=True)

        if user_subscription.plan.name == SubscriptionPlan.PREMIUM:
            return Response({'error': 'You already have the highest subscription plan.'}, status=status.HTTP_400_BAD_REQUEST)

        user_subscription.plan = plan
        user_subscription.end_date = timezone.now() + plan.duration
        user_subscription.is_active = False
        user_subscription.payment_completed = False
        user_subscription.subscription_status = 'pending'
        user_subscription.subscription_code = str(uuid.uuid4())
        user_subscription.save()

        callback_url = request.build_absolute_uri(reverse('payment-callback', kwargs={'ref': user_subscription.subscription_code}))
        response = paystack_client.initialize_transaction(user.email, int(plan.price * 100), user_subscription.subscription_code, callback_url)

        if response['status']:
            return Response({'authorization_url': response['data']['authorization_url'], 'subscription_code': user_subscription.subscription_code}, status=status.HTTP_200_OK)
        else:
            user_subscription.delete()
            return Response({'error': 'Payment initialization failed.'}, status=status.HTTP_400_BAD_REQUEST)


class CancelSubscriptionView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Cancel an active subscription plan.",
        responses={
            200: 'Subscription canceled successfully.',
            403: 'Forbidden for non-client users.'
        }
    )
    def delete(self, request):
        user = request.user
        if user.user_type != 'client':
            return Response({'error': 'Only clients can cancel subscriptions.'}, status=status.HTTP_403_FORBIDDEN)

        user_subscription = get_object_or_404(UserSubscription, user=user, is_active=True)
        user_subscription.deactivate_subscription()

        free_plan = get_object_or_404(SubscriptionPlan, name=SubscriptionPlan.FREE)
        user_subscription.plan = free_plan
        user_subscription.is_active = False
        user_subscription.subscription_status = 'canceled'
        user_subscription.save()

        return Response({'message': 'Subscription canceled successfully.'}, status=status.HTTP_200_OK)
