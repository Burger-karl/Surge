# Generated by Django 5.0.7 on 2025-01-20 11:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0002_alter_usersubscription_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscriptionplan',
            name='features',
            field=models.JSONField(default=list),
        ),
    ]
