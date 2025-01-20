# serializers.py
from rest_framework import serializers
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'

    def create(self, validated_data):
        if 'read' not in validated_data:
            validated_data['read'] = True  # Set read to True by default
        return super().create(validated_data)
