from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.contrib.auth import views as auth_views

schema_view = get_schema_view(
    openapi.Info(
        title="SurgeSeven Logistics API",
        default_version='v1',
        description="API Documentation for SurgeSeven Logistics",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="support@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('users.urls')),
    path('subscriptions/', include('subscriptions.urls')),
    path('booking/', include('booking.urls')),
    path('payment/', include('payment.urls')),
    path('delivery/', include('delivery.urls')),
    path('notify/', include('notification.urls')),
    path('dashboard/', include('dashboard.urls')),

    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    # path('api-auth/', include('rest_framework.urls')),

    # path('login/', auth_views.LoginView.as_view(template_name='login.html')),
    # path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]

urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
