from rest_framework import serializers
from apps.core.models import User
from apps.engagement.models import (
    Campaign, CampaignRecipient, Notification, FeedbackForm, 
    FeedbackResponse, Loyalty, LoyaltyTransaction, Referral
)


class CampaignRecipientSerializer(serializers.ModelSerializer):
    """Serializer for campaign recipients."""
    
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.SerializerMethodField()
    
    class Meta:
        model = CampaignRecipient
        fields = [
            'id', 'campaign', 'user', 'user_email', 'user_name', 'status',
            'sent_at', 'delivered_at', 'opened_at', 'clicked_at',
            'tracking_code', 'metadata', 'created_at', 'updated_at'
        ]
        read_only_fields = ['sent_at', 'delivered_at', 'opened_at', 'clicked_at', 'created_at', 'updated_at']
    
    def get_user_name(self, obj):
        """Get user's full name or email if name not available."""
        if obj.user.first_name:
            return f"{obj.user.first_name} {obj.user.last_name}"
        return obj.user.email


class CampaignSerializer(serializers.ModelSerializer):
    """Serializer for campaign data."""
    
    created_by_name = serializers.SerializerMethodField(read_only=True)
    recipients_count = serializers.IntegerField(read_only=True)
    engagement_rate = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Campaign
        fields = [
            'id', 'name', 'description', 'campaign_type', 'status',
            'audience_filter', 'subject', 'content', 'template',
            'scheduled_at', 'sent_at', 'total_recipients', 'successful_deliveries',
            'created_at', 'updated_at', 'created_by', 'created_by_name',
            'recipients_count', 'engagement_rate'
        ]
        read_only_fields = ['sent_at', 'created_at', 'updated_at']
    
    def get_created_by_name(self, obj):
        """Get the name of the user who created the campaign."""
        if obj.created_by:
            if obj.created_by.first_name:
                return f"{obj.created_by.first_name} {obj.created_by.last_name}"
            return obj.created_by.email
        return None
    
    def get_engagement_rate(self, obj):
        """Calculate the engagement rate based on successful deliveries and total recipients."""
        if obj.total_recipients > 0:
            return obj.successful_deliveries / obj.total_recipients * 100
        return 0


class CampaignDetailSerializer(CampaignSerializer):
    """Extended campaign serializer with recipient details."""
    
    recipients = CampaignRecipientSerializer(many=True, read_only=True)
    
    class Meta(CampaignSerializer.Meta):
        fields = CampaignSerializer.Meta.fields + ['recipients']


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for user notifications."""
    
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'user', 'user_email', 'title', 'message', 
            'notification_type', 'channel', 'status', 
            'content_type', 'object_id', 'action_url',
            'scheduled_at', 'sent_at', 'read_at', 
            'metadata', 'created_at', 'updated_at'
        ]
        read_only_fields = ['sent_at', 'read_at', 'created_at', 'updated_at']


class FeedbackFormSerializer(serializers.ModelSerializer):
    """Serializer for feedback forms."""
    
    created_by_name = serializers.SerializerMethodField(read_only=True)
    response_count = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = FeedbackForm
        fields = [
            'id', 'name', 'description', 'form_type', 'is_active',
            'form_structure', 'trigger_event', 'trigger_delay', 'theme',
            'created_at', 'updated_at', 'created_by', 'created_by_name',
            'response_count'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_created_by_name(self, obj):
        """Get the name of the user who created the feedback form."""
        if obj.created_by:
            if obj.created_by.first_name:
                return f"{obj.created_by.first_name} {obj.created_by.last_name}"
            return obj.created_by.email
        return None
    
    def get_response_count(self, obj):
        """Get the number of responses to this form."""
        return obj.responses.count()


class FeedbackResponseSerializer(serializers.ModelSerializer):
    """Serializer for feedback responses."""
    
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.SerializerMethodField()
    form_name = serializers.CharField(source='feedback_form.name', read_only=True)
    
    class Meta:
        model = FeedbackResponse
        fields = [
            'id', 'feedback_form', 'form_name', 'user', 'user_email', 'user_name', 
            'is_anonymous', 'response_data', 'content_type', 'object_id',
            'satisfaction_score', 'nps_score', 'submitted_at', 'metadata'
        ]
        read_only_fields = ['submitted_at']
    
    def get_user_name(self, obj):
        """Get user's full name or email if name not available and response is not anonymous."""
        if obj.is_anonymous:
            return "Anonymous"
        if obj.user.first_name:
            return f"{obj.user.first_name} {obj.user.last_name}"
        return obj.user.email


class LoyaltyTransactionSerializer(serializers.ModelSerializer):
    """Serializer for loyalty point transactions."""
    
    class Meta:
        model = LoyaltyTransaction
        fields = [
            'id', 'loyalty', 'points', 'transaction_type', 'description', 
            'content_type', 'object_id', 'reference_code',
            'created_at', 'created_by'
        ]
        read_only_fields = ['created_at']


class LoyaltySerializer(serializers.ModelSerializer):
    """Serializer for user loyalty information."""
    
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.SerializerMethodField()
    recent_transactions = serializers.SerializerMethodField()
    
    class Meta:
        model = Loyalty
        fields = [
            'id', 'user', 'user_email', 'user_name', 'points_balance', 'lifetime_points',
            'tier', 'enrollment_date', 'last_activity_date', 
            'preferences', 'metadata', 'recent_transactions'
        ]
        read_only_fields = ['enrollment_date', 'last_activity_date']
    
    def get_user_name(self, obj):
        """Get user's full name or email if name not available."""
        if obj.user.first_name:
            return f"{obj.user.first_name} {obj.user.last_name}"
        return obj.user.email
    
    def get_recent_transactions(self, obj):
        """Get the 5 most recent loyalty transactions."""
        transactions = obj.transactions.all()[:5]
        return LoyaltyTransactionSerializer(transactions, many=True).data


class ReferralSerializer(serializers.ModelSerializer):
    """Serializer for referral data."""
    
    referrer_email = serializers.EmailField(source='referrer.email', read_only=True)
    referrer_name = serializers.SerializerMethodField()
    referred_user_email = serializers.EmailField(source='referred_user.email', read_only=True)
    
    class Meta:
        model = Referral
        fields = [
            'id', 'referrer', 'referrer_email', 'referrer_name',
            'email', 'name', 'phone_number', 
            'referred_user', 'referred_user_email', 'status',
            'referral_code', 'created_at', 'converted_at',
            'referrer_reward_given', 'referred_reward_given', 'message'
        ]
        read_only_fields = ['referral_code', 'created_at', 'converted_at']
    
    def get_referrer_name(self, obj):
        """Get referrer's full name or email if name not available."""
        if obj.referrer.first_name:
            return f"{obj.referrer.first_name} {obj.referrer.last_name}"
        return obj.referrer.email