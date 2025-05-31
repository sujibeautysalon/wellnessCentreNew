# filepath: c:\Users\cadsa\OneDrive\Personal\Full stack web development\wellnessCentre\backend\apps\analytics\models.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.utils import timezone
from apps.clinic.models import Branch, Service


class Dashboard(models.Model):
    """Model for user-customized dashboards."""
    
    name = models.CharField(_('name'), max_length=100)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                           related_name='dashboards')
    is_default = models.BooleanField(_('is default'), default=False)
    layout = models.JSONField(_('layout'), default=dict)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('dashboard')
        verbose_name_plural = _('dashboards')
        ordering = ['name']
        
    def __str__(self):
        return f"{self.name} - {self.user.email}"


class PerformanceMetric(models.Model):
    """Model for tracking key performance indicators (KPIs)."""
    
    METRIC_TYPES = [
        ('revenue', 'Revenue'),
        ('appointments', 'Appointments'),
        ('customers', 'Customer Count'),
        ('retention', 'Customer Retention'),
        ('satisfaction', 'Customer Satisfaction'),
        ('occupancy', 'Occupancy Rate'),
        ('conversion', 'Conversion Rate'),
        ('custom', 'Custom Metric'),
    ]
    
    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    ]
    
    name = models.CharField(_('name'), max_length=100)
    metric_type = models.CharField(_('metric type'), max_length=20, choices=METRIC_TYPES)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, 
                             related_name='performance_metrics', null=True, blank=True)
    target_value = models.DecimalField(_('target value'), max_digits=12, decimal_places=2, null=True, blank=True)
    current_value = models.DecimalField(_('current value'), max_digits=12, decimal_places=2, null=True, blank=True)
    frequency = models.CharField(_('frequency'), max_length=10, choices=FREQUENCY_CHOICES, default='monthly')
    start_date = models.DateField(_('start date'), default=timezone.now)
    end_date = models.DateField(_('end date'), null=True, blank=True)
    calculation_method = models.TextField(_('calculation method'), blank=True, null=True)
    is_active = models.BooleanField(_('is active'), default=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, 
                                 null=True, related_name='created_metrics')
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('performance metric')
        verbose_name_plural = _('performance metrics')
        ordering = ['name']
        
    def __str__(self):
        branch_name = self.branch.name if self.branch else 'All Branches'
        return f"{self.name} - {branch_name} ({self.get_metric_type_display()})"


class MetricSnapshot(models.Model):
    """Model for storing historical values of performance metrics."""
    
    metric = models.ForeignKey(PerformanceMetric, on_delete=models.CASCADE, related_name='snapshots')
    value = models.DecimalField(_('value'), max_digits=12, decimal_places=2)
    timestamp = models.DateTimeField(_('timestamp'))
    notes = models.TextField(_('notes'), blank=True, null=True)
    
    class Meta:
        verbose_name = _('metric snapshot')
        verbose_name_plural = _('metric snapshots')
        ordering = ['-timestamp']
        
    def __str__(self):
        return f"{self.metric.name} - {self.value} - {self.timestamp}"


class AnalyticsReport(models.Model):
    """Model for storing generated analytics reports."""
    
    REPORT_TYPES = [
        ('customer_trends', 'Customer Trends'),
        ('service_popularity', 'Service Popularity'),
        ('revenue_analysis', 'Revenue Analysis'),
        ('customer_retention', 'Customer Retention'),
        ('therapist_performance', 'Therapist Performance'),
        ('marketing_effectiveness', 'Marketing Effectiveness'),
        ('inventory_usage', 'Inventory Usage'),
        ('customer_feedback', 'Customer Feedback'),
        ('custom', 'Custom Report'),
    ]
    
    name = models.CharField(_('name'), max_length=255)
    report_type = models.CharField(_('report type'), max_length=50, choices=REPORT_TYPES)
    start_date = models.DateField(_('start date'))
    end_date = models.DateField(_('end date'))
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, 
                             related_name='analytics_reports', null=True, blank=True)
    parameters = models.JSONField(_('parameters'), blank=True, null=True)
    report_data = models.JSONField(_('report data'), blank=True, null=True)
    file = models.FileField(_('file'), upload_to='analytics_reports/', blank=True, null=True)
    is_scheduled = models.BooleanField(_('is scheduled'), default=False)
    schedule_frequency = models.CharField(_('schedule frequency'), max_length=20, 
                                        choices=PerformanceMetric.FREQUENCY_CHOICES,
                                        null=True, blank=True)
    last_run = models.DateTimeField(_('last run'), null=True, blank=True)
    next_run = models.DateTimeField(_('next run'), null=True, blank=True)
    recipients = models.JSONField(_('recipients'), default=list, blank=True, null=True)
    generated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                   related_name='generated_analytics')
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('analytics report')
        verbose_name_plural = _('analytics reports')
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.name} - {self.get_report_type_display()} ({self.start_date} to {self.end_date})"


class ServiceAnalytics(models.Model):
    """Model for tracking service-specific analytics."""
    
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='analytics')
    time_period = models.DateField(_('time period'), help_text=_('Starting date of the time period'))
    appointment_count = models.IntegerField(_('appointment count'), default=0)
    revenue = models.DecimalField(_('revenue'), max_digits=12, decimal_places=2, default=0)
    customer_count = models.IntegerField(_('customer count'), default=0)
    new_customer_count = models.IntegerField(_('new customer count'), default=0)
    average_rating = models.DecimalField(_('average rating'), max_digits=3, decimal_places=2, 
                                      null=True, blank=True)
    cancellation_rate = models.DecimalField(_('cancellation rate'), max_digits=5, decimal_places=2, 
                                         default=0, help_text=_('Percentage of cancellations'))
    no_show_rate = models.DecimalField(_('no-show rate'), max_digits=5, decimal_places=2, 
                                    default=0)
    
    class Meta:
        verbose_name = _('service analytics')
        verbose_name_plural = _('service analytics')
        ordering = ['-time_period']
        unique_together = ('service', 'time_period')
        
    def __str__(self):
        return f"{self.service.name} - {self.time_period} - {self.appointment_count} appointments"


class CustomerJourneyStep(models.Model):
    """Model for tracking customer journey analytics."""
    
    STEP_TYPES = [
        ('website_visit', 'Website Visit'),
        ('signup', 'Sign Up'),
        ('first_booking', 'First Booking'),
        ('first_appointment', 'First Appointment'),
        ('repeat_booking', 'Repeat Booking'),
        ('feedback_submission', 'Feedback Submission'),
        ('referral', 'Referral'),
        ('cancellation', 'Cancellation'),
        ('custom', 'Custom Step'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, 
                           related_name='journey_steps')
    step_type = models.CharField(_('step type'), max_length=30, choices=STEP_TYPES)
    timestamp = models.DateTimeField(_('timestamp'), default=timezone.now)
    details = models.JSONField(_('details'), blank=True, null=True)
    source = models.CharField(_('source'), max_length=100, blank=True, null=True, 
                            help_text=_('Marketing source or channel'))
    
    class Meta:
        verbose_name = _('customer journey step')
        verbose_name_plural = _('customer journey steps')
        ordering = ['-timestamp']
        
    def __str__(self):
        return f"{self.user.email} - {self.get_step_type_display()} - {self.timestamp}"