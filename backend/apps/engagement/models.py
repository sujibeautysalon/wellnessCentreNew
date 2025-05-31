from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from apps.core.models import User


class Campaign(models.Model):
    """Marketing campaign model for targeted customer engagement."""
    
    CAMPAIGN_TYPES = [
        ('email', 'Email Campaign'),
        ('sms', 'SMS Campaign'),
        ('push', 'Push Notification'),
        ('multi', 'Multi-channel Campaign'),
    ]

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    campaign_type = models.CharField(_('campaign type'), max_length=20, choices=CAMPAIGN_TYPES)
    status = models.CharField(_('status'), max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Targeting criteria
    audience_filter = models.JSONField(_('audience filter'), default=dict, blank=True,
                                     help_text=_('JSON criteria for audience targeting'))
    
    # Content
    subject = models.CharField(_('subject'), max_length=255, blank=True, null=True,
                             help_text=_('Subject line for email campaigns'))
    content = models.TextField(_('content'), blank=True, null=True)
    template = models.CharField(_('template'), max_length=100, blank=True, null=True,
                              help_text=_('Template identifier'))
    
    # Scheduling
    scheduled_at = models.DateTimeField(_('scheduled at'), blank=True, null=True)
    sent_at = models.DateTimeField(_('sent at'), blank=True, null=True)
    
    # Metrics
    total_recipients = models.IntegerField(_('total recipients'), default=0)
    successful_deliveries = models.IntegerField(_('successful deliveries'), default=0)
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                 related_name='created_campaigns', null=True)
    
    class Meta:
        verbose_name = _('campaign')
        verbose_name_plural = _('campaigns')
    
    def __str__(self):
        return self.name


class CampaignRecipient(models.Model):
    """Tracks individual recipient status for each campaign."""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('opened', 'Opened'),
        ('clicked', 'Clicked'),
        ('bounced', 'Bounced'),
        ('unsubscribed', 'Unsubscribed'),
        ('failed', 'Failed'),
    ]
    
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='recipients')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='campaign_receipts')
    status = models.CharField(_('status'), max_length=20, choices=STATUS_CHOICES, default='pending')
    
    sent_at = models.DateTimeField(_('sent at'), blank=True, null=True)
    delivered_at = models.DateTimeField(_('delivered at'), blank=True, null=True)
    opened_at = models.DateTimeField(_('opened at'), blank=True, null=True)
    clicked_at = models.DateTimeField(_('clicked at'), blank=True, null=True)
    
    # For tracking email opens, clicks, etc.
    tracking_code = models.CharField(_('tracking code'), max_length=100, blank=True, null=True)
    
    # Additional data
    metadata = models.JSONField(_('metadata'), default=dict, blank=True)
    
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('campaign recipient')
        verbose_name_plural = _('campaign recipients')
        unique_together = ('campaign', 'user')
    
    def __str__(self):
        return f"{self.user.email} - {self.campaign.name}"


class Notification(models.Model):
    """Model for individual notifications sent to users."""
    
    NOTIFICATION_TYPES = [
        ('appointment', 'Appointment Notification'),
        ('reminder', 'Reminder'),
        ('billing', 'Billing Notification'),
        ('promotion', 'Promotional Message'),
        ('system', 'System Message'),
    ]
    
    CHANNELS = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('push', 'Push Notification'),
        ('in_app', 'In-App Notification'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('read', 'Read'),
        ('failed', 'Failed'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(_('title'), max_length=255)
    message = models.TextField(_('message'))
    notification_type = models.CharField(_('notification type'), max_length=20, choices=NOTIFICATION_TYPES)
    channel = models.CharField(_('channel'), max_length=20, choices=CHANNELS)
    status = models.CharField(_('status'), max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # If notification is related to a specific object (e.g., an appointment)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, blank=True, null=True)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # For deep linking to specific pages
    action_url = models.CharField(_('action url'), max_length=255, blank=True, null=True)
    
    # Scheduling
    scheduled_at = models.DateTimeField(_('scheduled at'), blank=True, null=True)
    sent_at = models.DateTimeField(_('sent at'), blank=True, null=True)
    read_at = models.DateTimeField(_('read at'), blank=True, null=True)
    
    # Metadata
    metadata = models.JSONField(_('metadata'), default=dict, blank=True)
    
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('notification')
        verbose_name_plural = _('notifications')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.user.email}"


class FeedbackForm(models.Model):
    """Model for creating customizable feedback forms."""
    
    FORM_TYPES = [
        ('satisfaction', 'Satisfaction Survey'),
        ('nps', 'Net Promoter Score'),
        ('session', 'Session Feedback'),
        ('service', 'Service Feedback'),
        ('general', 'General Feedback'),
    ]
    
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    form_type = models.CharField(_('form type'), max_length=20, choices=FORM_TYPES)
    is_active = models.BooleanField(_('active status'), default=True)
    
    # Form structure stored as JSON
    form_structure = models.JSONField(_('form structure'), 
                                    help_text=_('JSON structure defining form fields, validations, etc.'))
    
    # When to trigger the form
    trigger_event = models.CharField(_('trigger event'), max_length=100, blank=True, null=True,
                                   help_text=_('Event that triggers this feedback form'))
    trigger_delay = models.DurationField(_('trigger delay'), blank=True, null=True,
                                       help_text=_('Delay after the trigger event before sending'))
    
    # Appearance
    theme = models.CharField(_('theme'), max_length=50, blank=True, null=True, default='default')
    
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                 related_name='created_feedback_forms', null=True)
    
    class Meta:
        verbose_name = _('feedback form')
        verbose_name_plural = _('feedback forms')
    
    def __str__(self):
        return self.name


class FeedbackResponse(models.Model):
    """Stores user responses to feedback forms."""
    
    feedback_form = models.ForeignKey(FeedbackForm, on_delete=models.CASCADE, related_name='responses')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='feedback_responses')
    
    # For anonymous feedback
    is_anonymous = models.BooleanField(_('anonymous response'), default=False)
    
    # The actual response data
    response_data = models.JSONField(_('response data'))
    
    # If the feedback is related to a specific object (e.g., an appointment)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, blank=True, null=True)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # NPS and satisfaction metrics for easier querying
    satisfaction_score = models.IntegerField(_('satisfaction score'), blank=True, null=True)
    nps_score = models.IntegerField(_('NPS score'), blank=True, null=True)
    
    # Timestamps
    submitted_at = models.DateTimeField(_('submitted at'), auto_now_add=True)
    
    # Additional metadata
    metadata = models.JSONField(_('metadata'), default=dict, blank=True)
    
    class Meta:
        verbose_name = _('feedback response')
        verbose_name_plural = _('feedback responses')
        ordering = ['-submitted_at']
    
    def __str__(self):
        if self.is_anonymous:
            return f"Anonymous response - {self.feedback_form.name} - {self.submitted_at}"
        return f"{self.user.email} - {self.feedback_form.name} - {self.submitted_at}"


