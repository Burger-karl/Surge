from rest_framework import serializers
from users.models import User
from subscriptions.models import UserSubscription
from booking.models import Booking, Truck
from delivery.models import DeliverySchedule, DeliveryHistory
from users.serializers import ProfileSerializer


# For Clients and Truck Owners
class UserProfileSerializer(serializers.ModelSerializer):
    profile_image = serializers.ImageField(source='profile.profile_image')
    full_name = serializers.CharField(source='profile.full_name')
    address = serializers.CharField(source='profile.address')
    phone_number = serializers.CharField(source='profile.phone_number')
    state = serializers.CharField(source='profile.state')

    class Meta:
        model = User
        fields = ['profile_image', 'full_name', 'address', 'phone_number', 'state']


# For Clients
class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSubscription
        fields = ['id', 'plan', 'start_date', 'end_date', 'subscription_status']

# class UnpaidBookingSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Booking
#         fields = ['id', 'truck', 'product_name', 'destination_state', 'delivery_cost']

class UnpaidBookingSerializer(serializers.ModelSerializer):
    payment_completed = serializers.BooleanField()

    class Meta:
        model = Booking
        fields = [
            'id',
            'truck',
            'product_name',
            'destination_state',
            'delivery_cost',
            'payment_completed',  # Include this field for clarity
        ]


class DeliveryScheduleSerializer(serializers.ModelSerializer):
    product_name = serializers.SerializerMethodField()
    truck_name = serializers.SerializerMethodField()
    destination_state = serializers.SerializerMethodField()
    delivery_cost = serializers.SerializerMethodField()

    class Meta:
        model = DeliverySchedule
        fields = ['id', 'scheduled_date', 'status', 'product_name', 'truck_name', 'destination_state', 'delivery_cost']

    def get_product_name(self, obj):
        return obj.booking.product_name

    def get_truck_name(self, obj):
        return obj.booking.truck.name

    def get_destination_state(self, obj):
        return obj.booking.destination_state

    def get_delivery_cost(self, obj):
        return obj.booking.delivery_cost

class DeliveryHistorySerializer(serializers.ModelSerializer):
    product_name = serializers.SerializerMethodField()
    truck_name = serializers.SerializerMethodField()
    destination_state = serializers.SerializerMethodField()
    delivery_cost = serializers.SerializerMethodField()

    class Meta:
        model = DeliveryHistory
        fields = ['id', 'delivery_date', 'status', 'product_name', 'truck_name', 'destination_state', 'delivery_cost']

    def get_product_name(self, obj):
        return obj.booking.product_name

    def get_truck_name(self, obj):
        return obj.booking.truck.name

    def get_destination_state(self, obj):
        return obj.booking.destination_state

    def get_delivery_cost(self, obj):
        return obj.booking.delivery_cost



# Truck Owners

class TruckSerializer(serializers.ModelSerializer):
    class Meta:
        model = Truck
        fields = '__all__'

class BookingSerializer(serializers.ModelSerializer):
    truck = TruckSerializer()

    class Meta:
        model = Booking
        fields = ['id', 'client', 'truck', 'product_name', 'destination_state', 'delivery_cost', 'booking_status', 'payment_completed']
