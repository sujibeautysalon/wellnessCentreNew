from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

from .models import Branch, Service, TherapistProfile, TherapistAvailability, Holiday
from .serializers import (
    BranchSerializer,
    ServiceSerializer,
    TherapistProfileSerializer,
    TherapistAvailabilitySerializer,
    HolidaySerializer,
    TherapistPublicSerializer
)
from apps.core.permissions import IsAdminUser, IsTherapist, ReadOnly


class BranchViewSet(viewsets.ModelViewSet):
    """ViewSet for Branch model."""
    
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['city', 'state', 'country', 'is_active']
    search_fields = ['name', 'city', 'state', 'address']
    ordering_fields = ['name', 'created_at']
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]


class ServiceViewSet(viewsets.ModelViewSet):
    """ViewSet for Service model."""
    
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_active', 'available_branches']
    search_fields = ['name', 'description', 'category']
    ordering_fields = ['name', 'price', 'duration', 'created_at']
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by branch if branch_id is provided
        branch_id = self.request.query_params.get('branch_id')
        if branch_id:
            queryset = queryset.filter(available_branches__id=branch_id)
        
        # Filter by therapist if therapist_id is provided
        therapist_id = self.request.query_params.get('therapist_id')
        if therapist_id:
            queryset = queryset.filter(therapists__id=therapist_id)
            
        return queryset
    
    @action(detail=True, methods=['get'])
    def therapists(self, request, pk=None):
        """Get all therapists offering this service."""
        service = self.get_object()
        therapists = service.therapists.filter(is_active=True)
        serializer = TherapistPublicSerializer(therapists, many=True)
        return Response(serializer.data)


class TherapistProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for TherapistProfile model."""
    
    queryset = TherapistProfile.objects.all()
    serializer_class = TherapistProfileSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['branches', 'services', 'is_active', 'years_of_experience']
    search_fields = ['user__first_name', 'user__last_name', 'title', 'bio', 'specializations']
    ordering_fields = ['average_rating', 'years_of_experience', 'user__first_name']
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'public_list', 'public_detail']:
            permission_classes = [permissions.AllowAny]
        elif self.action in ['update', 'partial_update', 'availability']:
            permission_classes = [permissions.IsAuthenticated & (IsAdminUser | IsTherapist)]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # For public endpoints, only show active therapists
        if self.action in ['public_list', 'public_detail']:
            queryset = queryset.filter(is_active=True)
        
        # Filter by branch if branch_id is provided
        branch_id = self.request.query_params.get('branch_id')
        if branch_id:
            queryset = queryset.filter(branches__id=branch_id)
        
        # Filter by service if service_id is provided
        service_id = self.request.query_params.get('service_id')
        if service_id:
            queryset = queryset.filter(services__id=service_id)
        
        # Filter by specialization
        specialization = self.request.query_params.get('specialization')
        if specialization:
            # Using JSONField query to find specialization
            queryset = queryset.filter(specializations__contains=[specialization])
            
        return queryset
    
    def get_serializer_class(self):
        if self.action in ['public_list', 'public_detail']:
            return TherapistPublicSerializer
        return TherapistProfileSerializer
    
    @action(detail=False, methods=['get'])
    def public_list(self, request):
        """Get public list of therapists."""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def public_detail(self, request, pk=None):
        """Get public details of a therapist."""
        therapist = self.get_object()
        serializer = self.get_serializer(therapist)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def availability(self, request, pk=None):
        """Get availability for a therapist."""
        therapist = self.get_object()
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        # Build the filter
        filters = Q(therapist=therapist)
        if start_date:
            filters &= Q(start_time__date__gte=start_date)
        if end_date:
            filters &= Q(start_time__date__lte=end_date)
            
        availability = TherapistAvailability.objects.filter(filters)
        serializer = TherapistAvailabilitySerializer(availability, many=True)
        return Response(serializer.data)


class TherapistAvailabilityViewSet(viewsets.ModelViewSet):
    """ViewSet for TherapistAvailability model."""
    
    queryset = TherapistAvailability.objects.all()
    serializer_class = TherapistAvailabilitySerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['therapist', 'branch', 'service', 'is_available', 'recurrence']
    ordering_fields = ['start_time', 'end_time']
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAuthenticated & (IsAdminUser | IsTherapist)]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # If user is a therapist, only show their availability
        user = self.request.user
        if user.is_authenticated and user.role == 'therapist':
            try:
                therapist = TherapistProfile.objects.get(user=user)
                queryset = queryset.filter(therapist=therapist)
            except TherapistProfile.DoesNotExist:
                return TherapistAvailability.objects.none()
                
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(start_time__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(start_time__date__lte=end_date)
            
        return queryset.order_by('start_time')


class HolidayViewSet(viewsets.ModelViewSet):
    """ViewSet for Holiday model."""
    
    queryset = Holiday.objects.all()
    serializer_class = HolidaySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['branch', 'start_date', 'end_date']
    search_fields = ['name', 'description']
    ordering_fields = ['start_date', 'end_date', 'name']
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]