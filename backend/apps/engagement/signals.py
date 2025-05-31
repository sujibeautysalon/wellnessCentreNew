from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.core.models import User
from apps.engagement.models import Loyalty


@receiver(post_save, sender=User)
def create_user_loyalty(sender, instance, created, **kwargs):
    """
    Create a loyalty record for new users.
    """
    if created and instance.role == 'customer':
        Loyalty.objects.get_or_create(
            user=instance,
            defaults={
                'points_balance': 0,
                'lifetime_points': 0,
                'tier': 'standard'
            }
        )
