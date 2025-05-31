from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.engagement.models import (
    Campaign, CampaignRecipient, Notification, FeedbackForm, 
    FeedbackResponse, Loyalty, LoyaltyTransaction, Referral
)


class CampaignRecipientInline(admin.TabularInline):
    """Inline editor for campaign recipients."""
    model = CampaignRecipient
    extra = 0
    readonly_fields = ['sent_at', 'delivered_at', 'opened_at', 'clicked_at']


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    """Admin interface for campaigns."""
    list_display = ['name', 'campaign_type', 'status', 'scheduled_at', 'total_recipients', 'successful_deliveries']
    list_filter = ['campaign_type', 'status', 'created_at', 'scheduled_at']
    search_fields = ['name', 'description', 'subject']
    readonly_fields = ['sent_at', 'created_at', 'updated_at', 'total_recipients', 'successful_deliveries']
    fieldsets = [
        (_('Basic Information'), {
            'fields': ['name', 'description', 'campaign_type', 'status', 'created_by']
        }),
        (_('Audience'), {
            'fields': ['audience_filter', 'total_recipients']
        }),
        (_('Content'), {
            'fields': ['subject', 'content', 'template']
        }),
        (_('Scheduling'), {
            'fields': ['scheduled_at', 'sent_at']
        }),
        (_('Performance'), {
            'fields': ['successful_deliveries']
        }),
        (_('Metadata'), {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        }),
    ]
    inlines = [CampaignRecipientInline]


@admin.register(CampaignRecipient)
class CampaignRecipientAdmin(admin.ModelAdmin):
    """Admin interface for campaign recipients."""
    list_display = ['user', 'campaign', 'status', 'sent_at', 'opened_at']
    list_filter = ['status', 'sent_at', 'delivered_at', 'opened_at', 'campaign']
    search_fields = ['user__email', 'campaign__name']
    readonly_fields = ['sent_at', 'delivered_at', 'opened_at', 'clicked_at', 'created_at', 'updated_at']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Admin interface for notifications."""
    list_display = ['title', 'user', 'notification_type', 'channel', 'status', 'created_at']
    list_filter = ['notification_type', 'channel', 'status', 'created_at']
    search_fields = ['title', 'message', 'user__email']
    readonly_fields = ['sent_at', 'read_at', 'created_at', 'updated_at']
    fieldsets = [
        (_('Basic Information'), {
            'fields': ['user', 'title', 'message', 'notification_type', 'channel', 'status']
        }),
        (_('Related Content'), {
            'fields': ['content_type', 'object_id', 'action_url']
        }),
        (_('Scheduling'), {
            'fields': ['scheduled_at', 'sent_at', 'read_at']
        }),
        (_('Metadata'), {
            'fields': ['metadata', 'created_at', 'updated_at'],
            'classes': ['collapse']
        }),
    ]


@admin.register(FeedbackForm)
class FeedbackFormAdmin(admin.ModelAdmin):
    """Admin interface for feedback forms."""
    list_display = ['name', 'form_type', 'is_active', 'trigger_event', 'created_at']
    list_filter = ['form_type', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = [
        (_('Basic Information'), {
            'fields': ['name', 'description', 'form_type', 'is_active', 'created_by']
        }),
        (_('Form Structure'), {
            'fields': ['form_structure', 'theme']
        }),
        (_('Trigger Settings'), {
            'fields': ['trigger_event', 'trigger_delay']
        }),
        (_('Metadata'), {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        }),
    ]


class FeedbackResponseAdmin(admin.ModelAdmin):
    """Admin interface for feedback responses."""
    list_display = ['feedback_form', 'user', 'is_anonymous', 'satisfaction_score', 'nps_score', 'submitted_at']
    list_filter = ['is_anonymous', 'submitted_at', 'feedback_form', 'satisfaction_score', 'nps_score']
    search_fields = ['user__email', 'feedback_form__name', 'response_data']
    readonly_fields = ['submitted_at']
    fieldsets = [
        (_('Basic Information'), {
            'fields': ['feedback_form', 'user', 'is_anonymous', 'submitted_at']
        }),
        (_('Response Data'), {
            'fields': ['response_data', 'satisfaction_score', 'nps_score']
        }),
        (_('Related Content'), {
            'fields': ['content_type', 'object_id'],
            'classes': ['collapse']
        }),
        (_('Metadata'), {
            'fields': ['metadata'],
            'classes': ['collapse']
        }),
    ]

admin.site.register(FeedbackResponse, FeedbackResponseAdmin)


class LoyaltyTransactionInline(admin.TabularInline):
    """Inline editor for loyalty transactions."""
    model = LoyaltyTransaction
    extra = 0
    readonly_fields = ['created_at']


@admin.register(Loyalty)
class LoyaltyAdmin(admin.ModelAdmin):
    """Admin interface for loyalty information."""
    list_display = ['user', 'points_balance', 'lifetime_points', 'tier', 'enrollment_date']
    list_filter = ['tier', 'enrollment_date']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['enrollment_date', 'last_activity_date']
    inlines = [LoyaltyTransactionInline]
    fieldsets = [
        (_('User Information'), {
            'fields': ['user', 'enrollment_date', 'last_activity_date']
        }),
        (_('Points & Tier'), {
            'fields': ['points_balance', 'lifetime_points', 'tier']
        }),
        (_('Additional Data'), {
            'fields': ['preferences', 'metadata'],
            'classes': ['collapse']
        }),
    ]


@admin.register(LoyaltyTransaction)
class LoyaltyTransactionAdmin(admin.ModelAdmin):
    """Admin interface for loyalty transactions."""
    list_display = ['loyalty', 'points', 'transaction_type', 'description', 'created_at']
    list_filter = ['transaction_type', 'created_at']
    search_fields = ['loyalty__user__email', 'description', 'reference_code']
    readonly_fields = ['created_at']
    fieldsets = [
        (_('Basic Information'), {
            'fields': ['loyalty', 'points', 'transaction_type', 'description']
        }),
        (_('Related Content'), {
            'fields': ['content_type', 'object_id', 'reference_code']
        }),
        (_('Metadata'), {
            'fields': ['created_at', 'created_by'],
            'classes': ['collapse']
        }),
    ]


@admin.register(Referral)
class ReferralAdmin(admin.ModelAdmin):
    """Admin interface for referrals."""
    list_display = ['referrer', 'email', 'status', 'referred_user', 'created_at']
    list_filter = ['status', 'created_at', 'referrer_reward_given', 'referred_reward_given']
    search_fields = ['email', 'name', 'referrer__email', 'referred_user__email', 'referral_code']
    readonly_fields = ['referral_code', 'created_at', 'converted_at']
    fieldsets = [
        (_('Referral Information'), {
            'fields': ['referrer', 'email', 'name', 'phone_number', 'referral_code']
        }),
        (_('Status'), {
            'fields': ['status', 'referred_user', 'created_at', 'converted_at']
        }),
        (_('Rewards'), {
            'fields': ['referrer_reward_given', 'referred_reward_given']
        }),
        (_('Additional Data'), {
            'fields': ['message'],
            'classes': ['collapse']
        }),
    ]