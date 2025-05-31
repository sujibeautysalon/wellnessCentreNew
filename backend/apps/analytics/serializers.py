# filepath: c:\Users\cadsa\OneDrive\Personal\Full stack web development\wellnessCentre\backend\apps\analytics\serializers.py
from rest_framework import serializers
from apps.analytics.models import (
    Dashboard, PerformanceMetric, MetricSnapshot, AnalyticsReport,
    ServiceAnalytics, CustomerJourneyStep
)
from apps.core.serializers import UserSerializer
from apps.clinic.serializers import BranchSerializer, ServiceSerializer


class DashboardSerializer(serializers.ModelSerializer):
    """Serializer for Dashboard model."""
    
    user_detail = UserSerializer(source='user', read_only=True)
    
    class Meta:
        model = Dashboard
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class MetricSnapshotSerializer(serializers.ModelSerializer):
    """Serializer for MetricSnapshot model."""
    
    class Meta:
        model = MetricSnapshot
        fields = '__all__'


class PerformanceMetricSerializer(serializers.ModelSerializer):
    """Serializer for PerformanceMetric model."""
    
    branch_detail = BranchSerializer(source='branch', read_only=True)
    created_by_detail = UserSerializer(source='created_by', read_only=True)
    snapshots = MetricSnapshotSerializer(many=True, read_only=True)
    progress_percentage = serializers.SerializerMethodField()
    trend = serializers.SerializerMethodField()
    
    class Meta:
        model = PerformanceMetric
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')
    
    def get_progress_percentage(self, obj):
        """Calculate percentage of target achieved."""
        if obj.target_value and obj.target_value > 0 and obj.current_value is not None:
            return min(100, float(obj.current_value / obj.target_value) * 100)
        return None
    
    def get_trend(self, obj):
        """Calculate trend over the last few snapshots."""
        recent_snapshots = obj.snapshots.order_by('-timestamp')[:5]
        if len(recent_snapshots) < 2:
            return 'neutral'
        
        latest = recent_snapshots[0].value
        previous = recent_snapshots[-1].value
        
        if latest > previous:
            return 'up'
        elif latest < previous:
            return 'down'
        return 'neutral'


class AnalyticsReportSerializer(serializers.ModelSerializer):
    """Serializer for AnalyticsReport model."""
    
    branch_detail = BranchSerializer(source='branch', read_only=True)
    generated_by_detail = UserSerializer(source='generated_by', read_only=True)
    
    class Meta:
        model = AnalyticsReport
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'file', 'report_data', 
                           'last_run', 'next_run')


class ServiceAnalyticsSerializer(serializers.ModelSerializer):
    """Serializer for ServiceAnalytics model."""
    
    service_detail = ServiceSerializer(source='service', read_only=True)
    
    class Meta:
        model = ServiceAnalytics
        fields = '__all__'


class CustomerJourneyStepSerializer(serializers.ModelSerializer):
    """Serializer for CustomerJourneyStep model."""
    
    user_detail = UserSerializer(source='user', read_only=True)
    
    class Meta:
        model = CustomerJourneyStep
        fields = '__all__'
        read_only_fields = ('timestamp',)


class CustomerJourneyAnalyticsSerializer(serializers.Serializer):
    """Serializer for customer journey analytics data."""
    
    user_id = serializers.IntegerField()
    user_email = serializers.EmailField()
    first_visit_date = serializers.DateTimeField(allow_null=True)
    signup_date = serializers.DateTimeField(allow_null=True)
    first_booking_date = serializers.DateTimeField(allow_null=True)
    first_appointment_date = serializers.DateTimeField(allow_null=True)
    days_signup_to_booking = serializers.IntegerField(allow_null=True)
    days_booking_to_appointment = serializers.IntegerField(allow_null=True)
    total_bookings = serializers.IntegerField()
    total_appointments = serializers.IntegerField()
    total_feedback = serializers.IntegerField()
    total_referrals = serializers.IntegerField()
    total_cancellations = serializers.IntegerField()
    lifetime_value = serializers.DecimalField(max_digits=12, decimal_places=2)
    sources = serializers.DictField(child=serializers.IntegerField())
    journey_steps = CustomerJourneyStepSerializer(many=True, read_only=True)