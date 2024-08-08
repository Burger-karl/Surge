from notification.models import Notification
from django.db.models.signals import post_save
from django.dispatch import receiver
from booking.models import Booking
from .models import DeliverySchedule, DeliveryHistory
from datetime import datetime


@receiver(post_save, sender=DeliveryHistory)
def delivery_status_handler(sender, instance, **kwargs):
    if instance.status == 'delivered':
        Notification.objects.create(user=instance.booking.client, message="Your delivery has been successfully completed.")
        Notification.objects.create(user=instance.booking.truck.owner, message="Your truck has successfully completed a delivery.")


@receiver(post_save, sender=Booking)
def create_delivery_schedule_and_history(sender, instance, created, **kwargs):
    if created and instance.booking_status == 'active' and instance.payment_completed:
        scheduled_date = datetime.now().date()
        DeliverySchedule.objects.create(
            booking=instance,
            scheduled_date=scheduled_date
        )
        DeliveryHistory.objects.create(
            booking=instance,
            delivery_date=scheduled_date,
            status='pending'
        )
