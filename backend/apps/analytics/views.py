# filepath: c:\Users\cadsa\OneDrive\Personal\Full stack web development\wellnessCentre\backend\apps\analytics\views.py
from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Sum, Avg, F, Q, Case, When, Value, DecimalField
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth
from django.utils import timezone
from datetime import timedelta, datetime

from apps.analytics.models import (
    Dashboard, PerformanceMetric, MetricSnapshot, AnalyticsReport,
    ServiceAnalytics, CustomerJourneyStep
)
from apps.analytics.serializers import (
    DashboardSerializer, PerformanceMetricSerializer, MetricSnapshotSerializer,
    AnalyticsReportSerializer, ServiceAnalyticsSerializer, CustomerJourneyStepSerializer,
    CustomerJourneyAnalyticsSerializer
)
from apps.booking.models import Appointment, Payment
from apps.ehr.models import TreatmentSession
from apps.engagement.models import FeedbackResponse, Referral
from apps.core.models import User
from apps.core.permissions import IsAdminUser, IsTherapistUser, IsOwnerOrReadOnly


class DashboardViewSet(viewsets.ModelViewSet):
    """ViewSet for Dashboard model."""
    
    serializer_class = DashboardSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_default']
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']
    
    def get_queryset(self):
        """Get dashboards for the current user."""
        user = self.request.user
        if user.role == 'admin':
            return Dashboard.objects.all()
        return Dashboard.objects.filter(user=user)
    
    def perform_create(self, serializer):
        """Set the user field to the current user."""
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        """Set this dashboard as the default for the user."""
        dashboard = self.get_object()
        
        # Remove default flag from other dashboards for this user
        Dashboard.objects.filter(user=request.user, is_default=True).update(is_default=False)
        
        # Set this dashboard as default
        dashboard.is_default = True
        dashboard.save()
        
        return Response({
            "detail": "Dashboard set as default successfully."
        }, status=status.HTTP_200_OK)


