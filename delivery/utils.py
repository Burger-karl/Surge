from .models import DeliverySchedule, DeliveryHistory
from datetime import datetime

def confirm_booking(booking):
    if booking.payment_completed and booking.booking_status == 'active':
        scheduled_date = datetime.now().date()

        # Create DeliverySchedule
        DeliverySchedule.objects.get_or_create(
            booking=booking,
            defaults={'scheduled_date': scheduled_date, 'status': 'pending'}
        )

        # Create initial DeliveryHistory
        DeliveryHistory.objects.create(
            booking=booking,
            delivery_date=scheduled_date,
            status='pending'
        )

