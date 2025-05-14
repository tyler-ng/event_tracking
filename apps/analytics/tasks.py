import logging
from datetime import datetime, time, timedelta
from django.db import transaction
from django.db.models import Count
from django.utils import timezone
from celery import shared_task

from .models import Event, Session, EventAggregate

logger = logging.getLogger(__name__)


@shared_task
def process_event(event_id):
    """
    Process a single event.
    
    This task:
    1. Updates session data
    2. Identifies the user if possible
    3. Marks the event as processed
    """
    try:
        event = Event.objects.select_for_update().get(id=event_id)
        
        if event.processed:
            logger.info(f"Event {event_id} already processed, skipping")
            return True
            
        with transaction.atomic():
            # Find or create a session for this event
            update_session_for_event(event)
            
            # Mark as processed
            event.processed = True
            event.save(update_fields=['processed'])
            
        return True
    except Event.DoesNotExist:
        logger.error(f"Event with ID {event_id} not found")
        return False
    except Exception as e:
        logger.exception(f"Error processing event {event_id}: {str(e)}")
        return False


@shared_task
def process_event_batch(event_ids):
    """
    Process a batch of events.
    """
    logger.info(f"Processing batch of {len(event_ids)} events")
    success_count = 0
    error_count = 0
    
    for event_id in event_ids:
        result = process_event(event_id)
        if result:
            success_count += 1
        else:
            error_count += 1
    
    logger.info(f"Batch processing completed: {success_count} succeeded, {error_count} failed")
    return {
        'success_count': success_count,
        'error_count': error_count
    }


def update_session_for_event(event):
    """
    Update or create a session for the given event.
    """
    # Try to find a recent session for this user
    recent_session = Session.objects.filter(
        distinct_id=event.distinct_id,
        device_id=event.device_id,
        end_time__isnull=True,  # Session is still open
        start_time__gt=timezone.now() - timedelta(hours=6)  # Within 6 hours
    ).order_by('-start_time').first()
    
    if recent_session:
        # Update existing session
        recent_session.events_count += 1
        recent_session.save(update_fields=['events_count'])
    else:
        # Create a new session
        Session.objects.create(
            distinct_id=event.distinct_id,
            device_id=event.device_id,
            start_time=event.timestamp,
            events_count=1,
            app_version=event.app_version,
            os_name=event.os_name,
            os_version=event.os_version,
            is_simulator=event.is_simulator,
            is_rooted_device=event.is_rooted_device,
            is_vpn_enabled=event.is_vpn_enabled,
            latitude=event.latitude,
            longitude=event.longitude,
            ip_address=event.ip_address,
            city=event.city,
            country=event.country,
            continent=event.continent,
            user=event.user
        )


@shared_task
def aggregate_daily_events():
    """
    Aggregate events by day for faster analytics.
    
    This task is scheduled to run once a day and
    aggregates the previous day's events.
    """
    yesterday = (timezone.now() - timedelta(days=1)).date()
    
    # Get all event types from yesterday
    event_types = Event.objects.filter(
        timestamp__date=yesterday
    ).values_list('event_type', flat=True).distinct()
    
    for event_type in event_types:
        # Count events of this type
        events = Event.objects.filter(
            timestamp__date=yesterday,
            event_type=event_type
        )
        
        count = events.count()
        unique_users = events.values('distinct_id').distinct().count()
        
        # Create or update aggregate
        EventAggregate.objects.update_or_create(
            event_type=event_type,
            date=yesterday,
            hour=None,  # None indicates a daily aggregate
            defaults={
                'count': count,
                'unique_users': unique_users,
                'properties': {}  # Add aggregated properties if needed
            }
        )
    
    return f"Aggregated events for {yesterday}"


@shared_task
def aggregate_hourly_events():
    """
    Aggregate events by hour for faster analytics.
    
    This task is scheduled to run every hour and
    aggregates the previous hour's events.
    """
    now = timezone.now()
    previous_hour = now - timedelta(hours=1)
    date = previous_hour.date()
    hour = previous_hour.hour
    
    # Get all event types from the previous hour
    event_types = Event.objects.filter(
        timestamp__date=date,
        timestamp__hour=hour
    ).values_list('event_type', flat=True).distinct()
    
    for event_type in event_types:
        # Count events of this type
        events = Event.objects.filter(
            timestamp__date=date,
            timestamp__hour=hour,
            event_type=event_type
        )
        
        count = events.count()
        unique_users = events.values('distinct_id').distinct().count()
        
        # Create or update aggregate
        EventAggregate.objects.update_or_create(
            event_type=event_type,
            date=date,
            hour=hour,
            defaults={
                'count': count,
                'unique_users': unique_users,
                'properties': {}  # Add aggregated properties if needed
            }
        )
    
    return f"Aggregated events for {date} hour {hour}"


@shared_task
def close_inactive_sessions():
    """
    Close sessions that have been inactive for too long.
    
    This task finds sessions without an end time that haven't had
    any events for a while, and sets their end time.
    """
    # Find sessions that haven't ended but should have
    cutoff_time = timezone.now() - timedelta(minutes=30)
    
    inactive_sessions = Session.objects.filter(
        end_time__isnull=True,
        start_time__lt=cutoff_time
    )
    
    count = 0
    for session in inactive_sessions:
        # Set the end time to the last event or a default value
        last_event = Event.objects.filter(
            distinct_id=session.distinct_id,
            device_id=session.device_id,
            timestamp__gt=session.start_time
        ).order_by('-timestamp').first()
        
        if last_event:
            session.end_time = last_event.timestamp
        else:
            # If no events, use start time + a short duration
            session.end_time = session.start_time + timedelta(minutes=1)
        
        session.calculate_duration()
        session.save()
        count += 1
    
    return f"Closed {count} inactive sessions" 