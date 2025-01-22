from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Notification
from .serializers import NotificationSerializer

# List all notifications for the authenticated user
class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)
    

# Retrieve a single notification for the authenticated user
class NotificationDetailView(generics.RetrieveAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)


# Mark a single notification as read
class MarkNotificationAsReadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        notification_id = request.data.get('id')
        
        # Ensure ID is provided
        if not notification_id:
            return Response({"error": "Notification ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Fetch the notification for the authenticated user
            notification = Notification.objects.get(id=notification_id, user=request.user)
            
            # Mark as read
            notification.read = True
            notification.save()
            
            return Response({"message": "Notification marked as read successfully."}, status=status.HTTP_200_OK)
        
        except Notification.DoesNotExist:
            return Response({"error": "Notification not found or not accessible."}, status=status.HTTP_404_NOT_FOUND)


# Mark multiple notifications as read
class MultiMarkNotificationsAsReadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        notification_ids = request.data.get('ids', [])  # Expecting a list of IDs
        
        if not notification_ids or not isinstance(notification_ids, list):
            return Response({"error": "A list of Notification IDs is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch and update notifications for the authenticated user
        notifications = Notification.objects.filter(id__in=notification_ids, user=request.user)
        updated_count = notifications.update(read=True)
        
        return Response({"message": f"{updated_count} notifications marked as read."}, status=status.HTTP_200_OK)
