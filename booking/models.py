from django.db import models
from django.utils import timezone
from users.models import User

class Truck(models.Model):
    LIGHTWEIGHT = 'lightweight'
    MEDIUMWEIGHT = 'mediumweight'
    HEAVYWEIGHT = 'heavyweight'
    VERYHEAVYWEIGHT = 'veryheavyweight'
    
    WEIGHT_CHOICES = [
        (LIGHTWEIGHT, '0 - 1000kg'),
        (MEDIUMWEIGHT, '1001 - 5000kg'),
        (HEAVYWEIGHT, '5001 - 10000kg'),
        (VERYHEAVYWEIGHT, '10001kg and above')
    ]

    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='trucks/')
    weight_range = models.CharField(max_length=15, choices=WEIGHT_CHOICES, default=LIGHTWEIGHT)
    available = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({self.owner.username})"

class Booking(models.Model):
    STATES_CHOICES = [
        ('abia', 'Abia'), ('abuja', 'Abuja'), ('adamawa', 'Adamawa'), ('akwa_ibom', 'Akwa Ibom'), ('anambra', 'Anambra'),
        ('bauchi', 'Bauchi'), ('bayelsa', 'Bayelsa'), ('benue', 'Benue'), ('borno', 'Borno'),
        ('cross_river', 'Cross River'), ('delta', 'Delta'), ('ebonyi', 'Ebonyi'), ('edo', 'Edo'),
        ('ekiti', 'Ekiti'), ('enugu', 'Enugu'), ('gombe', 'Gombe'), ('imo', 'Imo'),
        ('jigawa', 'Jigawa'), ('kaduna', 'Kaduna'), ('kano', 'Kano'), ('katsina', 'Katsina'),
        ('kebbi', 'Kebbi'), ('kogi', 'Kogi'), ('kwara', 'Kwara'), ('lagos', 'Lagos'),
        ('nasarawa', 'Nasarawa'), ('niger', 'Niger'), ('ogun', 'Ogun'), ('ondo', 'Ondo'),
        ('osun', 'Osun'), ('oyo', 'Oyo'), ('plateau', 'Plateau'), ('rivers', 'Rivers'),
        ('sokoto', 'Sokoto'), ('taraba', 'Taraba'), ('yobe', 'Yobe'), ('zamfara', 'Zamfara'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('cancelled', 'Cancelled'),
    ]

    client = models.ForeignKey(User, on_delete=models.CASCADE)
    truck = models.ForeignKey(Truck, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=255)
    product_weight = models.CharField(max_length=15, choices=Truck.WEIGHT_CHOICES)
    product_value = models.DecimalField(max_digits=10, decimal_places=2)
    phone_number = models.DecimalField(max_digits=11, decimal_places=1, default=00000000000)
    payment_completed = models.BooleanField(default=False)
    booked_at = models.DateTimeField(default=timezone.now)
    pickup_state = models.CharField(max_length=20, choices=STATES_CHOICES)
    destination_state = models.CharField(max_length=20, choices=STATES_CHOICES)
    delivery_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    booking_code = models.CharField(max_length=255, null=True, blank=True)
    booking_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"Booking by {self.client.username} for {self.product_name}"
