from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
import json
import uuid

from apps.engagement.models import (
    Campaign, CampaignRecipient, Notification, FeedbackForm, 
    FeedbackResponse, Loyalty, LoyaltyTransaction, Referral
)

User = get_user_model()


class CampaignModelTest(TestCase):
    """Test case for Campaign model."""
    
    def setUp(self):
        self.admin_user = User.objects.create_user(
            email='admin@example.com',
            password='testpassword',
            role='admin',
            is_staff=True
        )
        self.campaign = Campaign.objects.create(
            name='Test Campaign',
            description='Test campaign description',
            campaign_type='email',
            status='draft',
            subject='Test Subject',
            content='This is a test email content',
            created_by=self.admin_user
        )
    
    def test_campaign_creation(self):
        """Test campaign model creation."""
        self.assertEqual(self.campaign.name, 'Test Campaign')
        self.assertEqual(self.campaign.campaign_type, 'email')
        self.assertEqual(self.campaign.status, 'draft')
        self.assertEqual(self.campaign.created_by, self.admin_user)
    
    def test_campaign_str_method(self):
        """Test campaign string representation."""
        self.assertEqual(str(self.campaign), 'Test Campaign')


class NotificationModelTest(TestCase):
    """Test case for Notification model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='user@example.com',
            password='testpassword',
            role='customer'
        )
        self.notification = Notification.objects.create(
            user=self.user,
            title='Test Notification',
            message='This is a test notification message',
            notification_type='system',
            channel='in_app',
            status='pending'
        )
    
    def test_notification_creation(self):
        """Test notification model creation."""
        self.assertEqual(self.notification.title, 'Test Notification')
        self.assertEqual(self.notification.notification_type, 'system')
        self.assertEqual(self.notification.channel, 'in_app')
        self.assertEqual(self.notification.status, 'pending')
        self.assertEqual(self.notification.user, self.user)
    
    def test_notification_str_method(self):
        """Test notification string representation."""
        self.assertEqual(str(self.notification), 'Test Notification - user@example.com')


class LoyaltyModelTest(TestCase):
    """Test case for Loyalty model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='user@example.com',
            password='testpassword',
            role='customer'
        )
        self.loyalty = Loyalty.objects.create(
            user=self.user,
            points_balance=100,
            lifetime_points=100,
            tier='standard'
        )
    
    def test_loyalty_creation(self):
        """Test loyalty model creation."""
        self.assertEqual(self.loyalty.points_balance, 100)
        self.assertEqual(self.loyalty.lifetime_points, 100)
        self.assertEqual(self.loyalty.tier, 'standard')
        self.assertEqual(self.loyalty.user, self.user)
    
    def test_loyalty_str_method(self):
        """Test loyalty string representation."""
        self.assertEqual(str(self.loyalty), 'user@example.com - 100 points')


class ReferralModelTest(TestCase):
    """Test case for Referral model."""
    
    def setUp(self):
        self.referrer = User.objects.create_user(
            email='referrer@example.com',
            password='testpassword',
            role='customer'
        )
        self.referral = Referral.objects.create(
            referrer=self.referrer,
            email='friend@example.com',
            name='Test Friend',
            status='pending',
            referral_code='REF-12345678'
        )
    
    def test_referral_creation(self):
        """Test referral model creation."""
        self.assertEqual(self.referral.email, 'friend@example.com')
        self.assertEqual(self.referral.name, 'Test Friend')
        self.assertEqual(self.referral.status, 'pending')
        self.assertEqual(self.referral.referrer, self.referrer)
    
    def test_referral_str_method(self):
        """Test referral string representation."""
        self.assertEqual(str(self.referral), 'Referral from referrer@example.com to friend@example.com')


