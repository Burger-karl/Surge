from rest_framework import serializers
from .models import DeliverySchedule, DeliveryHistory, DeliveryDocument

class DeliveryScheduleSerializer(serializers.ModelSerializer):
    truck_name = serializers.SerializerMethodField()
    product_name = serializers.SerializerMethodField()
    total_delivery_cost = serializers.SerializerMethodField()
    destination_address = serializers.SerializerMethodField()

    class Meta:
        model = DeliverySchedule
        fields = ['id', 'booking', 'scheduled_date', 'status', 'truck_name', 'product_name', 'total_delivery_cost', 'destination_address']

    def get_truck_name(self, obj):
        return obj.booking.truck.name

    def get_product_name(self, obj):
        return obj.booking.product_name

    def get_total_delivery_cost(self, obj):
        return obj.booking.total_delivery_cost

    def get_destination_address(self, obj):
        return obj.booking.destination_state

class DeliveryHistorySerializer(serializers.ModelSerializer):
    truck_name = serializers.SerializerMethodField()
    product_name = serializers.SerializerMethodField()
    total_delivery_cost = serializers.SerializerMethodField()
    destination_address = serializers.SerializerMethodField()

    class Meta:
        model = DeliveryHistory
        fields = ['id', 'booking', 'delivery_date', 'status', 'truck_name', 'product_name', 'total_delivery_cost', 'destination_address']

    def get_truck_name(self, obj):
        return obj.booking.truck.name

    def get_product_name(self, obj):
        return obj.booking.product_name

    def get_total_delivery_cost(self, obj):
        return obj.booking.total_delivery_cost

    def get_destination_address(self, obj):
        return obj.booking.destination_state


class DeliveryDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryDocument
        fields = '__all__'
