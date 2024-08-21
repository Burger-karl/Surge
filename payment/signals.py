from django.db.models.signals import post_save
from django.dispatch import receiver
from booking.models import Booking
from utils import is_migration_running  # Import the helper function
from notification.models import Notification
from payment.models import Payment

@receiver(post_save, sender=Booking)
def booking_payment_verified_handler(sender, instance, **kwargs):
    if is_migration_running():  # Check if migrations are running
        return
    if instance.payment_completed and instance.booking_status == 'active':
        Notification.objects.create(user=instance.client, message="Your booking payment has been verified and the booking is now active.")

@receiver(post_save, sender=Payment)
def payment_verified_handler(sender, instance, **kwargs):
    if is_migration_running():  # Check if migrations are running
        return
    if instance.booking is not None and instance.booking.client is not None:
        Notification.objects.create(user=instance.booking.client, message="Your payment has been successfully verified.")
    else:
        print("Warning: Booking or client is None.")
