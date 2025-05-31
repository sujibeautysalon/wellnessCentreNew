from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import Q

from .models import MedicalHistory, TreatmentSession, SymptomTracker, WellnessJournal, FileAttachment
from .serializers import (
    MedicalHistorySerializer,
    TreatmentSessionSerializer,
    SymptomTrackerSerializer,
    WellnessJournalSerializer,
    FileAttachmentSerializer
)
from apps.core.permissions import IsAdminUser, IsTherapist, IsOwnerOrAdmin
from apps.booking.models import Appointment


class MedicalHistoryViewSet(viewsets.ModelViewSet):
    """ViewSet for MedicalHistory model."""
    
    serializer_class = MedicalHistorySerializer
    
    def get_queryset(self):
        queryset = MedicalHistory.objects.all()
        
        # Filter based on user role
        user = self.request.user
        if user.role == 'customer':
            queryset = queryset.filter(customer=user)
        elif user.role == 'therapist':
            # Therapists can see medical histories of their patients
            # Get all appointments for this therapist
            try:
                profile = user.therapist_profile
                patient_ids = Appointment.objects.filter(
                    therapist_profile=profile
                ).values_list('customer_id', flat=True).distinct()
                queryset = queryset.filter(customer_id__in=patient_ids)
            except:
                return MedicalHistory.objects.none()
            
        return queryset
    
    def get_permissions(self):
        if self.action in ['retrieve', 'update', 'partial_update']:
            permission_classes = [permissions.IsAuthenticated & (IsOwnerOrAdmin | IsTherapist)]
        elif self.action == 'create':
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        """Set the customer to the current user if not specified."""
        customer = serializer.validated_data.get('customer', self.request.user)
        serializer.save(customer=customer)