class CampaignViewSetTest(APITestCase):
    """Test the Campaign API views."""
    
    def setUp(self):
        # Create users with different roles
        self.admin_user = User.objects.create_user(
            email='admin@example.com',
            password='testpassword',
            role='admin',
            is_staff=True
        )
        self.therapist_user = User.objects.create_user(
            email='therapist@example.com',
            password='testpassword',
            role='therapist'
        )
        self.customer_user = User.objects.create_user(
            email='customer@example.com',
            password='testpassword',
            role='customer'
        )
        
        # Create a test campaign
        self.campaign = Campaign.objects.create(
            name='Test Campaign',
            description='Test campaign description',
            campaign_type='email',
            status='draft',
            subject='Test Subject',
            content='This is a test email content',
            created_by=self.admin_user
        )
        
        # Add recipients
        self.recipient = CampaignRecipient.objects.create(
            campaign=self.campaign,
            user=self.customer_user,
            status='pending'
        )
        
        # Set up API client
        self.client = APIClient()
        self.campaign_list_url = reverse('campaign-list')
        self.campaign_detail_url = reverse('campaign-detail', kwargs={'pk': self.campaign.pk})
    
    def test_campaign_list_admin(self):
        """Test that admin users can list campaigns."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.campaign_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_campaign_list_therapist(self):
        """Test that therapist users can list campaigns."""
        self.client.force_authenticate(user=self.therapist_user)
        response = self.client.get(self.campaign_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_campaign_list_customer(self):
        """Test that customer users cannot list campaigns."""
        self.client.force_authenticate(user=self.customer_user)
        response = self.client.get(self.campaign_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_campaign_create_admin(self):
        """Test that admin users can create campaigns."""
        self.client.force_authenticate(user=self.admin_user)
        campaign_data = {
            'name': 'New Campaign',
            'description': 'New campaign description',
            'campaign_type': 'email',
            'status': 'draft',
            'subject': 'New Subject',
            'content': 'This is new content'
        }
        response = self.client.post(self.campaign_list_url, campaign_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'New Campaign')
    
    def test_campaign_create_customer(self):
        """Test that customer users cannot create campaigns."""
        self.client.force_authenticate(user=self.customer_user)
        campaign_data = {
            'name': 'New Campaign',
            'description': 'New campaign description',
            'campaign_type': 'email',
            'status': 'draft',
            'subject': 'New Subject',
            'content': 'This is new content'
        }
        response = self.client.post(self.campaign_list_url, campaign_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_send_campaign(self):
        """Test the send campaign action."""
        self.client.force_authenticate(user=self.admin_user)
        send_url = reverse('campaign-send', kwargs={'pk': self.campaign.pk})
        response = self.client.post(send_url)
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        
        # Check that campaign status was updated
        self.campaign.refresh_from_db()
        self.assertEqual(self.campaign.status, 'active')
        self.assertIsNotNone(self.campaign.sent_at)


class NotificationViewSetTest(APITestCase):
    """Test the Notification API views."""
    
    def setUp(self):
        # Create users
        self.admin_user = User.objects.create_user(
            email='admin@example.com',
            password='testpassword',
            role='admin',
            is_staff=True
        )
        self.customer_user = User.objects.create_user(
            email='customer@example.com',
            password='testpassword',
            role='customer'
        )
        
        # Create notifications
        self.admin_notification = Notification.objects.create(
            user=self.admin_user,
            title='Admin Notification',
            message='Admin notification message',
            notification_type='system',
            channel='in_app',
            status='sent'
        )
        
        self.customer_notification = Notification.objects.create(
            user=self.customer_user,
            title='Customer Notification',
            message='Customer notification message',
            notification_type='appointment',
            channel='email',
            status='sent'
        )
        
        # Set up API client
        self.client = APIClient()
        self.notification_list_url = reverse('notification-list')
        self.customer_notification_url = reverse('notification-detail', kwargs={'pk': self.customer_notification.pk})
        self.admin_notification_url = reverse('notification-detail', kwargs={'pk': self.admin_notification.pk})
    
    def test_customer_notification_list(self):
        """Test that customers can only see their own notifications."""
        self.client.force_authenticate(user=self.customer_user)
        response = self.client.get(self.notification_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Customer Notification')
    
    def test_admin_notification_list(self):
        """Test that admins can see all notifications."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.notification_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_mark_notification_as_read(self):
        """Test marking a notification as read."""
        self.client.force_authenticate(user=self.customer_user)
        mark_read_url = reverse('notification-mark-as-read', kwargs={'pk': self.customer_notification.pk})
        response = self.client.post(mark_read_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that notification status was updated
        self.customer_notification.refresh_from_db()
        self.assertEqual(self.customer_notification.status, 'read')
        self.assertIsNotNone(self.customer_notification.read_at)
    
    def test_mark_all_notifications_as_read(self):
        """Test marking all notifications as read."""
        # Create a second notification for the customer
        Notification.objects.create(
            user=self.customer_user,
            title='Second Notification',
            message='Second notification message',
            notification_type='system',
            channel='in_app',
            status='sent'
        )
        
        self.client.force_authenticate(user=self.customer_user)
        mark_all_read_url = reverse('notification-mark-all-as-read')
        response = self.client.post(mark_all_read_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that all customer's notifications are read
        notifications = Notification.objects.filter(user=self.customer_user)
        for notification in notifications:
            self.assertEqual(notification.status, 'read')
            self.assertIsNotNone(notification.read_at)


class LoyaltyViewSetTest(APITestCase):
    """Test the Loyalty API views."""
    
    def setUp(self):
        # Create users
        self.customer_user = User.objects.create_user(
            email='customer@example.com',
            password='testpassword',
            role='customer'
        )
        
        # Create loyalty record
        self.loyalty = Loyalty.objects.create(
            user=self.customer_user,
            points_balance=200,
            lifetime_points=250,
            tier='gold'
        )
        
        # Create loyalty transaction
        self.transaction = LoyaltyTransaction.objects.create(
            loyalty=self.loyalty,
            points=50,
            transaction_type='earn',
            description='Test transaction'
        )
        
        # Set up API client
        self.client = APIClient()
        self.loyalty_my_url = reverse('loyalty-my-loyalty')
    
    def test_my_loyalty(self):
        """Test retrieving the user's loyalty data."""
        self.client.force_authenticate(user=self.customer_user)
        response = self.client.get(self.loyalty_my_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['points_balance'], 200)
        self.assertEqual(response.data['tier'], 'gold')
        self.assertEqual(len(response.data['recent_transactions']), 1)
    
    def test_my_loyalty_creates_if_missing(self):
        """Test that my_loyalty creates a loyalty record if none exists."""
        # Create a new user without a loyalty record
        new_user = User.objects.create_user(
            email='newuser@example.com',
            password='testpassword',
            role='customer'
        )
        
        self.client.force_authenticate(user=new_user)
        response = self.client.get(self.loyalty_my_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['points_balance'], 0)
        self.assertEqual(response.data['tier'], 'standard')
        
        # Check that a loyalty record was created
        self.assertTrue(Loyalty.objects.filter(user=new_user).exists())