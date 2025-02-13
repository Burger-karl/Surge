# Generated by Django 5.0.7 on 2025-01-31 07:00

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('delivery', '0003_remove_deliveryhistory_user_deliveryschedule_status_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='deliveryhistory',
            name='client',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='delivery_histories', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='deliveryschedule',
            name='client',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='delivery_schedules', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='deliveryhistory',
            name='delivery_date',
            field=models.DateField(auto_now_add=True),
        ),
        migrations.DeleteModel(
            name='DeliveryDocument',
        ),
    ]
