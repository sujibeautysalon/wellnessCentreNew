from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Q
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType

from apps.core.permissions import IsAdminOrTherapist, IsOwner
from apps.engagement.models import (
    Campaign, CampaignRecipient, Notification, FeedbackForm, 
    FeedbackResponse, Loyalty, LoyaltyTransaction, Referral
)
from apps.engagement.serializers import (
    CampaignSerializer, CampaignDetailSerializer, CampaignRecipientSerializer,
    NotificationSerializer, FeedbackFormSerializer, FeedbackResponseSerializer,
    LoyaltySerializer, LoyaltyTransactionSerializer, ReferralSerializer
)

User = get_user_model()


class CampaignViewSet(viewsets.ModelViewSet):
    """
    ViewSet for campaigns - allows admin users to create and manage marketing campaigns.
    """
    queryset = Campaign.objects.all()
    serializer_class = CampaignSerializer
    permission_classes = [IsAdminOrTherapist]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'status']
    ordering_fields = ['name', 'status', 'created_at', 'scheduled_at']
    ordering = ['-created_at']

    def get_queryset(self):
        """Filter campaigns and annotate with recipient count."""
        queryset = Campaign.objects.annotate(
            recipients_count=Count('recipients')
        )
        
        # Filter by campaign type if provided
        campaign_type = self.request.query_params.get('type')
        if campaign_type:
            queryset = queryset.filter(campaign_type=campaign_type)
            
        # Filter by status if provided
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)
            
        return queryset
    
    def get_serializer_class(self):
        """Return detail serializer for retrieve actions."""
        if self.action == 'retrieve':
            return CampaignDetailSerializer
        return CampaignSerializer
    
    def perform_create(self, serializer):
        """Set the created_by field to the current user."""
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def send(self, request, pk=None):
        """
        Trigger sending of a campaign.
        
        This would typically connect to a task queue like Celery for actual delivery.
        """
        campaign = self.get_object()
        
        # Check if campaign can be sent
        if campaign.status not in ['draft', 'scheduled']:
            return Response(
                {"detail": "Only campaigns with 'draft' or 'scheduled' status can be sent"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Set to active and record sent time
        campaign.status = 'active'
        campaign.sent_at = timezone.now()
        campaign.save()
        
        # Here we would typically trigger a Celery task for actual sending
        # e.g. send_campaign_task.delay(campaign.id)
        
        return Response({"detail": "Campaign sending initiated"}, status=status.HTTP_202_ACCEPTED)
    
    @action(detail=True, methods=['post'])
    def add_recipients(self, request, pk=None):
        """Add recipients to a campaign."""
        campaign = self.get_object()
        
        # Cannot add recipients to campaigns that have already been sent
        if campaign.status not in ['draft', 'scheduled']:
            return Response(
                {"detail": "Cannot add recipients to campaigns that have already been sent or completed"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user_ids = request.data.get('user_ids', [])
        if not user_ids:
            return Response(
                {"detail": "No user IDs provided"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get users and create recipients
        users = User.objects.filter(id__in=user_ids)
        
        recipients_created = []
        for user in users:
            recipient, created = CampaignRecipient.objects.get_or_create(
                campaign=campaign,
                user=user,
                defaults={'status': 'pending'}
            )
            if created:
                recipients_created.append(recipient.id)
        
        # Update total recipients count
        campaign.total_recipients = CampaignRecipient.objects.filter(campaign=campaign).count()
        campaign.save()
        
        return Response({
            "detail": f"{len(recipients_created)} recipients added to campaign",
            "recipient_ids": recipients_created
        }, status=status.HTTP_201_CREATED)


class NotificationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for user notifications.
    """
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'message']
    ordering_fields = ['created_at', 'scheduled_at', 'notification_type', 'status']
    ordering = ['-created_at']

    def get_queryset(self):
        """
        Filter notifications to show only those for the current user,
        unless user is admin/therapist with specific permission.
        """
        user = self.request.user
        queryset = Notification.objects.all()
        
        # If not admin/therapist, filter by current user
        if not user.is_staff and user.role not in ['admin', 'therapist']:
            queryset = queryset.filter(user=user)
            
        # Filter by notification type if provided
        notification_type = self.request.query_params.get('type')
        if notification_type:
            queryset = queryset.filter(notification_type=notification_type)
            
        # Filter by status if provided
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)
            
        # Filter by channel if provided
        channel = self.request.query_params.get('channel')
        if channel:
            queryset = queryset.filter(channel=channel)
            
        return queryset
    
    def perform_create(self, serializer):
        """Set defaults for notification creation."""
        # Here we could add processing logic, e.g. for selecting notification channel
        # based on user preferences or determining related object
        serializer.save()
    
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """Mark a notification as read."""
        notification = self.get_object()
        
        # Only the notification owner or staff can mark it as read
        if notification.user != request.user and not request.user.is_staff:
            return Response(
                {"detail": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        notification.status = 'read'
        notification.read_at = timezone.now()
        notification.save()
        
        return Response({"detail": "Notification marked as read"}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        """Mark all user's notifications as read."""
        Notification.objects.filter(user=request.user, status__in=['sent', 'delivered']).update(
            status='read',
            read_at=timezone.now()
        )
        
        return Response({"detail": "All notifications marked as read"}, status=status.HTTP_200_OK)


class FeedbackFormViewSet(viewsets.ModelViewSet):
    """
    ViewSet for feedback forms. Only admin and therapists can create/modify forms.
    Customers can view active forms.
    """
    queryset = FeedbackForm.objects.all()
    serializer_class = FeedbackFormSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'form_type']
    ordering_fields = ['name', 'created_at', 'form_type']
    ordering = ['name']

    def get_permissions(self):
        """
        Restrict form creation/modification to admin/therapists,
        but allow customers to view active forms.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminOrTherapist]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """
        Filter forms based on user role and request parameters.
        """
        user = self.request.user
        queryset = FeedbackForm.objects.all()
        
        # If user is not admin/therapist, show only active forms
        if not user.is_staff and user.role not in ['admin', 'therapist']:
            queryset = queryset.filter(is_active=True)
        
        # Filter by form type if provided
        form_type = self.request.query_params.get('type')
        if form_type:
            queryset = queryset.filter(form_type=form_type)
            
        # Filter by trigger event if provided
        trigger_event = self.request.query_params.get('trigger_event')
        if trigger_event:
            queryset = queryset.filter(trigger_event=trigger_event)
            
        # Annotate with response count
        queryset = queryset.annotate(response_count=Count('responses'))
        
        return queryset
    
    def perform_create(self, serializer):
        """Set the created_by field to the current user."""
        serializer.save(created_by=self.request.user)


class FeedbackResponseViewSet(viewsets.ModelViewSet):
    """
    ViewSet for feedback responses. Customers can create responses.
    Only admin/therapists can list and view all responses.
    """
    serializer_class = FeedbackResponseSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['feedback_form__name', 'user__email']
    ordering_fields = ['submitted_at', 'satisfaction_score', 'nps_score']
    ordering = ['-submitted_at']

    def get_queryset(self):
        """
        Filter feedback responses based on user role.
        """
        user = self.request.user
        
        # Admin/therapist can see all responses
        if user.is_staff or user.role in ['admin', 'therapist']:
            queryset = FeedbackResponse.objects.all()
        else:
            # Regular users can only see their own non-anonymous responses
            queryset = FeedbackResponse.objects.filter(
                Q(user=user, is_anonymous=False)
            )
        
        # Filter by form if provided
        form_id = self.request.query_params.get('form_id')
        if form_id:
            queryset = queryset.filter(feedback_form_id=form_id)
            
        # Filter by content type and object id if provided (e.g., for appointment feedback)
        content_type_id = self.request.query_params.get('content_type_id')
        object_id = self.request.query_params.get('object_id')
        if content_type_id and object_id:
            queryset = queryset.filter(
                content_type_id=content_type_id, 
                object_id=object_id
            )
            
        return queryset
    
    def perform_create(self, serializer):
        """Set the user field to the current user if not anonymous."""
        is_anonymous = self.request.data.get('is_anonymous', False)
        
        if not is_anonymous:
            serializer.save(user=self.request.user)
        else:
            # For anonymous responses, we still track the user internally
            # but make sure response is marked anonymous
            serializer.save(user=self.request.user, is_anonymous=True)


class LoyaltyViewSet(viewsets.ModelViewSet):
    """
    ViewSet for user loyalty information.
    Customers can view their own loyalty info.
    Admin/therapists can view and update loyalty information.
    """
    serializer_class = LoyaltySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['user__email', 'tier']
    ordering_fields = ['points_balance', 'lifetime_points', 'enrollment_date']
    ordering = ['-points_balance']

    def get_queryset(self):
        """
        Filter loyalty data based on user role.
        """
        user = self.request.user
        
        # Admin/therapist can see all loyalty data
        if user.is_staff or user.role in ['admin', 'therapist']:
            return Loyalty.objects.all()
        
        # Regular users can only see their own loyalty data
        return Loyalty.objects.filter(user=user)
    
    @action(detail=False, methods=['get'])
    def my_loyalty(self, request):
        """Get the current user's loyalty data."""
        try:
            loyalty = Loyalty.objects.get(user=request.user)
            serializer = self.get_serializer(loyalty)
            return Response(serializer.data)
        except Loyalty.DoesNotExist:
            # Create new loyalty record if one doesn't exist
            loyalty = Loyalty.objects.create(
                user=request.user,
                points_balance=0,
                lifetime_points=0,
                tier='standard'
            )
            serializer = self.get_serializer(loyalty)
            return Response(serializer.data)


class LoyaltyTransactionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for loyalty transactions.
    Customers can view their own transactions.
    Admin/therapists can create and view all transactions.
    """
    serializer_class = LoyaltyTransactionSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['description', 'transaction_type', 'reference_code']
    ordering_fields = ['created_at', 'points']
    ordering = ['-created_at']

    def get_permissions(self):
        """
        Restrict transaction creation to admin/therapists,
        but allow customers to view their own transactions.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminOrTherapist]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Filter loyalty transactions based on user role.
        """
        user = self.request.user
        
        # Admin/therapist can see all transactions
        if user.is_staff or user.role in ['admin', 'therapist']:
            queryset = LoyaltyTransaction.objects.all()
        else:
            # Regular users can only see their own transactions
            queryset = LoyaltyTransaction.objects.filter(loyalty__user=user)
        
        # Filter by transaction type if provided
        transaction_type = self.request.query_params.get('type')
        if transaction_type:
            queryset = queryset.filter(transaction_type=transaction_type)
            
        # Filter by date range if provided
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)
            
        return queryset
    
    def perform_create(self, serializer):
        """
        Create a transaction and update the user's loyalty point balance.
        """
        transaction = serializer.save(created_by=self.request.user)
        
        # Update the user's loyalty balance
        loyalty = transaction.loyalty
        if transaction.transaction_type == 'earn':
            loyalty.points_balance += transaction.points
            loyalty.lifetime_points += transaction.points
        elif transaction.transaction_type == 'redeem':
            loyalty.points_balance -= transaction.points
        elif transaction.transaction_type == 'expire':
            loyalty.points_balance -= transaction.points
        elif transaction.transaction_type == 'adjustment' or transaction.transaction_type == 'bonus':
            loyalty.points_balance += transaction.points
            if transaction.points > 0:
                loyalty.lifetime_points += transaction.points
        
        loyalty.save()


class ReferralViewSet(viewsets.ModelViewSet):
    """
    ViewSet for referrals.
    Customers can create and view their own referrals.
    Admin/therapists can view all referrals.
    """
    serializer_class = ReferralSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['email', 'name', 'referral_code']
    ordering_fields = ['created_at', 'status']
    ordering = ['-created_at']

    def get_queryset(self):
        """
        Filter referrals based on user role.
        """
        user = self.request.user
        
        # Admin/therapist can see all referrals
        if user.is_staff or user.role in ['admin', 'therapist']:
            queryset = Referral.objects.all()
        else:
            # Regular users can only see their own referrals
            queryset = Referral.objects.filter(referrer=user)
        
        # Filter by status if provided
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)
            
        return queryset
    
    def perform_create(self, serializer):
        """Set the referrer to the current user and generate a referral code."""
        import uuid
        referral_code = f"REF-{uuid.uuid4().hex[:8].upper()}"
        serializer.save(referrer=self.request.user, referral_code=referral_code)
    
    @action(detail=True, methods=['post'])
    def mark_converted(self, request, pk=None):
        """
        Mark a referral as converted when the referred user signs up.
        This would typically be called internally by the registration process.
        """
        referral = self.get_object()
        referred_user_id = request.data.get('user_id')
        
        if not referred_user_id:
            return Response(
                {"detail": "No user ID provided"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            referred_user = User.objects.get(id=referred_user_id)
        except User.DoesNotExist:
            return Response(
                {"detail": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Update the referral
        referral.referred_user = referred_user
        referral.status = 'converted'
        referral.converted_at = timezone.now()
        referral.save()
        
        # TODO: Trigger reward process for referrer and referred
        # This would typically connect to a task queue
        
        return Response({"detail": "Referral marked as converted"}, status=status.HTTP_200_OK)