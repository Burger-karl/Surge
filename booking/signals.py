from django.db.models.signals import post_save
from django.dispatch import receiver
from notification.models import Notification
from booking.models import Booking, Truck
from payment.models import Payment
from delivery.models import DeliveryHistory
from users.models import User
from delivery.utils import confirm_booking
from utils import is_migration_running  # Helper function to check if migrations are running

@receiver(post_save, sender=Booking)
def booking_payment_handler(sender, instance, **kwargs):
    if is_migration_running():  # Check if migrations are running
        return
    if instance.payment_completed and instance.booking_status == 'active':
        confirm_booking(instance)


@receiver(post_save, sender=Booking)
def handle_booking_notifications(sender, instance, created, **kwargs):
    if is_migration_running():
        return

    # Cache superuser
    superuser = User.objects.filter(is_superuser=True).first()

    if created:
        # Notify the superuser and client about new booking
        Notification.objects.create(
            user=superuser,
            booking=instance,
            message=f"A new booking has been made by {instance.client.username} and is awaiting delivery cost assignment.",
            notification_type="booking-created",
        )
        Notification.objects.create(
            user=instance.client,
            booking=instance,
            message="Your booking has been created successfully. Waiting for delivery cost assignment.",
            notification_type="booking-created",
        )

    # Notify client when delivery cost is assigned
    if instance.delivery_cost and not instance.payment_completed:
        Notification.objects.create(
            user=instance.client,
            booking=instance,
            message="The delivery cost for your booking has been set by the admin.",
            notification_type="booking-cost-added",
        )

    # Notify relevant users when payment is completed
    if instance.payment_completed and instance.booking_status == 'active':
        Notification.objects.create(
            user=instance.truck.owner,
            booking=instance,
            message="Your truck has been successfully booked and paid for.",
            notification_type="truck-booked",
        )
        Notification.objects.create(
            user=instance.client,
            booking=instance,
            message="Your booking payment has been verified.",
            notification_type="booking-payment-verified",
        )

@receiver(post_save, sender=Payment)
def handle_payment_notifications(sender, instance, created, **kwargs):
    if is_migration_running():
        return

    if created and instance.verified:
        # Notify client when payment is verified
        Notification.objects.create(
            user=instance.booking.client,
            booking=instance.booking,
            message="Your payment has been successfully verified.",
            notification_type="booking-payment-verified",
        )

@receiver(post_save, sender=DeliveryHistory)
def handle_delivery_notifications(sender, instance, **kwargs):
    if is_migration_running():
        return

    if instance.status == 'delivered':
        # Notify both client and truck owner on delivery completion
        Notification.objects.bulk_create([
            Notification(
                user=instance.booking.client,
                booking=instance.booking,
                message="Your delivery has been successfully completed.",
                notification_type="delivery-completed",
            ),
            Notification(
                user=instance.booking.truck.owner,
                booking=instance.booking,
                message="Your truck has successfully completed a delivery.",
                notification_type="delivery-completed",
            ),
        ])

@receiver(post_save, sender=Truck)
def handle_truck_notifications(sender, instance, created, **kwargs):
    if is_migration_running():
        return

    # Cache superuser
    superuser = User.objects.filter(is_superuser=True).first()

    if created:
        # Notify superuser and owner on truck upload
        Notification.objects.bulk_create([
            Notification(
                user=superuser,
                booking=None,
                message=f"A new truck has been uploaded by {instance.owner.username} and is awaiting inspection.",
                notification_type="truck-uploaded",
            ),
            Notification(
                user=instance.owner,
                booking=None,
                message="Your truck has been uploaded and is awaiting inspection.",
                notification_type="truck-uploaded",
            ),
        ])

    if instance.available:
        # Notify truck owner when status is updated to available
        Notification.objects.create(
            user=instance.owner,
            booking=None,
            message="Your truck status has been updated to available after inspection.",
            notification_type="truck-available",
        )
