# notification/signals.py

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Notification
from booking.models import Truck, Booking
from payment.models import Payment
from delivery.models import DeliveryHistory
from users.models import User

@receiver(post_save, sender=Truck)
def truck_uploaded_handler(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(user=instance.owner, message="Your truck has been uploaded and is awaiting inspection.")
        Notification.objects.create(user=User.objects.filter(is_superuser=True).first(), message="A new truck has been uploaded and is awaiting inspection.")
    elif instance.available:
        Notification.objects.create(user=instance.owner, message="Your truck status has been updated to available after inspection.")

@receiver(post_save, sender=Booking)
def booking_created_handler(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(user=User.objects.filter(is_superuser=True).first(), message="A new booking has been made and is awaiting delivery cost assignment.")
        Notification.objects.create(user=instance.client, message="Your booking has been created successfully. Waiting for delivery cost assignment.")
    elif instance.payment_completed and instance.booking_status == 'active':
        Notification.objects.create(user=instance.truck.owner, message="Your truck has been successfully booked and paid for.")
        Notification.objects.create(user=instance.client, message="Your booking payment has been verified.")

@receiver(post_save, sender=Payment)
def payment_verified_handler(sender, instance, created, **kwargs):
    if created and instance.verified:
        Notification.objects.create(user=instance.booking.client, message="Your payment has been successfully verified.")

@receiver(post_save, sender=DeliveryHistory)
def delivery_status_handler(sender, instance, **kwargs):
    if instance.status == 'delivered':
        Notification.objects.create(user=instance.booking.client, message="Your delivery has been successfully completed.")
        Notification.objects.create(user=instance.booking.truck.owner, message="Your truck has successfully completed a delivery.")
