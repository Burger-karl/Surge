from django.contrib import admin
from .models import DeliverySchedule, DeliveryHistory, DeliveryDocument

# Register your models here.

admin.site.register(DeliverySchedule)
admin.site.register(DeliveryHistory)
admin.site.register(DeliveryDocument)
