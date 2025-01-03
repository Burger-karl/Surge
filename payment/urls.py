from django.urls import path
from .views import VerifyPaymentView, CreateBookingPaymentView, VerifyBookingPaymentView, PaymentHistoryView

urlpatterns = [
    # path('subscription/<int:plan_id>/', CreateSubscriptionPaymentView.as_view(), name='create-subscription-payment'),
    path('verify-payment/<str:ref>/', VerifyPaymentView.as_view(), name='payment-callback'),

    path('booking-payments/create/<int:booking_id>/', CreateBookingPaymentView.as_view(), name='create-booking-payment'),
    path('booking-payments/verify/<str:ref>/', VerifyBookingPaymentView.as_view(), name='verify-booking-payment'),

    path('payment-history/', PaymentHistoryView.as_view(), name='payment-history'),
]

