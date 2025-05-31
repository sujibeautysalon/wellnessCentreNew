# filepath: c:\Users\cadsa\OneDrive\Personal\Full stack web development\wellnessCentre\backend\apps\analytics\tests\test_models.py
from django.test import TestCase
from django.utils import timezone
from decimal import Decimal
from datetime import date, timedelta

from apps.analytics.models import (
    Dashboard, PerformanceMetric, MetricSnapshot, AnalyticsReport,
    ServiceAnalytics, CustomerJourneyStep
)
from apps.core.models import User
from apps.clinic.models import Branch, Service


class DashboardTests(TestCase):
    """Test the Dashboard model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com",
            password="password123",
            role="admin"
        )
        
        self.dashboard = Dashboard.objects.create(
            name="Revenue Dashboard",
            user=self.user,
            is_default=True,
            layout={
                "widgets": [
                    {"id": "revenue_chart", "x": 0, "y": 0, "w": 6, "h": 4},
                    {"id": "monthly_bookings", "x": 6, "y": 0, "w": 6, "h": 4}
                ]
            }
        )

    def test_dashboard_creation(self):
        """Test that Dashboard instances are created correctly."""
        self.assertEqual(self.dashboard.name, "Revenue Dashboard")
        self.assertEqual(self.dashboard.user, self.user)
        self.assertEqual(self.dashboard.is_default, True)
        self.assertEqual(len(self.dashboard.layout["widgets"]), 2)
        
    def test_dashboard_string_representation(self):
        """Test the string representation of Dashboard."""
        expected = f"Revenue Dashboard - {self.user.email}"
        self.assertEqual(str(self.dashboard), expected)


class PerformanceMetricTests(TestCase):
    """Test the PerformanceMetric model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com",
            password="password123",
            role="admin"
        )
        
        self.branch = Branch.objects.create(
            name="Main Branch",
            address="123 Main St",
            phone_number="555-123-4567"
        )
        
        self.metric = PerformanceMetric.objects.create(
            name="Monthly Revenue",
            metric_type="revenue",
            branch=self.branch,
            target_value=Decimal('10000.00'),
            current_value=Decimal('8500.00'),
            frequency="monthly",
            start_date=date.today().replace(day=1),
            calculation_method="Sum of all completed payments in the month",
            created_by=self.user
        )

    def test_performance_metric_creation(self):
        """Test that PerformanceMetric instances are created correctly."""
        self.assertEqual(self.metric.name, "Monthly Revenue")
        self.assertEqual(self.metric.metric_type, "revenue")
        self.assertEqual(self.metric.branch, self.branch)
        self.assertEqual(self.metric.target_value, Decimal('10000.00'))
        self.assertEqual(self.metric.current_value, Decimal('8500.00'))
        self.assertEqual(self.metric.frequency, "monthly")
        
    def test_performance_metric_string_representation(self):
        """Test the string representation of PerformanceMetric."""
        expected = f"Monthly Revenue - Main Branch (Revenue)"
        self.assertEqual(str(self.metric), expected)


