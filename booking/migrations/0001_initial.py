# Generated by Django 5.0.7 on 2024-07-21 09:00

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Truck',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('image', models.ImageField(upload_to='trucks/')),
                ('weight_range', models.CharField(choices=[('lightweight', '0 - 1000kg'), ('mediumweight', '1001 - 5000kg'), ('heavyweight', '5001 - 10000kg'), ('veryheavyweight', '10001kg and above')], default='lightweight', max_length=15)),
                ('available', models.BooleanField(default=False)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
