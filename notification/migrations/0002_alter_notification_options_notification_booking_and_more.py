# Generated by Django 5.0.7 on 2025-01-20 08:49

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0011_alter_booking_phone_number'),
        ('notification', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='notification',
            options={'ordering': ['-created_at']},
        ),
        migrations.AddField(
            model_name='notification',
            name='booking',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='booking.booking'),
        ),
        migrations.AddField(
            model_name='notification',
            name='notification_type',
            field=models.CharField(choices=[('booking-payment-verified', 'Booking Payment Verified'), ('booking-created', 'Booking Created'), ('booking-cost-added', 'Booking Cost Added'), ('truck-uploaded', 'Truck Uploaded'), ('truck-available', 'Truck Available'), ('truck-booked', 'Truck Booked'), ('delivery-completed', 'Delivery Completed')], default='booking-created', max_length=50),
        ),
        migrations.AlterField(
            model_name='notification',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to=settings.AUTH_USER_MODEL),
        ),
    ]
