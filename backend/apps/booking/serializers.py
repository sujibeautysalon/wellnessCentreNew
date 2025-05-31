from rest_framework import serializers
from django.utils import timezone
from .models import Appointment, Payment, Invoice, WaitlistEntry
from apps.clinic.serializers import TherapistProfileSerializer, ServiceSerializer, BranchSerializer
from apps.clinic.models import TherapistProfile, Service, Branch, TherapistAvailability


class AppointmentSerializer(serializers.ModelSerializer):
    """Serializer for Appointment model."""
    
    customer_name = serializers.SerializerMethodField()
    therapist_name = serializers.SerializerMethodField()
    service_name = serializers.SerializerMethodField()
    branch_name = serializers.SerializerMethodField()
    service_details = ServiceSerializer(source='service', read_only=True)
    therapist_details = TherapistProfileSerializer(source='therapist_profile', read_only=True)
    branch_details = BranchSerializer(source='branch', read_only=True)
    
    class Meta:
        model = Appointment
        fields = ['id', 'customer', 'customer_name', 'therapist_profile', 'therapist_name',
                 'service', 'service_name', 'branch', 'branch_name', 'start_time',
                 'end_time', 'status', 'notes', 'customer_notes', 'created_at', 'updated_at',
                 'service_details', 'therapist_details', 'branch_details']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_customer_name(self, obj):
        return obj.customer.get_full_name() if obj.customer else None
        
    def get_therapist_name(self, obj):
        if obj.therapist_profile and obj.therapist_profile.user:
            return obj.therapist_profile.user.get_full_name()
        return None
        
    def get_service_name(self, obj):
        return obj.service.name if obj.service else None
        
    def get_branch_name(self, obj):
        return obj.branch.name if obj.branch else None
        
    def validate(self, data):
        """
        Validate the appointment timing, availability, etc.
        """
        # Get relevant data
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        therapist_profile = data.get('therapist_profile')
        branch = data.get('branch')
        service = data.get('service')
        
        # Ensure start time is in the future
        if start_time and start_time <= timezone.now():
            raise serializers.ValidationError("Appointment start time must be in the future.")
            
        # Ensure end time is after start time
        if start_time and end_time and end_time <= start_time:
            raise serializers.ValidationError("Appointment end time must be after start time.")
            
        # Ensure therapist is available at selected branch
        if therapist_profile and branch and not therapist_profile.branches.filter(id=branch.id).exists():
            raise serializers.ValidationError("Selected therapist does not work at this branch.")
            
        # Ensure therapist offers the selected service
        if therapist_profile and service and not therapist_profile.services.filter(id=service.id).exists():
            raise serializers.ValidationError("Selected therapist does not offer this service.")
            
        # Check for therapist availability
        if therapist_profile and start_time and end_time:
            # Check if there's a conflicting appointment
            existing_appointments = Appointment.objects.filter(
                therapist_profile=therapist_profile,
                status__in=['pending', 'confirmed'],
                start_time__lt=end_time,
                end_time__gt=start_time
            )
            
            # Exclude current appointment if updating
            if self.instance:
                existing_appointments = existing_appointments.exclude(id=self.instance.id)
                
            if existing_appointments.exists():
                raise serializers.ValidationError("Selected time slot is not available for this therapist.")
                
            # Check if therapist has availability for this time slot
            availability = TherapistAvailability.objects.filter(
                therapist=therapist_profile,
                start_time__lte=start_time,
                end_time__gte=end_time,
                is_available=True
            )
            
            if not availability.exists():
                raise serializers.ValidationError("Therapist is not available during this time slot.")
                
        return data


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for Payment model."""
    
    appointment_details = AppointmentSerializer(source='appointment', read_only=True)
    
    class Meta:
        model = Payment
        fields = ['id', 'appointment', 'amount', 'tax_amount', 'discount_amount', 
                 'total_amount', 'status', 'payment_method', 'transaction_id',
                 'payment_date', 'payment_details', 'created_at', 'updated_at',
                 'appointment_details']
        read_only_fields = ['id', 'created_at', 'updated_at']


class InvoiceSerializer(serializers.ModelSerializer):
    """Serializer for Invoice model."""
    
    customer_name = serializers.SerializerMethodField()
    appointment_details = AppointmentSerializer(source='appointment', read_only=True)
    
    class Meta:
        model = Invoice
        fields = ['id', 'customer', 'customer_name', 'appointment', 'appointment_details',
                 'invoice_number', 'issue_date', 'due_date', 'items', 'subtotal',
                 'tax_rate', 'tax_amount', 'discount', 'total', 'paid_amount',
                 'status', 'notes', 'terms', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
        
    def get_customer_name(self, obj):
        return obj.customer.get_full_name() if obj.customer else None


class WaitlistEntrySerializer(serializers.ModelSerializer):
    """Serializer for WaitlistEntry model."""
    
    customer_name = serializers.SerializerMethodField()
    service_name = serializers.SerializerMethodField()
    therapist_name = serializers.SerializerMethodField()
    branch_name = serializers.SerializerMethodField()
    
    class Meta:
        model = WaitlistEntry
        fields = ['id', 'customer', 'customer_name', 'service', 'service_name',
                 'therapist_profile', 'therapist_name', 'branch', 'branch_name',
                 'preferred_date', 'preferred_time_slots', 'status', 'notes',
                 'position', 'created_at', 'updated_at']
        read_only_fields = ['id', 'position', 'created_at', 'updated_at']
        
    def get_customer_name(self, obj):
        return obj.customer.get_full_name() if obj.customer else None
        
    def get_service_name(self, obj):
        return obj.service.name if obj.service else None
        
    def get_therapist_name(self, obj):
        if obj.therapist_profile and obj.therapist_profile.user:
            return obj.therapist_profile.user.get_full_name()
        return None
        
    def get_branch_name(self, obj):
        return obj.branch.name if obj.branch else None


class AppointmentBookingSerializer(serializers.Serializer):
    """Serializer for booking an appointment."""
    
    service_id = serializers.IntegerField()
    therapist_id = serializers.IntegerField(required=False)
    branch_id = serializers.IntegerField()
    start_time = serializers.DateTimeField()
    notes = serializers.CharField(required=False, allow_blank=True)
    
    def validate(self, data):
        """
        Validate the booking request.
        """
        # Get relevant data
        service_id = data.get('service_id')
        therapist_id = data.get('therapist_id')
        branch_id = data.get('branch_id')
        start_time = data.get('start_time')
        
        try:
            # Fetch related objects
            service = Service.objects.get(id=service_id, is_active=True)
            branch = Branch.objects.get(id=branch_id, is_active=True)
            
            # Validate branch offers service
            if not service.available_branches.filter(id=branch_id).exists():
                raise serializers.ValidationError("Selected service is not available at this branch.")
                
            # Set end time based on service duration
            end_time = start_time + timezone.timedelta(minutes=service.duration)
            
            # If therapist is specified, validate availability
            if therapist_id:
                try:
                    therapist = TherapistProfile.objects.get(id=therapist_id, is_active=True)
                    
                    # Check if therapist works at this branch
                    if not therapist.branches.filter(id=branch_id).exists():
                        raise serializers.ValidationError("Selected therapist does not work at this branch.")
                        
                    # Check if therapist offers this service
                    if not therapist.services.filter(id=service_id).exists():
                        raise serializers.ValidationError("Selected therapist does not offer this service.")
                        
                    # Check for conflicts
                    conflicts = Appointment.objects.filter(
                        therapist_profile=therapist,
                        status__in=['pending', 'confirmed'],
                        start_time__lt=end_time,
                        end_time__gt=start_time
                    ).exists()
                    
                    if conflicts:
                        raise serializers.ValidationError("Selected therapist is not available at this time.")
                        
                    # Check if therapist has availability
                    has_availability = TherapistAvailability.objects.filter(
                        therapist=therapist,
                        start_time__lte=start_time,
                        end_time__gte=end_time,
                        is_available=True
                    ).exists()
                    
                    if not has_availability:
                        raise serializers.ValidationError("Therapist is not available during this time.")
                        
                except TherapistProfile.DoesNotExist:
                    raise serializers.ValidationError("Selected therapist does not exist or is inactive.")
            
            # Store validated objects in data
            data['service'] = service
            data['branch'] = branch
            data['end_time'] = end_time
            if therapist_id:
                data['therapist_profile'] = therapist
                
        except Service.DoesNotExist:
            raise serializers.ValidationError("Selected service does not exist or is inactive.")
        except Branch.DoesNotExist:
            raise serializers.ValidationError("Selected branch does not exist or is inactive.")
            
        return data