class Loyalty(models.Model):
    """User loyalty program model for tracking points and rewards."""
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='loyalty')
    points_balance = models.IntegerField(_('points balance'), default=0)
    lifetime_points = models.IntegerField(_('lifetime points'), default=0)
    tier = models.CharField(_('loyalty tier'), max_length=50, default='standard')
    enrollment_date = models.DateTimeField(_('enrollment date'), auto_now_add=True)
    last_activity_date = models.DateTimeField(_('last activity date'), auto_now=True)
    
    # Additional preferences and metadata
    preferences = models.JSONField(_('preferences'), default=dict, blank=True)
    metadata = models.JSONField(_('metadata'), default=dict, blank=True)
    
    class Meta:
        verbose_name = _('loyalty')
        verbose_name_plural = _('loyalty')
    
    def __str__(self):
        return f"{self.user.email} - {self.points_balance} points"


class LoyaltyTransaction(models.Model):
    """Records for loyalty point transactions."""
    
    TRANSACTION_TYPES = [
        ('earn', 'Points Earned'),
        ('redeem', 'Points Redeemed'),
        ('expire', 'Points Expired'),
        ('adjustment', 'Manual Adjustment'),
        ('bonus', 'Bonus Points'),
    ]
    
    loyalty = models.ForeignKey(Loyalty, on_delete=models.CASCADE, related_name='transactions')
    points = models.IntegerField(_('points'))
    transaction_type = models.CharField(_('transaction type'), max_length=20, choices=TRANSACTION_TYPES)
    description = models.CharField(_('description'), max_length=255)
    
    # If transaction is related to a specific object (e.g., an appointment)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, blank=True, null=True)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Reference for grouping related transactions
    reference_code = models.CharField(_('reference code'), max_length=100, blank=True, null=True)
    
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                 related_name='+', null=True, blank=True)
    
    class Meta:
        verbose_name = _('loyalty transaction')
        verbose_name_plural = _('loyalty transactions')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.loyalty.user.email} - {self.transaction_type} - {self.points} points"


class Referral(models.Model):
    """Referral tracking system model."""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('converted', 'Converted'),
        ('expired', 'Expired'),
    ]
    
    referrer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='referrals_made')
    email = models.EmailField(_('email address'))
    name = models.CharField(_('name'), max_length=255, blank=True, null=True)
    phone_number = models.CharField(_('phone number'), max_length=20, blank=True, null=True)
    
    # The person who was referred (if they signed up)
    referred_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                    related_name='referred_by', null=True, blank=True)
    
    status = models.CharField(_('status'), max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Unique code for tracking this specific referral
    referral_code = models.CharField(_('referral code'), max_length=100, unique=True)
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    converted_at = models.DateTimeField(_('converted at'), blank=True, null=True)
    
    # Rewards
    referrer_reward_given = models.BooleanField(_('referrer reward given'), default=False)
    referred_reward_given = models.BooleanField(_('referred reward given'), default=False)
    
    # Message
    message = models.TextField(_('message'), blank=True, null=True)
    
    class Meta:
        verbose_name = _('referral')
        verbose_name_plural = _('referrals')
        unique_together = ('referrer', 'email')
    
    def __str__(self):
        return f"Referral from {self.referrer.email} to {self.email}"