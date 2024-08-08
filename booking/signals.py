from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Booking, Truck
from delivery.utils import confirm_booking
from notification.models import Notification
from users.models import User


@receiver(post_save, sender=Booking)
def booking_payment_handler(sender, instance, **kwargs):
    if instance.payment_completed and instance.booking_status == 'active':
        confirm_booking(instance)



from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Truck, Booking
from notification.models import Notification
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
