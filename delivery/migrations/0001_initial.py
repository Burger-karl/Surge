# Generated by Django 5.0.7 on 2024-07-29 16:35

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('booking', '0007_booking_booking_status'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DeliveryDocument',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('document_type', models.CharField(choices=[('Receipt', 'Receipt'), ('Invoice', 'Invoice')], max_length=50)),
                ('document_file', models.FileField(upload_to='delivery_documents/')),
                ('booking', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='booking.booking')),
            ],
        ),
        migrations.CreateModel(
            name='DeliveryHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('delivery_date', models.DateField()),
                ('status', models.CharField(choices=[('Scheduled', 'Scheduled'), ('In Transit', 'In Transit'), ('Delivered', 'Delivered')], max_length=50)),
                ('booking', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='booking.booking')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='DeliverySchedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('scheduled_date', models.DateField()),
                ('status', models.CharField(choices=[('Scheduled', 'Scheduled'), ('In Transit', 'In Transit'), ('Delivered', 'Delivered')], default='Scheduled', max_length=50)),
                ('booking', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='booking.booking')),
            ],
        ),
    ]
