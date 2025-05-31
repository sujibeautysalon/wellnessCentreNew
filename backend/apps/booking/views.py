from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from django.utils import timezone
import uuid

from .models import Appointment, Payment, Invoice, WaitlistEntry
from .serializers import (
    AppointmentSerializer, 
    PaymentSerializer,
    InvoiceSerializer, 
    WaitlistEntrySerializer,
    AppointmentBookingSerializer
)
from apps.core.permissions import IsAdminUser, IsTherapist, IsCustomer, IsOwnerOrAdmin


class AppointmentViewSet(viewsets.ModelViewSet):
    """ViewSet for Appointment model."""
    
    serializer_class = AppointmentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'service', 'branch', 'therapist_profile']
    search_fields = ['customer__first_name', 'customer__last_name', 'customer__email', 'notes']
    ordering_fields = ['start_time', 'end_time', 'created_at']
    
    def get_queryset(self):
        queryset = Appointment.objects.all()
        
        # Filter based on user role
        user = self.request.user
        if user.role == 'customer':
            queryset = queryset.filter(customer=user)
        elif user.role == 'therapist':
            try:
                profile = user.therapist_profile
                queryset = queryset.filter(therapist_profile=profile)
            except:
                return Appointment.objects.none()
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(start_time__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(start_time__date__lte=end_date)
            
        return queryset.order_by('-start_time')
    
    def get_permissions(self):
        if self.action == 'create' or self.action == 'book_appointment':
            permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['cancel', 'reschedule']:
            permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
        elif self.action in ['list', 'retrieve', 'update', 'partial_update']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)
    
    @action(detail=False, methods=['post'])
    def book_appointment(self, request):
        """Book a new appointment."""
        serializer = AppointmentBookingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Extract validated data
        service = serializer.validated_data['service']
        branch = serializer.validated_data['branch']
        start_time = serializer.validated_data['start_time']
        end_time = serializer.validated_data['end_time']
        notes = serializer.validated_data.get('notes', '')
        
        # Get therapist if specified, otherwise find an available one
        if 'therapist_profile' in serializer.validated_data:
            therapist_profile = serializer.validated_data['therapist_profile']
        else:
            # Find available therapist logic would go here
            # For now, return an error if no therapist specified
            return Response(
                {"error": "Automatic therapist assignment not implemented, please select a therapist"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create the appointment
        appointment = Appointment.objects.create(
            customer=request.user,
            therapist_profile=therapist_profile,
            service=service,
            branch=branch,
            start_time=start_time,
            end_time=end_time,
            status='pending',
            notes=notes
        )
        
        # Return the created appointment
        return Response(
            AppointmentSerializer(appointment).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel an appointment."""
        appointment = self.get_object()
        
        # Check if appointment is already completed or cancelled
        if appointment.status in ['completed', 'cancelled', 'no_show']:
            return Response(
                {"error": f"Cannot cancel an appointment that is already {appointment.status}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update the status
        appointment.status = 'cancelled'
        appointment.save()
        
        # Return the updated appointment
        return Response(
            AppointmentSerializer(appointment).data,
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    def reschedule(self, request, pk=None):
        """Reschedule an appointment."""
        appointment = self.get_object()
        
        # Check if appointment is already completed, cancelled or no-show
        if appointment.status in ['completed', 'cancelled', 'no_show']:
            return Response(
                {"error": f"Cannot reschedule an appointment that is {appointment.status}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate new time
        serializer = AppointmentBookingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Update appointment fields
        appointment.start_time = serializer.validated_data['start_time']
        appointment.end_time = serializer.validated_data['end_time']
        
        # Update therapist if changed
        if 'therapist_profile' in serializer.validated_data:
            appointment.therapist_profile = serializer.validated_data['therapist_profile']
        
        appointment.status = 'pending'  # Reset to pending for re-confirmation
        appointment.save()
        
        # Return the updated appointment
        return Response(
            AppointmentSerializer(appointment).data,
            status=status.HTTP_200_OK
        )


class PaymentViewSet(viewsets.ModelViewSet):
    """ViewSet for Payment model."""
    
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'payment_method', 'appointment__status']
    ordering_fields = ['payment_date', 'created_at', 'total_amount']
    
    def get_queryset(self):
        queryset = Payment.objects.all()
        
        # Filter based on user role
        user = self.request.user
        if user.role == 'customer':
            queryset = queryset.filter(appointment__customer=user)
        elif user.role == 'therapist':
            try:
                profile = user.therapist_profile
                queryset = queryset.filter(appointment__therapist_profile=profile)
            except:
                return Payment.objects.none()
                
        return queryset.order_by('-created_at')
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['create', 'update', 'partial_update']:
            permission_classes = [permissions.IsAuthenticated & (IsAdminUser | IsCustomer)]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]
    
    @action(detail=False, methods=['post'])
    def process_payment(self, request):
        """Process a payment for an appointment."""
        # This would integrate with Stripe/Razorpay in production
        # For now, just simulate a payment
        
        appointment_id = request.data.get('appointment_id')
        payment_method = request.data.get('payment_method')
        
        if not appointment_id or not payment_method:
            return Response(
                {"error": "appointment_id and payment_method are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            appointment = Appointment.objects.get(id=appointment_id)
            
            # Check if user is authorized to make payment
            if not request.user.is_staff and not request.user.role == 'admin' and appointment.customer != request.user:
                return Response(
                    {"error": "You are not authorized to make payment for this appointment"},
                    status=status.HTTP_403_FORBIDDEN
                )
                
            # Check if appointment is already paid
            if Payment.objects.filter(appointment=appointment, status='completed').exists():
                return Response(
                    {"error": "This appointment is already paid"},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            # Calculate amounts
            amount = appointment.service.price
            tax_rate = 0.18  # 18% tax
            tax_amount = amount * tax_rate
            total_amount = amount + tax_amount
            
            # Create payment
            payment = Payment.objects.create(
                appointment=appointment,
                amount=amount,
                tax_amount=tax_amount,
                total_amount=total_amount,
                status='completed',
                payment_method=payment_method,
                transaction_id=f"TXID-{uuid.uuid4().hex[:8]}",
                payment_date=timezone.now(),
                payment_details={"processor": "mock", "paid_by": request.user.email}
            )
            
            # Update appointment status
            appointment.status = 'confirmed'
            appointment.save()
            
            # Generate invoice
            invoice_number = f"INV-{timezone.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6]}"
            invoice = Invoice.objects.create(
                customer=appointment.customer,
                appointment=appointment,
                invoice_number=invoice_number,
                issue_date=timezone.now().date(),
                items=[{
                    "service": appointment.service.name,
                    "description": appointment.service.description,
                    "quantity": 1,
                    "unit_price": float(amount),
                    "total": float(amount)
                }],
                subtotal=amount,
                tax_rate=tax_rate,
                tax_amount=tax_amount,
                total=total_amount,
                paid_amount=total_amount,
                status='paid',
                terms="Thank you for your business!"
            )
            
            return Response({
                "payment": PaymentSerializer(payment).data,
                "invoice": InvoiceSerializer(invoice).data,
                "message": "Payment processed successfully"
            }, status=status.HTTP_201_CREATED)
            
        except Appointment.DoesNotExist:
            return Response(
                {"error": "Appointment not found"},
                status=status.HTTP_404_NOT_FOUND
            )


class InvoiceViewSet(viewsets.ModelViewSet):
    """ViewSet for Invoice model."""
    
    serializer_class = InvoiceSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'issue_date', 'customer']
    search_fields = ['invoice_number', 'customer__first_name', 'customer__last_name', 'customer__email']
    ordering_fields = ['issue_date', 'due_date', 'total', 'created_at']
    
    def get_queryset(self):
        queryset = Invoice.objects.all()
        
        # Filter based on user role
        user = self.request.user
        if user.role == 'customer':
            queryset = queryset.filter(customer=user)
        elif user.role == 'therapist':
            try:
                profile = user.therapist_profile
                queryset = queryset.filter(appointment__therapist_profile=profile)
            except:
                return Invoice.objects.none()
                
        return queryset.order_by('-issue_date')
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'download']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]
    
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """Download invoice as PDF."""
        invoice = self.get_object()
        
        # In a real app, we would generate a PDF here using WeasyPrint
        # For now, just return the invoice data
        return Response({
            "message": "PDF generation would happen here",
            "invoice": InvoiceSerializer(invoice).data
        })


class WaitlistEntryViewSet(viewsets.ModelViewSet):
    """ViewSet for WaitlistEntry model."""
    
    serializer_class = WaitlistEntrySerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'service', 'branch', 'therapist_profile', 'preferred_date']
    ordering_fields = ['preferred_date', 'position', 'created_at']
    
    def get_queryset(self):
        queryset = WaitlistEntry.objects.all()
        
        # Filter based on user role
        user = self.request.user
        if user.role == 'customer':
            queryset = queryset.filter(customer=user)
        elif user.role == 'therapist':
            try:
                profile = user.therapist_profile
                queryset = queryset.filter(therapist_profile=profile)
            except:
                return WaitlistEntry.objects.none()
                
        return queryset.order_by('position', 'created_at')
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'create']:
            permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['update', 'partial_update', 'cancel']:
            permission_classes = [permissions.IsAuthenticated & (IsAdminUser | IsOwnerOrAdmin)]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        """Override create to set position and customer."""
        
        # Set the customer to the current user
        customer = self.request.user
        
        # Get the position (count of active waitlist entries + 1)
        service = serializer.validated_data.get('service')
        branch = serializer.validated_data.get('branch')
        therapist_profile = serializer.validated_data.get('therapist_profile')
        
        # Build filters for counting position
        filters = Q(service=service, branch=branch, status='active')
        if therapist_profile:
            filters &= Q(therapist_profile=therapist_profile)
            
        position = WaitlistEntry.objects.filter(filters).count() + 1
        
        # Save the entry
        serializer.save(customer=customer, position=position)
        
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a waitlist entry."""
        entry = self.get_object()
        
        # Check if entry is already cancelled or expired
        if entry.status in ['cancelled', 'expired', 'booked']:
            return Response(
                {"error": f"Cannot cancel a waitlist entry that is already {entry.status}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update the status
        entry.status = 'cancelled'
        entry.save()
        
        # Update positions for other entries
        service = entry.service
        branch = entry.branch
        therapist_profile = entry.therapist_profile
        
        # Build filters for updating positions
        filters = Q(service=service, branch=branch, status='active')
        if therapist_profile:
            filters &= Q(therapist_profile=therapist_profile)
            
        # Get entries with higher position and decrement them
        entries_to_update = WaitlistEntry.objects.filter(
            filters, position__gt=entry.position
        )
        
        for e in entries_to_update:
            e.position -= 1
            e.save()
        
        # Return the updated entry
        return Response(
            WaitlistEntrySerializer(entry).data,
            status=status.HTTP_200_OK
        )