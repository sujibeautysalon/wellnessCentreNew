from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('users', views.UserViewSet, basename='user')
router.register('profiles', views.UserProfileViewSet, basename='profile')
router.register('settings', views.UserSettingsViewSet, basename='settings')
router.register('consents', views.UserConsentViewSet, basename='consent')
router.register('audit-logs', views.AuditLogViewSet, basename='audit-log')

urlpatterns = [
    # Auth endpoints
    path('auth/register/', views.RegisterView.as_view(), name='register'),
    path('auth/login/', views.LoginView.as_view(), name='login'),
    path('auth/logout/', views.LogoutView.as_view(), name='logout'),
    path('auth/password/change/', views.PasswordChangeView.as_view(), name='password-change'),
    path('auth/password/reset/', views.PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('auth/password/reset/confirm/', views.PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    
    # API router
    path('', include(router.urls)),
]