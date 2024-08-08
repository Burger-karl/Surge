from django.apps import AppConfig

class SubscriptionsConfig(AppConfig):
    name = 'subscriptions'

    def ready(self):
        from .models import SubscriptionPlan
        SubscriptionPlan.create_default_plans()
