from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import Event

User = get_user_model()

@receiver(post_save, sender=User)
def track_user_events(sender, instance, created, **kwargs):
    """
    Track user-related events.
    
    When a user is created or updated, we create an event in the
    analytics system to track this activity.
    """
    if created:
        # New user created
        Event.objects.create(
            distinct_id=str(instance.id),
            event_type='user_created',
            properties={
                'username': instance.username,
                'email': instance.email,
                'is_staff': instance.is_staff,
            },
            timestamp=timezone.now(),
            device_id='system',
            app_version='1.0',
            os_name='system',
            os_version='1.0',
            user=instance,
        )
    else:
        # Existing user updated
        # Only track significant changes to avoid noise
        changed_fields = []
        if instance.tracker.has_changed('email'):
            changed_fields.append('email')
        if instance.tracker.has_changed('is_active'):
            changed_fields.append('is_active')
        
        if changed_fields:
            Event.objects.create(
                distinct_id=str(instance.id),
                event_type='user_updated',
                properties={
                    'username': instance.username,
                    'email': instance.email,
                    'is_staff': instance.is_staff,
                    'changed_fields': changed_fields,
                },
                timestamp=timezone.now(),
                device_id='system',
                app_version='1.0',
                os_name='system',
                os_version='1.0',
                user=instance,
            ) 