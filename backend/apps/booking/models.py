from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class Appointment(models.Model):
    """Model for appointments."""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
        ('no_show', 'No Show'),
    ]
    
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, 
                               related_name='appointments')
    therapist_profile = models.ForeignKey('clinic.TherapistProfile', on_delete=models.CASCADE, 
                                        related_name='appointments')
    service = models.ForeignKey('clinic.Service', on_delete=models.CASCADE, 
                              related_name='appointments')
    branch = models.ForeignKey('clinic.Branch', on_delete=models.CASCADE, 
                             related_name='appointments')
    start_time = models.DateTimeField(_('start time'))
    end_time = models.DateTimeField(_('end time'))
    status = models.CharField(_('status'), max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(_('notes'), blank=True, null=True)
    customer_notes = models.TextField(_('customer notes'), blank=True, null=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('appointment')
        verbose_name_plural = _('appointments')
        ordering = ['-start_time']
        
    def __str__(self):
        return f"{self.customer} - {self.service} - {self.start_time.strftime('%Y-%m-%d %H:%M')}"


class Payment(models.Model):
    """Model for payments."""
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
        ('partially_refunded', 'Partially Refunded'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('card', 'Card'),
        ('cash', 'Cash'),
        ('wallet', 'Wallet'),
        ('insurance', 'Insurance'),
        ('bank_transfer', 'Bank Transfer'),
        ('razorpay', 'Razorpay'),
    ]
    
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, 
                                  related_name='payments')
    amount = models.DecimalField(_('amount'), max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField(_('tax amount'), max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(_('discount amount'), max_digits=10, 
                                        decimal_places=2, default=0)
    total_amount = models.DecimalField(_('total amount'), max_digits=10, decimal_places=2)
    status = models.CharField(_('status'), max_length=20, choices=PAYMENT_STATUS_CHOICES, 
                            default='pending')
    payment_method = models.CharField(_('payment method'), max_length=20, 
                                    choices=PAYMENT_METHOD_CHOICES)
    transaction_id = models.CharField(_('transaction id'), max_length=255, blank=True, null=True)
    payment_date = models.DateTimeField(_('payment date'), blank=True, null=True)
    payment_details = models.JSONField(_('payment details'), blank=True, null=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('payment')
        verbose_name_plural = _('payments')
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.appointment} - {self.total_amount} - {self.status}"


class Invoice(models.Model):
    """Model for invoices."""
    
    INVOICE_STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('issued', 'Issued'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, 
                               related_name='invoices')
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, 
                                  related_name='invoices', null=True, blank=True)
    invoice_number = models.CharField(_('invoice number'), max_length=50, unique=True)
    issue_date = models.DateField(_('issue date'))
    due_date = models.DateField(_('due date'), blank=True, null=True)
    items = models.JSONField(_('items'))
    subtotal = models.DecimalField(_('subtotal'), max_digits=10, decimal_places=2)
    tax_rate = models.DecimalField(_('tax rate'), max_digits=5, decimal_places=2, default=0)
    tax_amount = models.DecimalField(_('tax amount'), max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(_('discount'), max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(_('total'), max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField(_('paid amount'), max_digits=10, decimal_places=2, default=0)
    status = models.CharField(_('status'), max_length=20, choices=INVOICE_STATUS_CHOICES, 
                            default='draft')
    notes = models.TextField(_('notes'), blank=True, null=True)
    terms = models.TextField(_('terms and conditions'), blank=True, null=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('invoice')
        verbose_name_plural = _('invoices')
        ordering = ['-issue_date']
        
    def __str__(self):
        return f"Invoice #{self.invoice_number} - {self.customer} - {self.total}"


class WaitlistEntry(models.Model):
    """Model for waitlist entries."""
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('notified', 'Notified'),
        ('booked', 'Booked'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    ]
    
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, 
                               related_name='waitlist_entries')
    service = models.ForeignKey('clinic.Service', on_delete=models.CASCADE, 
                              related_name='waitlist_entries')
    therapist_profile = models.ForeignKey('clinic.TherapistProfile', on_delete=models.CASCADE, 
                                        related_name='waitlist_entries', null=True, blank=True)
    branch = models.ForeignKey('clinic.Branch', on_delete=models.CASCADE, 
                             related_name='waitlist_entries')
    preferred_date = models.DateField(_('preferred date'))
    preferred_time_slots = models.JSONField(_('preferred time slots'), default=list)
    status = models.CharField(_('status'), max_length=20, choices=STATUS_CHOICES, default='active')
    notes = models.TextField(_('notes'), blank=True, null=True)
    position = models.PositiveIntegerField(_('position'), blank=True, null=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('waitlist entry')
        verbose_name_plural = _('waitlist entries')
        ordering = ['created_at']
        
    def __str__(self):
        return f"{self.customer} - {self.service} - {self.preferred_date}"