from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('appointments', views.AppointmentViewSet, basename='appointment')
router.register('payments', views.PaymentViewSet, basename='payment')
router.register('invoices', views.InvoiceViewSet, basename='invoice')
router.register('waitlist', views.WaitlistEntryViewSet, basename='waitlist')

urlpatterns = [
    path('', include(router.urls)),
]