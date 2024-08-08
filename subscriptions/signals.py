from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import UserSubscription, SubscriptionPlan

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_subscription(sender, instance, created, **kwargs):
    if created:
        free_plan = SubscriptionPlan.objects.get(name=SubscriptionPlan.FREE)
        UserSubscription.objects.create(user=instance, plan=free_plan, subscription_status='inactive')