class TreatmentSessionViewSet(viewsets.ModelViewSet):
    """ViewSet for TreatmentSession model."""
    
    serializer_class = TreatmentSessionSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'service', 'therapist']
    ordering_fields = ['created_at', 'updated_at']
    
    def get_queryset(self):
        queryset = TreatmentSession.objects.all()
        
        # Filter based on user role
        user = self.request.user
        if user.role == 'customer':
            queryset = queryset.filter(customer=user)
        elif user.role == 'therapist':
            try:
                profile = user.therapist_profile
                queryset = queryset.filter(therapist=profile)
            except:
                return TreatmentSession.objects.none()
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(created_at__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__date__lte=end_date)
            
        return queryset.order_by('-created_at')
    
    def get_permissions(self):
        if self.action in ['retrieve']:
            permission_classes = [permissions.IsAuthenticated & (IsOwnerOrAdmin | IsTherapist)]
        elif self.action in ['create', 'update', 'partial_update']:
            permission_classes = [permissions.IsAuthenticated & (IsAdminUser | IsTherapist)]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]
    
    @action(detail=True, methods=['post'])
    def add_attachment(self, request, pk=None):
        """Add an attachment to a treatment session."""
        treatment_session = self.get_object()
        
        # Check permissions - only therapists or admins can add attachments
        if not (request.user.is_staff or request.user.role in ['admin', 'therapist']):
            return Response({
                'error': 'You do not have permission to add attachments.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Validate file upload
        serializer = FileAttachmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(
                treatment_session=treatment_session,
                uploaded_by=request.user
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def pdf_summary(self, request, pk=None):
        """Generate a PDF summary of the treatment session."""
        treatment_session = self.get_object()
        
        # In a real implementation, we would generate a PDF here
        # For now, just return the session data
        return Response({
            'message': 'PDF generation would happen here',
            'session': TreatmentSessionSerializer(treatment_session).data
        })


class SymptomTrackerViewSet(viewsets.ModelViewSet):
    """ViewSet for SymptomTracker model."""
    
    serializer_class = SymptomTrackerSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['type', 'symptom_name', 'date_recorded']
    search_fields = ['symptom_name', 'description', 'notes']
    ordering_fields = ['date_recorded', 'created_at']
    
    def get_queryset(self):
        queryset = SymptomTracker.objects.all()
        
        # Filter based on user role
        user = self.request.user
        if user.role == 'customer':
            queryset = queryset.filter(customer=user)
        elif user.role == 'therapist':
            # Therapists can see symptoms of their patients
            try:
                profile = user.therapist_profile
                patient_ids = Appointment.objects.filter(
                    therapist_profile=profile
                ).values_list('customer_id', flat=True).distinct()
                queryset = queryset.filter(customer_id__in=patient_ids)
            except:
                return SymptomTracker.objects.none()
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(date_recorded__gte=start_date)
        if end_date:
            queryset = queryset.filter(date_recorded__lte=end_date)
            
        return queryset.order_by('-date_recorded')
    
    def get_permissions(self):
        if self.action in ['retrieve']:
            permission_classes = [permissions.IsAuthenticated & (IsOwnerOrAdmin | IsTherapist)]
        elif self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated & (IsOwnerOrAdmin)]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        """Set the customer to the current user."""
        serializer.save(customer=self.request.user)
    
    @action(detail=False, methods=['get'])
    def chart_data(self, request):
        """Get symptom data for charting."""
        user = request.user
        symptom_name = request.query_params.get('symptom_name')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        # Build the filter
        filters = Q(customer=user)
        if symptom_name:
            filters &= Q(symptom_name=symptom_name)
        if start_date:
            filters &= Q(date_recorded__gte=start_date)
        if end_date:
            filters &= Q(date_recorded__lte=end_date)
        
        # Get the data
        symptoms = SymptomTracker.objects.filter(filters).order_by('date_recorded')
        serializer = SymptomTrackerSerializer(symptoms, many=True)
        
        # Format for chart
        chart_data = {}
        for entry in serializer.data:
            symptom = entry['symptom_name']
            if symptom not in chart_data:
                chart_data[symptom] = []
            
            chart_data[symptom].append({
                'date': entry['date_recorded'],
                'value': entry['value'],
                'notes': entry['notes']
            })
        
        return Response(chart_data)


class WellnessJournalViewSet(viewsets.ModelViewSet):
    """ViewSet for WellnessJournal model."""
    
    serializer_class = WellnessJournalSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['mood', 'date_recorded', 'is_private', 'tags']
    search_fields = ['title', 'content', 'mood', 'tags']
    ordering_fields = ['date_recorded', 'created_at', 'energy_level']
    
    def get_queryset(self):
        queryset = WellnessJournal.objects.all()
        
        # Filter based on user role
        user = self.request.user
        if user.role == 'customer':
            queryset = queryset.filter(customer=user)
        elif user.role == 'therapist':
            # Therapists can see non-private wellness journals of their patients
            try:
                profile = user.therapist_profile
                patient_ids = Appointment.objects.filter(
                    therapist_profile=profile
                ).values_list('customer_id', flat=True).distinct()
                queryset = queryset.filter(customer_id__in=patient_ids, is_private=False)
            except:
                return WellnessJournal.objects.none()
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(date_recorded__gte=start_date)
        if end_date:
            queryset = queryset.filter(date_recorded__lte=end_date)
        
        # Filter by tag
        tags = self.request.query_params.getlist('tag')
        if tags:
            for tag in tags:
                queryset = queryset.filter(tags__contains=[tag])
            
        return queryset.order_by('-date_recorded')
    
    def get_permissions(self):
        if self.action in ['retrieve']:
            permission_classes = [permissions.IsAuthenticated & (IsOwnerOrAdmin | IsTherapist)]
        elif self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated & IsOwnerOrAdmin]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        """Set the customer to the current user."""
        serializer.save(
            customer=self.request.user,
            date_recorded=serializer.validated_data.get('date_recorded', timezone.now().date())
        )


class FileAttachmentViewSet(viewsets.ModelViewSet):
    """ViewSet for FileAttachment model."""
    
    serializer_class = FileAttachmentSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['file_type', 'treatment_session']
    ordering_fields = ['uploaded_at', 'name']
    
    def get_queryset(self):
        queryset = FileAttachment.objects.all()
        
        # Filter based on user role
        user = self.request.user
        if user.role == 'customer':
            queryset = queryset.filter(treatment_session__customer=user)
        elif user.role == 'therapist':
            try:
                profile = user.therapist_profile
                queryset = queryset.filter(treatment_session__therapist=profile)
            except:
                return FileAttachment.objects.none()
            
        return queryset.order_by('-uploaded_at')
    
    def get_permissions(self):
        if self.action in ['retrieve', 'list']:
            permission_classes = [permissions.IsAuthenticated & (IsOwnerOrAdmin | IsTherapist)]
        elif self.action in ['create']:
            permission_classes = [permissions.IsAuthenticated & (IsAdminUser | IsTherapist)]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        """Set the uploaded_by field to current user."""
        serializer.save(uploaded_by=self.request.user)