from django.contrib import admin
from .models import Truck, Booking
from rest_framework.exceptions import PermissionDenied

# Register your models here.

@admin.register(Truck)
class TruckAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'weight_range', 'available']
    list_filter = ['available', 'weight_range']
    search_fields = ['name', 'owner__username']
    actions = ['make_available']

    def make_available(self, request, queryset):
        queryset.update(available=True)
    make_available.short_description = "Mark selected trucks as available"


class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'truck', 'product_name', 'product_weight', 'product_value', 'phone_number', 'pickup_state', 'destination_state', 'delivery_cost', 'payment_completed', 'booked_at')
    list_editable = ('delivery_cost',)
    list_filter = ('client', 'truck', 'pickup_state', 'destination_state', 'payment_completed', 'booked_at')
    search_fields = ('client__username', 'truck__name', 'product_name', 'pickup_state', 'destination_state')

    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser:
            return self.readonly_fields + ('delivery_cost',)
        return self.readonly_fields

    def save_model(self, request, obj, form, change):
        if change and 'delivery_cost' in form.changed_data:
            if request.user.is_superuser:
                super().save_model(request, obj, form, change)
            else:
                raise PermissionDenied("You do not have permission to edit the delivery cost.")
        else:
            super().save_model(request, obj, form, change)

admin.site.register(Booking, BookingAdmin)





# SQL Commands

# SELECT id, name, owner_id, weight_range, available
# FROM booking_truck;

# UPDATE booking_truck
# SET available = TRUE
# WHERE id = 1;

# SELECT id, name, owner_id, weight_range, available
# FROM booking_truck
# WHERE id = 1;


# UPDATE booking
# SET delivery_cost = 5000.00
# WHERE id = 1;

