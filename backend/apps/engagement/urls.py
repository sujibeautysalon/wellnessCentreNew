from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.engagement.views import (
    CampaignViewSet, NotificationViewSet, FeedbackFormViewSet, 
    FeedbackResponseViewSet, LoyaltyViewSet, LoyaltyTransactionViewSet, ReferralViewSet
)

router = DefaultRouter()
router.register('campaigns', CampaignViewSet, basename='campaign')
router.register('notifications', NotificationViewSet, basename='notification')
router.register('feedback-forms', FeedbackFormViewSet, basename='feedback-form')
router.register('feedback-responses', FeedbackResponseViewSet, basename='feedback-response')
router.register('loyalty', LoyaltyViewSet, basename='loyalty')
router.register('loyalty-transactions', LoyaltyTransactionViewSet, basename='loyalty-transaction')
router.register('referrals', ReferralViewSet, basename='referral')

urlpatterns = [
    path('', include(router.urls)),
]