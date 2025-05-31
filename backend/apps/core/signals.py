from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import UserProfile, UserSettings

User = get_user_model()


@receiver(post_save, sender=User)
def create_user_profile_settings(sender, instance, created, **kwargs):
    """Create UserProfile and UserSettings when a new User is created."""
    if created:
        # Create profile if it doesn't exist
        if not hasattr(instance, 'profile'):
            UserProfile.objects.create(user=instance)
            
        # Create settings if they don't exist
        if not hasattr(instance, 'settings'):
            UserSettings.objects.create(user=instance)
