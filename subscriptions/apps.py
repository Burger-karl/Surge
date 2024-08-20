# from django.apps import AppConfig

# class SubscriptionsConfig(AppConfig):
#     name = 'subscriptions'

#     def ready(self):
#         from .models import SubscriptionPlan
#         SubscriptionPlan.create_default_plans()


from django.apps import AppConfig
from django.db.utils import OperationalError

class SubscriptionsConfig(AppConfig):
    name = 'subscriptions'

    def ready(self):
        from .models import SubscriptionPlan
        from . import signals  # Ensure signals are connected

        try:
            # Attempt to query to check if the table exists
            SubscriptionPlan.objects.get(name='free')
        except OperationalError:
            # The table doesn't exist yet, so handle it gracefully
            pass
