from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
import logging

from apps.analytics.models import Event

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Clean up old events based on retention policy'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=None,
            help='Number of days to keep events (defaults to settings.EVENT_TRACKING["RETENTION_DAYS"])',
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=10000,
            help='Batch size for deletion operations',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        # Determine retention period
        days = options['days']
        if days is None:
            days = getattr(settings, 'EVENT_TRACKING', {}).get('RETENTION_DAYS', 365)
        
        batch_size = options['batch_size']
        dry_run = options['dry_run']
        
        # Calculate cutoff date
        cutoff_date = timezone.now() - timedelta(days=days)
        
        # Count events to be deleted
        count = Event.objects.filter(timestamp__lt=cutoff_date).count()
        
        if dry_run:
            self.stdout.write(f"Would delete {count} events older than {cutoff_date.strftime('%Y-%m-%d')}")
            return
        
        if count == 0:
            self.stdout.write("No events to delete")
            return
        
        self.stdout.write(f"Deleting {count} events older than {cutoff_date.strftime('%Y-%m-%d')}")
        
        # Delete in batches to avoid memory issues
        deleted_count = 0
        while True:
            # Get a batch of old event IDs
            event_ids = list(
                Event.objects.filter(timestamp__lt=cutoff_date)
                .values_list('id', flat=True)[:batch_size]
            )
            
            if not event_ids:
                break
                
            # Delete this batch
            batch_deleted = Event.objects.filter(id__in=event_ids).delete()[0]
            deleted_count += batch_deleted
            
            self.stdout.write(f"Deleted batch of {batch_deleted} events. Progress: {deleted_count}/{count}")
        
        self.stdout.write(self.style.SUCCESS(f"Successfully deleted {deleted_count} old events")) 