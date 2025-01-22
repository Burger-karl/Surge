from django.urls import path
from .views import NotificationListView, NotificationDetailView, MarkNotificationAsReadView, MultiMarkNotificationsAsReadView

urlpatterns = [
    path('notifications/', NotificationListView.as_view(), name='notification-list'),
    path('notifications/<int:pk>/', NotificationDetailView.as_view(), name='notification-detail'),
    path('notifications/read/', MarkNotificationAsReadView.as_view(), name='mark-notification-as-read'),
    path('notifications/read-multiple/', MultiMarkNotificationsAsReadView.as_view(), name='mark-notifications-as-read'),
]