class MetricSnapshotTests(TestCase):
    """Test the MetricSnapshot model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com",
            password="password123",
            role="admin"
        )
        
        self.branch = Branch.objects.create(
            name="Main Branch",
            address="123 Main St",
            phone_number="555-123-4567"
        )
        
        self.metric = PerformanceMetric.objects.create(
            name="Monthly Revenue",
            metric_type="revenue",
            branch=self.branch,
            target_value=Decimal('10000.00'),
            current_value=Decimal('8500.00'),
            frequency="monthly",
            created_by=self.user
        )
        
        self.snapshot = MetricSnapshot.objects.create(
            metric=self.metric,
            value=Decimal('8500.00'),
            timestamp=timezone.now(),
            notes="End of month snapshot"
        )

    def test_metric_snapshot_creation(self):
        """Test that MetricSnapshot instances are created correctly."""
        self.assertEqual(self.snapshot.metric, self.metric)
        self.assertEqual(self.snapshot.value, Decimal('8500.00'))
        self.assertEqual(self.snapshot.notes, "End of month snapshot")
        
    def test_metric_snapshot_string_representation(self):
        """Test the string representation of MetricSnapshot."""
        expected = f"Monthly Revenue - 8500.00 - {self.snapshot.timestamp}"
        self.assertEqual(str(self.snapshot), expected)


class AnalyticsReportTests(TestCase):
    """Test the AnalyticsReport model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com",
            password="password123",
            role="admin"
        )
        
        self.branch = Branch.objects.create(
            name="Main Branch",
            address="123 Main St",
            phone_number="555-123-4567"
        )
        
        self.report = AnalyticsReport.objects.create(
            name="Q1 Customer Analysis",
            report_type="customer_trends",
            start_date=date(2023, 1, 1),
            end_date=date(2023, 3, 31),
            branch=self.branch,
            parameters={"include_demographics": True},
            report_data={
                "new_customers": 120,
                "returning_customers": 350,
                "customer_retention": 85
            },
            generated_by=self.user
        )

    def test_analytics_report_creation(self):
        """Test that AnalyticsReport instances are created correctly."""
        self.assertEqual(self.report.name, "Q1 Customer Analysis")
        self.assertEqual(self.report.report_type, "customer_trends")
        self.assertEqual(self.report.start_date, date(2023, 1, 1))
        self.assertEqual(self.report.end_date, date(2023, 3, 31))
        self.assertEqual(self.report.branch, self.branch)
        self.assertEqual(self.report.parameters, {"include_demographics": True})
        self.assertEqual(
            self.report.report_data, 
            {"new_customers": 120, "returning_customers": 350, "customer_retention": 85}
        )
        
    def test_analytics_report_string_representation(self):
        """Test the string representation of AnalyticsReport."""
        expected = f"Q1 Customer Analysis - Customer Trends (2023-01-01 to 2023-03-31)"
        self.assertEqual(str(self.report), expected)


class ServiceAnalyticsTests(TestCase):
    """Test the ServiceAnalytics model."""
    
    def setUp(self):
        self.branch = Branch.objects.create(
            name="Main Branch",
            address="123 Main St",
            phone_number="555-123-4567"
        )
        
        self.service = Service.objects.create(
            name="Deep Tissue Massage",
            description="Deep tissue massage therapy",
            duration=60,
            price=Decimal('90.00')
        )
        
        self.analytics = ServiceAnalytics.objects.create(
            service=self.service,
            time_period=date(2023, 5, 1),
            appointment_count=45,
            revenue=Decimal('3825.00'),
            customer_count=38,
            new_customer_count=12,
            average_rating=Decimal('4.7'),
            cancellation_rate=Decimal('5.2'),
            no_show_rate=Decimal('2.1')
        )

    def test_service_analytics_creation(self):
        """Test that ServiceAnalytics instances are created correctly."""
        self.assertEqual(self.analytics.service, self.service)
        self.assertEqual(self.analytics.time_period, date(2023, 5, 1))
        self.assertEqual(self.analytics.appointment_count, 45)
        self.assertEqual(self.analytics.revenue, Decimal('3825.00'))
        self.assertEqual(self.analytics.customer_count, 38)
        self.assertEqual(self.analytics.new_customer_count, 12)
        self.assertEqual(self.analytics.average_rating, Decimal('4.7'))
        self.assertEqual(self.analytics.cancellation_rate, Decimal('5.2'))
        self.assertEqual(self.analytics.no_show_rate, Decimal('2.1'))
        
    def test_service_analytics_string_representation(self):
        """Test the string representation of ServiceAnalytics."""
        expected = f"Deep Tissue Massage - 2023-05-01 - 45 appointments"
        self.assertEqual(str(self.analytics), expected)


class CustomerJourneyStepTests(TestCase):
    """Test the CustomerJourneyStep model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email="customer@example.com",
            password="password123",
            role="customer"
        )
        
        self.step = CustomerJourneyStep.objects.create(
            user=self.user,
            step_type="signup",
            details={"utm_source": "google", "utm_medium": "cpc"},
            source="google_ads"
        )

    def test_customer_journey_step_creation(self):
        """Test that CustomerJourneyStep instances are created correctly."""
        self.assertEqual(self.step.user, self.user)
        self.assertEqual(self.step.step_type, "signup")
        self.assertEqual(self.step.details, {"utm_source": "google", "utm_medium": "cpc"})
        self.assertEqual(self.step.source, "google_ads")
        
    def test_customer_journey_step_string_representation(self):
        """Test the string representation of CustomerJourneyStep."""
        expected = f"customer@example.com - Sign Up - {self.step.timestamp}"
        self.assertEqual(str(self.step), expected)