from rest_framework import serializers
from .models import Branch, Service, TherapistProfile, TherapistAvailability, Holiday


class BranchSerializer(serializers.ModelSerializer):
    """Serializer for Branch model."""
    
    class Meta:
        model = Branch
        fields = ['id', 'name', 'address', 'city', 'state', 'country', 'postal_code',
                 'phone', 'email', 'latitude', 'longitude', 'timezone', 'opening_hours',
                 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ServiceSerializer(serializers.ModelSerializer):
    """Serializer for Service model."""
    
    class Meta:
        model = Service
        fields = ['id', 'name', 'description', 'duration', 'price', 'discount_price',
                 'category', 'is_active', 'image', 'max_capacity', 'preparation_time',
                 'cooldown_time', 'available_branches', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class TherapistProfileSerializer(serializers.ModelSerializer):
    """Serializer for TherapistProfile model."""
    
    user_details = serializers.SerializerMethodField()
    branches_details = BranchSerializer(source='branches', many=True, read_only=True)
    services_details = ServiceSerializer(source='services', many=True, read_only=True)
    
    class Meta:
        model = TherapistProfile
        fields = ['id', 'user', 'user_details', 'title', 'bio', 'specializations',
                 'years_of_experience', 'education', 'certifications', 'languages',
                 'branches', 'branches_details', 'services', 'services_details', 
                 'profile_image', 'average_rating', 'rating_count', 'is_active',
                 'created_at', 'updated_at']
        read_only_fields = ['id', 'average_rating', 'rating_count', 'created_at', 'updated_at']
    
    def get_user_details(self, obj):
        """Get basic user details."""
        return {
            'id': obj.user.id,
            'email': obj.user.email,
            'first_name': obj.user.first_name,
            'last_name': obj.user.last_name,
            'full_name': obj.user.get_full_name(),
            'phone_number': obj.user.phone_number
        }


class TherapistAvailabilitySerializer(serializers.ModelSerializer):
    """Serializer for TherapistAvailability model."""
    
    therapist_name = serializers.SerializerMethodField()
    branch_name = serializers.SerializerMethodField()
    service_name = serializers.SerializerMethodField()
    
    class Meta:
        model = TherapistAvailability
        fields = ['id', 'therapist', 'therapist_name', 'branch', 'branch_name', 
                 'service', 'service_name', 'start_time', 'end_time', 'is_available', 
                 'recurrence', 'recurrence_end_date', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_therapist_name(self, obj):
        if obj.therapist and obj.therapist.user:
            return obj.therapist.user.get_full_name()
        return None
    
    def get_branch_name(self, obj):
        if obj.branch:
            return obj.branch.name
        return None
    
    def get_service_name(self, obj):
        if obj.service:
            return obj.service.name
        return None


class HolidaySerializer(serializers.ModelSerializer):
    """Serializer for Holiday model."""
    
    branch_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Holiday
        fields = ['id', 'branch', 'branch_name', 'name', 'description', 'start_date', 
                 'end_date', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_branch_name(self, obj):
        if obj.branch:
            return obj.branch.name
        return 'All Branches'


class TherapistPublicSerializer(serializers.ModelSerializer):
    """Serializer for public therapist profiles."""
    
    user_details = serializers.SerializerMethodField()
    services = ServiceSerializer(many=True, read_only=True)
    branches = BranchSerializer(many=True, read_only=True)
    
    class Meta:
        model = TherapistProfile
        fields = ['id', 'user_details', 'title', 'bio', 'specializations',
                 'years_of_experience', 'education', 'certifications', 'languages',
                 'branches', 'services', 'profile_image', 'average_rating', 'rating_count']
        read_only_fields = fields
    
    def get_user_details(self, obj):
        """Get limited user details for public view."""
        return {
            'first_name': obj.user.first_name,
            'last_name': obj.user.last_name,
            'full_name': obj.user.get_full_name()
        }