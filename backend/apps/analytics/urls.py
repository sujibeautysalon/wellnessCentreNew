# filepath: c:\Users\cadsa\OneDrive\Personal\Full stack web development\wellnessCentre\backend\apps\analytics\urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.analytics.views import (
    DashboardViewSet, PerformanceMetricViewSet, AnalyticsReportViewSet,
    ServiceAnalyticsViewSet, CustomerJourneyViewSet
)

router = DefaultRouter()
router.register(r'dashboards', DashboardViewSet, basename='dashboard')
router.register(r'metrics', PerformanceMetricViewSet)
router.register(r'reports', AnalyticsReportViewSet)
router.register(r'service-analytics', ServiceAnalyticsViewSet)
router.register(r'customer-journey', CustomerJourneyViewSet, basename='customer-journey')

urlpatterns = [
    path('', include(router.urls)),
]