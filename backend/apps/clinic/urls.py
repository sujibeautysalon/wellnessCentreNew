from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('branches', views.BranchViewSet, basename='branch')
router.register('services', views.ServiceViewSet, basename='service')
router.register('therapists', views.TherapistProfileViewSet, basename='therapist')
router.register('availability', views.TherapistAvailabilityViewSet, basename='availability')
router.register('holidays', views.HolidayViewSet, basename='holiday')

urlpatterns = [
    path('', include(router.urls)),
]