class PerformanceMetricViewSet(viewsets.ModelViewSet):
    """ViewSet for PerformanceMetric model."""
    
    queryset = PerformanceMetric.objects.filter(is_active=True)
    serializer_class = PerformanceMetricSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['metric_type', 'branch', 'frequency', 'is_active']
    search_fields = ['name', 'calculation_method']
    ordering_fields = ['name', 'created_at']
    
    def perform_create(self, serializer):
        """Set the created_by field to the current user."""
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def add_snapshot(self, request, pk=None):
        """Add a snapshot for this metric."""
        metric = self.get_object()
        
        value = request.data.get('value')
        timestamp = request.data.get('timestamp', timezone.now())
        notes = request.data.get('notes', '')
        
        if value is None:
            return Response({
                "detail": "Value is required."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        snapshot = MetricSnapshot.objects.create(
            metric=metric,
            value=value,
            timestamp=timestamp,
            notes=notes
        )
        
        # Update the current value of the metric
        metric.current_value = value
        metric.save()
        
        serializer = MetricSnapshotSerializer(snapshot)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Get metrics for the dashboard."""
        metric_type = request.query_params.get('metric_type')
        branch_id = request.query_params.get('branch')
        
        metrics = self.get_queryset()
        
        if metric_type:
            metrics = metrics.filter(metric_type=metric_type)
        if branch_id:
            metrics = metrics.filter(Q(branch_id=branch_id) | Q(branch__isnull=True))
        
        serializer = self.get_serializer(metrics, many=True)
        return Response(serializer.data)


class AnalyticsReportViewSet(viewsets.ModelViewSet):
    """ViewSet for AnalyticsReport model."""
    
    queryset = AnalyticsReport.objects.all()
    serializer_class = AnalyticsReportSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['report_type', 'branch', 'is_scheduled']
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']
    
    def perform_create(self, serializer):
        """Set the generated_by field to the current user."""
        serializer.save(generated_by=self.request.user)
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """Generate a new analytics report."""
        # Get parameters from request
        report_type = request.data.get('report_type')
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        branch_id = request.data.get('branch')
        name = request.data.get('name')
        
        if not all([report_type, start_date, end_date, name]):
            return Response({
                "detail": "Missing required parameters."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Generate report data based on type
        report_data = {}
        
        if report_type == 'customer_trends':
            # New customers over time
            users = User.objects.filter(
                date_joined__range=(start_date, end_date),
                role__in=['visitor', 'customer']
            )
            if branch_id:
                # Filter by appointments at this branch
                user_ids = Appointment.objects.filter(branch_id=branch_id).values_list('customer_id', flat=True).distinct()
                users = users.filter(id__in=user_ids)
              # Group by day/week/month based on date range
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
            date_diff = (end_date_obj - start_date_obj).days
            if date_diff <= 30:
                # Group by day for ranges <= 30 days
                users_by_date = users.annotate(
                    date=TruncDay('date_joined')
                ).values('date').annotate(count=Count('id')).order_by('date')
                date_format = '%Y-%m-%d'
            elif date_diff <= 90:
                # Group by week for ranges <= 90 days
                users_by_date = users.annotate(
                    date=TruncWeek('date_joined')
                ).values('date').annotate(count=Count('id')).order_by('date')
                date_format = '%Y-%m-%d'
            else:
                # Group by month for ranges > 90 days
                users_by_date = users.annotate(
                    date=TruncMonth('date_joined')
                ).values('date').annotate(count=Count('id')).order_by('date')
                date_format = '%Y-%m'
            
            # Format the results
            user_trend = [
                {
                    'date': item['date'].strftime(date_format),
                    'count': item['count']
                }
                for item in users_by_date
            ]
            
            report_data = {
                'new_customers': user_trend,
                'total_customers': users.count(),
                'customer_roles': list(users.values('role').annotate(count=Count('id')))
            }
        
        # Create the report
        report = AnalyticsReport.objects.create(
            name=name,
            report_type=report_type,
            start_date=start_date,
            end_date=end_date,
            branch_id=branch_id if branch_id else None,
            parameters=request.data,
            report_data=report_data,
            generated_by=request.user
        )
        
        serializer = self.get_serializer(report)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ServiceAnalyticsViewSet(viewsets.ModelViewSet):
    """ViewSet for ServiceAnalytics model."""
    
    queryset = ServiceAnalytics.objects.all()
    serializer_class = ServiceAnalyticsSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['service', 'time_period']
    ordering_fields = ['time_period', 'appointment_count', 'revenue']
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """Generate service analytics for a specific time period."""
        service_id = request.data.get('service_id')
        time_period = request.data.get('time_period')  # Date in YYYY-MM-DD format
        
        if not service_id or not time_period:
            return Response({
                "detail": "Service ID and time period are required."
            }, status=status.HTTP_400_BAD_REQUEST)
          # Calculate start and end of the month for the given time period
        date_obj = datetime.strptime(time_period, '%Y-%m-%d')
        start_of_month = date_obj.replace(day=1).date()
        if date_obj.month == 12:
            end_of_month = date_obj.replace(year=date_obj.year+1, month=1, day=1) - timedelta(days=1)
        else:
            end_of_month = date_obj.replace(month=date_obj.month+1, day=1) - timedelta(days=1)
        end_of_month = end_of_month.date()
        
        # Get appointments for this service in the time period
        appointments = Appointment.objects.filter(
            service_id=service_id,
            start_time__date__range=(start_of_month, end_of_month)
        )
        
        # Calculate metrics
        appointment_count = appointments.count()
        
        # Get unique customers
        customer_count = appointments.values('customer').distinct().count()
        
        # Get payments for these appointments
        payments = Payment.objects.filter(appointment__in=appointments)
        revenue = payments.aggregate(total=Sum('total_amount'))['total'] or 0
        
        # Calculate cancellation rate
        cancelled = appointments.filter(status='cancelled').count()
        cancellation_rate = 0
        if appointment_count > 0:
            cancellation_rate = (cancelled / appointment_count) * 100
            
        # Calculate no-show rate
        no_shows = appointments.filter(status='no_show').count()
        no_show_rate = 0
        if appointment_count > 0:
            no_show_rate = (no_shows / appointment_count) * 100
            
        # Get customer feedback for these appointments
        feedback_responses = FeedbackResponse.objects.filter(
            appointment__in=appointments
        )
        avg_rating = feedback_responses.aggregate(avg=Avg('rating'))['avg']
        
        # Check for existing analytics record
        analytics, created = ServiceAnalytics.objects.update_or_create(
            service_id=service_id,
            time_period=start_of_month,
            defaults={
                'appointment_count': appointment_count,
                'revenue': revenue,
                'customer_count': customer_count,
                'average_rating': avg_rating,
                'cancellation_rate': cancellation_rate,
                'no_show_rate': no_show_rate
            }
        )
        
        serializer = self.get_serializer(analytics)
        return Response(serializer.data)


class CustomerJourneyViewSet(viewsets.ViewSet):
    """ViewSet for customer journey analytics."""
    
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    
    def list(self, request):
        """Get aggregate journey analytics."""
        # Filter parameters
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date', timezone.now().date())
        
        # Base query - get customers
        customers = User.objects.filter(role__in=['customer', 'visitor'])
        
        if start_date:
            customers = customers.filter(date_joined__gte=start_date)
            
        # Get journey steps for these users
        steps = CustomerJourneyStep.objects.filter(user__in=customers)
        
        # Aggregate stats
        total_customers = customers.count()
        
        # Journey progression
        signups = steps.filter(step_type='signup').count()
        first_bookings = steps.filter(step_type='first_booking').count()
        first_appointments = steps.filter(step_type='first_appointment').count()
        repeat_bookings = steps.filter(step_type='repeat_booking').count()
        
        # Conversion rates
        signup_to_booking = 0
        booking_to_appointment = 0
        
        if signups > 0:
            signup_to_booking = (first_bookings / signups) * 100
        
        if first_bookings > 0:
            booking_to_appointment = (first_appointments / first_bookings) * 100
        
        # Top sources
        sources = steps.values('source').annotate(count=Count('id')).order_by('-count')[:5]
        
        return Response({
            'total_customers': total_customers,
            'journey_progression': {
                'signups': signups,
                'first_bookings': first_bookings,
                'first_appointments': first_appointments,
                'repeat_bookings': repeat_bookings,
            },
            'conversion_rates': {
                'signup_to_booking': signup_to_booking,
                'booking_to_appointment': booking_to_appointment,
            },
            'top_sources': sources
        })
    
    @action(detail=False, methods=['get'])
    def user(self, request):
        """Get journey analytics for a specific user."""
        user_id = request.query_params.get('user_id')
        
        if not user_id:
            return Response({
                "detail": "User ID is required."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({
                "detail": "User not found."
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get journey steps for this user
        steps = CustomerJourneyStep.objects.filter(user=user).order_by('timestamp')
        
        # Get key journey dates
        first_visit = steps.filter(step_type='website_visit').first()
        signup = steps.filter(step_type='signup').first()
        first_booking = steps.filter(step_type='first_booking').first()
        first_appointment = steps.filter(step_type='first_appointment').first()
        
        # Calculate time between steps
        days_signup_to_booking = None
        days_booking_to_appointment = None
        
        if signup and first_booking:
            days_signup_to_booking = (first_booking.timestamp - signup.timestamp).days
            
        if first_booking and first_appointment:
            days_booking_to_appointment = (first_appointment.timestamp - first_booking.timestamp).days
            
        # Get appointment counts
        total_bookings = steps.filter(step_type__in=['first_booking', 'repeat_booking']).count()
        total_appointments = steps.filter(step_type__in=['first_appointment']).count() + \
                           Appointment.objects.filter(
                               customer=user, 
                               status__in=['completed', 'confirmed']
                           ).count() - 1  # Subtract 1 to avoid double-counting first appointment
        
        # Other metrics
        total_feedback = steps.filter(step_type='feedback_submission').count()
        total_referrals = steps.filter(step_type='referral').count()
        total_cancellations = steps.filter(step_type='cancellation').count()
        
        # Calculate lifetime value
        lifetime_value = Payment.objects.filter(
            appointment__customer=user,
            status='completed'
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        # Get source breakdown
        sources = {}
        for step in steps:
            if step.source:
                if step.source in sources:
                    sources[step.source] += 1
                else:
                    sources[step.source] = 1
        
        # Create response data
        response_data = {
            'user_id': user.id,
            'user_email': user.email,
            'first_visit_date': first_visit.timestamp if first_visit else None,
            'signup_date': signup.timestamp if signup else None,
            'first_booking_date': first_booking.timestamp if first_booking else None,
            'first_appointment_date': first_appointment.timestamp if first_appointment else None,
            'days_signup_to_booking': days_signup_to_booking,
            'days_booking_to_appointment': days_booking_to_appointment,
            'total_bookings': total_bookings,
            'total_appointments': total_appointments,
            'total_feedback': total_feedback,
            'total_referrals': total_referrals,
            'total_cancellations': total_cancellations,
            'lifetime_value': lifetime_value,
            'sources': sources,
            'journey_steps': CustomerJourneyStepSerializer(steps, many=True).data
        }
        
        serializer = CustomerJourneyAnalyticsSerializer(response_data)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def track(self, request):
        """Record a customer journey step."""
        user_id = request.data.get('user_id')
        step_type = request.data.get('step_type')
        details = request.data.get('details', {})
        source = request.data.get('source')
        
        if not user_id or not step_type:
            return Response({
                "detail": "User ID and step type are required."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({
                "detail": "User not found."
            }, status=status.HTTP_404_NOT_FOUND)
            
        # Create the journey step
        step = CustomerJourneyStep.objects.create(
            user=user,
            step_type=step_type,
            details=details,
            source=source
        )
        
        serializer = CustomerJourneyStepSerializer(step)
        return Response(serializer.data, status=status.HTTP_201_CREATED)