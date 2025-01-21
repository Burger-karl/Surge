from django.db.models.signals import post_save
from django.dispatch import receiver
from utils import is_migration_running  # Import the helper function
from booking.models import Booking
from .models import DeliverySchedule, DeliveryHistory
from datetime import datetime
from notification.models import Notification



@receiver(post_save, sender=Booking)
def create_delivery_schedule_on_payment(sender, instance, created, **kwargs):
    """
    Create a delivery schedule and initial delivery history when a booking payment is completed.
    """
    if created:  # New booking created
        return

    # Trigger when payment is completed and booking is active
    if instance.payment_completed and instance.booking_status == 'active':
        scheduled_date = datetime.now().date()

        # Create DeliverySchedule if it doesn't already exist
        delivery_schedule, schedule_created = DeliverySchedule.objects.get_or_create(
            booking=instance,
            defaults={'scheduled_date': scheduled_date, 'status': 'pending'}
        )

        if schedule_created:  # Only create DeliveryHistory for new schedules
            DeliveryHistory.objects.create(
                booking=instance,
                delivery_date=scheduled_date,
                status='pending'
            )


# @receiver(post_save, sender=DeliveryHistory)
# def handle_delivery_notifications(sender, instance, **kwargs):
#     if is_migration_running():
#         return

#     if instance.status == 'delivered':
#         # Notify both client and truck owner on delivery completion
#         Notification.objects.bulk_create([
#             Notification(
#                 user=instance.booking.client,
#                 booking=instance.booking,
#                 message="Your delivery has been successfully completed.",
#                 notification_type="delivery-completed",
#             ),
#             Notification(
#                 user=instance.booking.truck.owner,
#                 booking=instance.booking,
#                 message="Your truck has successfully completed a delivery.",
#                 notification_type="delivery-completed",
#             ),
#         ])
