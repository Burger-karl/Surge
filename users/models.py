from django.contrib.auth.models import AbstractUser
from django.db import models
from .managers import CustomUserManager
from django.utils import timezone
from datetime import timedelta


class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('client', 'Client'),
        ('truck_owner', 'Truck Owner'),
        ('admin', 'Admin'),
    )
    user_type = models.CharField(max_length=11, choices=USER_TYPE_CHOICES, default='client')
    
    objects = CustomUserManager()

    def __str__(self):
        return self.username
    

class OTP(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)



class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def is_expired(self):
        return self.created_at < timezone.now() - timedelta(hours=1)  # Example: 1 hour expiry


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    full_name = models.CharField(max_length=255, blank=True)
    address = models.TextField(blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    state = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.user.username