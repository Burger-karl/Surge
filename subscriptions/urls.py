from django.urls import path
from .views import SubscriptionPlanListView, UserSubscriptionListView, SubscribeView, RenewSubscriptionView, UpgradeSubscriptionView, CancelSubscriptionView

urlpatterns = [
    path('plans/', SubscriptionPlanListView.as_view(), name='subscription-plans'),
    path('user-subscriptions/', UserSubscriptionListView.as_view(), name='user-subscriptions'),
    path('subscribe/<int:pk>/', SubscribeView.as_view(), name='subscribe'),
    # path('verify-payment/<str:ref>/', PaymentCallbackView.as_view(), name='verify-payment'),
    path('renew-subscription/', RenewSubscriptionView.as_view(), name='renew-subscription'),
    path('upgrade-subscription/<int:pk>/', UpgradeSubscriptionView.as_view(), name='upgrade-subscription'),
    path('cancel-subscription/', CancelSubscriptionView.as_view(), name='cancel-subscription'),
]
