from rest_framework import serializers
from .models import Truck, TruckImage, Booking
    
class TruckImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TruckImage
        fields = ['image']

    def to_representation(self, instance):
        return instance.image.url  # Return the URL of the image


class TruckSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField()
    images = TruckImageSerializer(many=True, read_only=True)

    class Meta:
        model = Truck
        fields = ['id', 'owner', 'name', 'weight_range', 'available', 'images']
        read_only_fields = ['available', 'owner']


class BookingSerializer(serializers.ModelSerializer):
    client = serializers.StringRelatedField()
    truck = serializers.PrimaryKeyRelatedField(queryset=Truck.objects.all())

    class Meta:
        model = Booking
        fields = [
            'id', 'client', 'truck', 'product_name', 'product_weight', 'product_value',
            'phone_number', 'payment_completed', 'booked_at', 'pickup_state',
            'destination_state', 'delivery_cost', 'insurance_payment', 'total_delivery_cost'  # Include total_delivery_cost
        ]
        read_only_fields = ['client', 'payment_completed', 'booked_at', 'delivery_cost', 'insurance_payment', 'total_delivery_cost']

    def validate(self, data):
        pickup_state = data.get('pickup_state')
        destination_state = data.get('destination_state')

        if pickup_state not in [choice[0] for choice in Booking.STATES_CHOICES]:
            raise serializers.ValidationError("Invalid pickup state.")
        
        if destination_state not in [choice[0] for choice in Booking.STATES_CHOICES]:
            raise serializers.ValidationError("Invalid destination state.")

        return data