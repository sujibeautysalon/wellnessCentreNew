from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('medical-history', views.MedicalHistoryViewSet, basename='medical-history')
router.register('treatment-sessions', views.TreatmentSessionViewSet, basename='treatment-session')
router.register('symptoms', views.SymptomTrackerViewSet, basename='symptom')
router.register('wellness-journal', views.WellnessJournalViewSet, basename='wellness-journal')
router.register('attachments', views.FileAttachmentViewSet, basename='attachment')

urlpatterns = [
    path('', include(router.urls)),
]