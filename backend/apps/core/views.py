from django.contrib.auth import get_user_model, authenticate, login, logout
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from django.shortcuts import get_object_or_404

from rest_framework import status, generics, permissions, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError

from .models import UserProfile, UserSettings, UserConsent, AuditLog
from .serializers import (
    UserSerializer, 
    RegisterSerializer,
    LoginSerializer, 
    UserProfileSerializer,
    UserSettingsSerializer,
    UserConsentSerializer,
    AuditLogSerializer,
    PasswordChangeSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer
)
from .permissions import IsAdminUser, IsOwnerOrAdmin

User = get_user_model()


def get_tokens_for_user(user):
    """Generate JWT tokens for a user."""
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class RegisterView(generics.CreateAPIView):
    """Handle user registration."""
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Log the registration
        AuditLog.objects.create(
            user=user,
            action='user_registered',
            ip_address=self.request.META.get('REMOTE_ADDR'),
            resource_type='user',
            resource_id=str(user.id)
        )
        
        # Return user with tokens
        tokens = get_tokens_for_user(user)
        return Response({
            'user': UserSerializer(user, context=self.get_serializer_context()).data,
            'tokens': tokens,
            'message': 'User registered successfully'
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """Handle user login."""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = authenticate(
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password']
        )
        
        if not user:
            return Response({
                'error': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)
            
        if not user.is_active:
            return Response({
                'error': 'Account is disabled'
            }, status=status.HTTP_401_UNAUTHORIZED)
            
        # Login user
        login(request, user)
        
        # Log the login
        AuditLog.objects.create(
            user=user,
            action='user_logged_in',
            ip_address=request.META.get('REMOTE_ADDR'),
            resource_type='user',
            resource_id=str(user.id)
        )
        
        # Return user with tokens
        tokens = get_tokens_for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'tokens': tokens,
            'message': 'Login successful'
        }, status=status.HTTP_200_OK)


class LogoutView(APIView):
    """Handle user logout."""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        # Log the logout
        AuditLog.objects.create(
            user=request.user,
            action='user_logged_out',
            ip_address=request.META.get('REMOTE_ADDR'),
            resource_type='user',
            resource_id=str(request.user.id)
        )
        
        # Logout user
        logout(request)
        
        return Response({
            'message': 'Logged out successfully'
        }, status=status.HTTP_200_OK)


class PasswordChangeView(APIView):
    """Handle password change for authenticated user."""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        
        # Check if the old password is correct
        if not user.check_password(serializer.validated_data['old_password']):
            return Response({
                'error': 'Incorrect password'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        # Set new password
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        # Log the password change
        AuditLog.objects.create(
            user=user,
            action='password_changed',
            ip_address=request.META.get('REMOTE_ADDR'),
            resource_type='user',
            resource_id=str(user.id)
        )
        
        return Response({
            'message': 'Password changed successfully'
        }, status=status.HTTP_200_OK)


class PasswordResetRequestView(APIView):
    """Handle password reset request."""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        
        # Check if user exists
        try:
            user = User.objects.get(email=email)
            
            # Generate token
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # In a real app, we would send an email here
            # For now, just log the action
            AuditLog.objects.create(
                user=user,
                action='password_reset_requested',
                ip_address=request.META.get('REMOTE_ADDR'),
                resource_type='user',
                resource_id=str(user.id),
                details={
                    'token': token,
                    'uid': uid
                }
            )
            
        except User.DoesNotExist:
            pass  # Don't reveal if user exists or not
        
        return Response({
            'message': 'Password reset email sent if account exists'
        }, status=status.HTTP_200_OK)


class PasswordResetConfirmView(APIView):
    """Handle password reset confirmation."""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            uid = force_str(urlsafe_base64_decode(serializer.validated_data['uid']))
            user = User.objects.get(pk=uid)
            
            # Verify the token
            if default_token_generator.check_token(user, serializer.validated_data['token']):
                user.set_password(serializer.validated_data['new_password'])
                user.save()
                
                # Log the password reset
                AuditLog.objects.create(
                    user=user,
                    action='password_reset_completed',
                    ip_address=request.META.get('REMOTE_ADDR'),
                    resource_type='user',
                    resource_id=str(user.id)
                )
                
                return Response({
                    'message': 'Password reset successful'
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': 'Invalid token'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except (User.DoesNotExist, ValidationError, ValueError):
            return Response({
                'error': 'Invalid reset link'
            }, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for User model."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [permissions.IsAdminUser]
        elif self.action in ['update', 'partial_update', 'destroy', 'me']:
            permission_classes = [IsOwnerOrAdmin]
        elif self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        # Regular users can only see themselves, admins can see all users
        if self.request.user.is_staff or self.request.user.role == 'admin':
            return User.objects.all()
        return User.objects.filter(id=self.request.user.id)
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get the current user's profile."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    def perform_destroy(self, instance):
        # Log user deletion
        AuditLog.objects.create(
            user=self.request.user,
            action='user_deleted',
            ip_address=self.request.META.get('REMOTE_ADDR'),
            resource_type='user',
            resource_id=str(instance.id),
            details={'deleted_user_email': instance.email}
        )
        super().perform_destroy(instance)


class UserProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for UserProfile model."""
    serializer_class = UserProfileSerializer
    
    def get_queryset(self):
        # Regular users can only see their profile, admins can see all profiles
        if self.request.user.is_staff or self.request.user.role == 'admin':
            return UserProfile.objects.all()
        return UserProfile.objects.filter(user=self.request.user)
    
    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsOwnerOrAdmin]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]


class UserSettingsViewSet(viewsets.ModelViewSet):
    """ViewSet for UserSettings model."""
    serializer_class = UserSettingsSerializer
    
    def get_queryset(self):
        # Regular users can only see their settings, admins can see all settings
        if self.request.user.is_staff or self.request.user.role == 'admin':
            return UserSettings.objects.all()
        return UserSettings.objects.filter(user=self.request.user)
    
    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsOwnerOrAdmin]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]


class UserConsentViewSet(viewsets.ModelViewSet):
    """ViewSet for UserConsent model."""
    serializer_class = UserConsentSerializer
    
    def get_queryset(self):
        # Regular users can only see their consents, admins can see all consents
        if self.request.user.is_staff or self.request.user.role == 'admin':
            return UserConsent.objects.all()
        return UserConsent.objects.filter(user=self.request.user)
    
    def get_permissions(self):
        permission_classes = [permissions.IsAuthenticated]
        if self.action in ['destroy']:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        # Set user and IP address automatically
        serializer.save(
            user=self.request.user,
            ip_address=self.request.META.get('REMOTE_ADDR'),
            user_agent=self.request.META.get('HTTP_USER_AGENT')
        )


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for AuditLog model (read-only)."""
    serializer_class = AuditLogSerializer
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        return AuditLog.objects.all().order_by('-created_at')