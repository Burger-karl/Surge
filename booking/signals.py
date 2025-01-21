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
