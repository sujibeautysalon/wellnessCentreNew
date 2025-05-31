from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class Branch(models.Model):
    """Model for clinic branches."""
    
    name = models.CharField(_('name'), max_length=255)
    address = models.TextField(_('address'))
    city = models.CharField(_('city'), max_length=100)
    state = models.CharField(_('state'), max_length=100)
    country = models.CharField(_('country'), max_length=100)
    postal_code = models.CharField(_('postal code'), max_length=20)
    phone = models.CharField(_('phone'), max_length=20)
    email = models.EmailField(_('email'), blank=True, null=True)
    latitude = models.DecimalField(_('latitude'), max_digits=9, decimal_places=6, 
                                 blank=True, null=True)
    longitude = models.DecimalField(_('longitude'), max_digits=9, decimal_places=6, 
                                  blank=True, null=True)
    timezone = models.CharField(_('timezone'), max_length=50, default='UTC')
    opening_hours = models.JSONField(_('opening hours'), default=dict)
    is_active = models.BooleanField(_('is active'), default=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('branch')
        verbose_name_plural = _('branches')
        ordering = ['name']
        
    def __str__(self):
        return f"{self.name} ({self.city})"


class Service(models.Model):
    """Model for clinic services."""
    
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'))
    duration = models.PositiveIntegerField(_('duration in minutes'), 
                                         help_text=_('Duration in minutes'))
    price = models.DecimalField(_('price'), max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(_('discount price'), max_digits=10, 
                                       decimal_places=2, blank=True, null=True)
    category = models.CharField(_('category'), max_length=100)
    is_active = models.BooleanField(_('is active'), default=True)
    image = models.ImageField(_('image'), upload_to='services/', blank=True, null=True)
    max_capacity = models.PositiveIntegerField(_('max capacity'), default=1, 
                                             help_text=_('Maximum number of clients per session'))
    preparation_time = models.PositiveIntegerField(_('preparation time'), default=0, 
                                                 help_text=_('Preparation time in minutes'))
    cooldown_time = models.PositiveIntegerField(_('cooldown time'), default=0, 
                                              help_text=_('Cooldown time in minutes'))
    available_branches = models.ManyToManyField(Branch, related_name='services', 
                                              verbose_name=_('available branches'))
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('service')
        verbose_name_plural = _('services')
        ordering = ['name']
        
    def __str__(self):
        return f"{self.name} ({self.duration} min, {self.price})"


class TherapistProfile(models.Model):
    """Model for therapist profiles."""
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, 
                              related_name='therapist_profile')
    title = models.CharField(_('title'), max_length=100, blank=True, null=True)
    bio = models.TextField(_('bio'), blank=True, null=True)
    specializations = models.JSONField(_('specializations'), default=list)
    years_of_experience = models.PositiveIntegerField(_('years of experience'), default=0)
    education = models.JSONField(_('education'), default=list)
    certifications = models.JSONField(_('certifications'), default=list)
    languages = models.JSONField(_('languages'), default=list)
    branches = models.ManyToManyField(Branch, related_name='therapists', 
                                    verbose_name=_('branches'))
    services = models.ManyToManyField(Service, related_name='therapists', 
                                    verbose_name=_('services'))
    profile_image = models.ImageField(_('profile image'), upload_to='therapists/', 
                                    blank=True, null=True)
    average_rating = models.DecimalField(_('average rating'), max_digits=3, decimal_places=2, 
                                       default=0, 
                                       validators=[MinValueValidator(0), MaxValueValidator(5)])
    rating_count = models.PositiveIntegerField(_('rating count'), default=0)
    is_active = models.BooleanField(_('is active'), default=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('therapist profile')
        verbose_name_plural = _('therapist profiles')
        ordering = ['-average_rating', 'user__first_name']
        
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.title or 'Therapist'}"


class TherapistAvailability(models.Model):
    """Model for therapist availability."""
    
    RECURRENCE_CHOICES = [
        ('none', 'None'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('biweekly', 'Bi-Weekly'),
        ('monthly', 'Monthly'),
    ]
    
    therapist = models.ForeignKey(TherapistProfile, on_delete=models.CASCADE, 
                                related_name='availability')
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, null=True, blank=True, 
                             related_name='therapist_availability')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, null=True, blank=True, 
                              related_name='therapist_availability')
    start_time = models.DateTimeField(_('start time'))
    end_time = models.DateTimeField(_('end time'))
    is_available = models.BooleanField(_('is available'), default=True)
    recurrence = models.CharField(_('recurrence'), max_length=20, choices=RECURRENCE_CHOICES, 
                                default='none')
    recurrence_end_date = models.DateField(_('recurrence end date'), null=True, blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('therapist availability')
        verbose_name_plural = _('therapist availability')
        ordering = ['start_time']
        
    def __str__(self):
        return f"{self.therapist} - {self.start_time.strftime('%Y-%m-%d %H:%M')} to {self.end_time.strftime('%H:%M')}"


class Holiday(models.Model):
    """Model for holidays/closures."""
    
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, null=True, blank=True, 
                             related_name='holidays')
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), blank=True, null=True)
    start_date = models.DateField(_('start date'))
    end_date = models.DateField(_('end date'))
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('holiday')
        verbose_name_plural = _('holidays')
        ordering = ['start_date']
        
    def __str__(self):
        return f"{self.name} ({self.start_date} to {self.end_date})"