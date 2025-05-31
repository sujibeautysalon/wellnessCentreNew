"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="Wellness Centre API",
      default_version='v1',
      description="API for Wellness Centre platform",
      terms_of_service="https://www.wellnesscentre.com/terms/",
      contact=openapi.Contact(email="contact@wellnesscentre.com"),
      license=openapi.License(name="Private"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

# API Patterns
api_patterns = [
    path('core/', include('apps.core.urls')),
    path('clinic/', include('apps.clinic.urls')),
    path('booking/', include('apps.booking.urls')),
    path('ehr/', include('apps.ehr.urls')),
    path('engagement/', include('apps.engagement.urls')),
    path('inventory/', include('apps.inventory.urls')),
    path('finance/', include('apps.finance.urls')),
    path('analytics/', include('apps.analytics.urls')),
]

urlpatterns = [
    # Admin site
    path('admin/', admin.site.urls),
    
    # API endpoints (v1)
    path('api/v1/', include(api_patterns)),
    
    # API documentation
    path('', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    
    # Health check
    path('health/', include('health_check.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
