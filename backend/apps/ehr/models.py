from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class MedicalHistory(models.Model):
    """Model for patient medical history."""
    
    customer = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, 
                                  related_name='medical_history')
    allergies = models.JSONField(_('allergies'), default=list)
    medical_conditions = models.JSONField(_('medical conditions'), default=list)
    medications = models.JSONField(_('medications'), default=list)
    surgeries = models.JSONField(_('surgeries'), default=list)
    family_history = models.JSONField(_('family history'), default=list)
    lifestyle = models.JSONField(_('lifestyle'), default=dict)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('medical history')
        verbose_name_plural = _('medical histories')
        
    def __str__(self):
        return f"Medical History for {self.customer.email}"


class TreatmentSession(models.Model):
    """Model for treatment session records."""
    
    STATUS_CHOICES = [
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    appointment = models.OneToOneField('booking.Appointment', on_delete=models.CASCADE, 
                                     related_name='treatment_session')
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, 
                               related_name='treatment_sessions')
    therapist = models.ForeignKey('clinic.TherapistProfile', on_delete=models.CASCADE, 
                                related_name='treatment_sessions')
    service = models.ForeignKey('clinic.Service', on_delete=models.CASCADE, 
                              related_name='treatment_sessions')
    status = models.CharField(_('status'), max_length=20, choices=STATUS_CHOICES, default='planned')
    notes = models.TextField(_('session notes'), blank=True, null=True)
    clinical_findings = models.JSONField(_('clinical findings'), default=dict, blank=True)
    treatment_provided = models.TextField(_('treatment provided'), blank=True, null=True)
    medications_prescribed = models.JSONField(_('medications prescribed'), default=list, blank=True)
    recommendations = models.TextField(_('recommendations'), blank=True, null=True)
    follow_up = models.TextField(_('follow up'), blank=True, null=True)
    attachments = models.JSONField(_('attachments'), default=list, blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('treatment session')
        verbose_name_plural = _('treatment sessions')
        ordering = ['-created_at']
        
    def __str__(self):
        return f"Session for {self.customer.email} on {self.created_at.strftime('%Y-%m-%d')}"


class SymptomTracker(models.Model):
    """Model for tracking patient symptoms over time."""
    
    TYPE_CHOICES = [
        ('scale', 'Scale (1-10)'),
        ('boolean', 'Boolean (Yes/No)'),
        ('text', 'Text'),
    ]
    
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, 
                               related_name='symptom_trackers')
    symptom_name = models.CharField(_('symptom name'), max_length=100)
    description = models.TextField(_('description'), blank=True, null=True)
    type = models.CharField(_('type'), max_length=10, choices=TYPE_CHOICES, default='scale')
    date_recorded = models.DateField(_('date recorded'))
    value = models.JSONField(_('value'))
    notes = models.TextField(_('notes'), blank=True, null=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('symptom tracker')
        verbose_name_plural = _('symptom trackers')
        ordering = ['-date_recorded']
        
    def __str__(self):
        return f"{self.symptom_name} for {self.customer.email} on {self.date_recorded}"


class WellnessJournal(models.Model):
    """Model for patient wellness journal entries."""
    
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, 
                               related_name='wellness_journals')
    title = models.CharField(_('title'), max_length=255)
    content = models.TextField(_('content'))
    mood = models.CharField(_('mood'), max_length=50, blank=True, null=True)
    energy_level = models.PositiveIntegerField(_('energy level'), blank=True, null=True)
    tags = models.JSONField(_('tags'), default=list, blank=True)
    date_recorded = models.DateField(_('date recorded'))
    is_private = models.BooleanField(_('is private'), default=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('wellness journal')
        verbose_name_plural = _('wellness journals')
        ordering = ['-date_recorded']
        
    def __str__(self):
        return f"{self.title} - {self.customer.email} on {self.date_recorded}"


class FileAttachment(models.Model):
    """Model for file attachments to treatment sessions."""
    
    FILE_TYPE_CHOICES = [
        ('image', 'Image'),
        ('document', 'Document'),
        ('lab_report', 'Lab Report'),
        ('prescription', 'Prescription'),
        ('other', 'Other'),
    ]
    
    treatment_session = models.ForeignKey(TreatmentSession, on_delete=models.CASCADE, 
                                        related_name='file_attachments')
    file = models.FileField(_('file'), upload_to='ehr_attachments/')
    file_type = models.CharField(_('file type'), max_length=20, choices=FILE_TYPE_CHOICES)
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), blank=True, null=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, 
                                  related_name='uploaded_files', null=True)
    uploaded_at = models.DateTimeField(_('uploaded at'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('file attachment')
        verbose_name_plural = _('file attachments')
        ordering = ['-uploaded_at']
        
    def __str__(self):
        return f"{self.name} for {self.treatment_session}"