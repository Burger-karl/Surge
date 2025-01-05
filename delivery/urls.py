from django.urls import path
from .views import DeliveryScheduleListView, DeliveryHistoryView, UpdateDeliveryScheduleStatusView

urlpatterns = [
    path('delivery-schedules/', DeliveryScheduleListView.as_view(), name='delivery-schedules'),
    path('delivery-histories/', DeliveryHistoryView.as_view(), name='delivery-histories'),
    # path('delivery-documents/', DeliveryDocumentView.as_view(), name='delivery-documents'),

    # FOR SUPERUSER
    path('delivery-schedules/<int:pk>/update-status/', UpdateDeliveryScheduleStatusView.as_view(), name='update-delivery-schedule-status'),
]
