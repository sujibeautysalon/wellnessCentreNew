from rest_framework import serializers
from .models import MedicalHistory, TreatmentSession, SymptomTracker, WellnessJournal, FileAttachment
from apps.booking.serializers import AppointmentSerializer


class MedicalHistorySerializer(serializers.ModelSerializer):
    """Serializer for MedicalHistory model."""
    
    customer_name = serializers.SerializerMethodField()
    
    class Meta:
        model = MedicalHistory
        fields = ['id', 'customer', 'customer_name', 'allergies', 'medical_conditions', 
                 'medications', 'surgeries', 'family_history', 'lifestyle', 
                 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_customer_name(self, obj):
        return obj.customer.get_full_name() if obj.customer else None


class FileAttachmentSerializer(serializers.ModelSerializer):
    """Serializer for FileAttachment model."""
    
    class Meta:
        model = FileAttachment
        fields = ['id', 'treatment_session', 'file', 'file_type', 'name', 'description', 
                 'uploaded_by', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']


class TreatmentSessionSerializer(serializers.ModelSerializer):
    """Serializer for TreatmentSession model."""
    
    customer_name = serializers.SerializerMethodField()
    therapist_name = serializers.SerializerMethodField()
    service_name = serializers.SerializerMethodField()
    appointment_details = AppointmentSerializer(source='appointment', read_only=True)
    attachments = FileAttachmentSerializer(source='file_attachments', many=True, read_only=True)
    
    class Meta:
        model = TreatmentSession
        fields = ['id', 'appointment', 'customer', 'customer_name', 'therapist', 
                 'therapist_name', 'service', 'service_name', 'status', 'notes', 
                 'clinical_findings', 'treatment_provided', 'medications_prescribed', 
                 'recommendations', 'follow_up', 'attachments', 'created_at', 'updated_at', 
                 'appointment_details']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_customer_name(self, obj):
        return obj.customer.get_full_name() if obj.customer else None
    
    def get_therapist_name(self, obj):
        if obj.therapist and obj.therapist.user:
            return obj.therapist.user.get_full_name()
        return None
    
    def get_service_name(self, obj):
        return obj.service.name if obj.service else None


class SymptomTrackerSerializer(serializers.ModelSerializer):
    """Serializer for SymptomTracker model."""
    
    customer_name = serializers.SerializerMethodField()
    
    class Meta:
        model = SymptomTracker
        fields = ['id', 'customer', 'customer_name', 'symptom_name', 'description', 
                 'type', 'date_recorded', 'value', 'notes', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_customer_name(self, obj):
        return obj.customer.get_full_name() if obj.customer else None
    
    def validate_value(self, value):
        """Validate the value format based on the symptom type."""
        instance = getattr(self, 'instance', None)
        symptom_type = self.initial_data.get('type', instance.type if instance else None)
        
        if symptom_type == 'scale':
            if not isinstance(value, int) or value < 1 or value > 10:
                raise serializers.ValidationError("Scale value must be an integer between 1 and 10.")
        elif symptom_type == 'boolean':
            if not isinstance(value, bool):
                raise serializers.ValidationError("Boolean value must be true or false.")
        
        return value


class WellnessJournalSerializer(serializers.ModelSerializer):
    """Serializer for WellnessJournal model."""
    
    customer_name = serializers.SerializerMethodField()
    
    class Meta:
        model = WellnessJournal
        fields = ['id', 'customer', 'customer_name', 'title', 'content', 'mood', 
                 'energy_level', 'tags', 'date_recorded', 'is_private', 'created_at', 
                 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_customer_name(self, obj):
        return obj.customer.get_full_name() if obj.customer else None
    
    def validate_energy_level(self, value):
        """Validate energy level is between 1 and 10."""
        if value is not None and (value < 1 or value > 10):
            raise serializers.ValidationError("Energy level must be between 1 and 10.")
        return value