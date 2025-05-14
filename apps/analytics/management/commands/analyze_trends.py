from django.core.management.base import BaseCommand
from django.db.models import Count, F, Sum
from django.utils import timezone
from datetime import timedelta

from apps.analytics.models import Event, EventAggregate


class Command(BaseCommand):
    help = 'Analyze trends in event data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=7,
            help='Number of days to analyze',
        )
        parser.add_argument(
            '--event-type',
            type=str,
            help='Filter by event type',
        )

    def handle(self, *args, **options):
        days = options['days']
        event_type = options.get('event_type')
        
        # Define the date range
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        self.stdout.write(f'Analyzing events from {start_date} to {end_date}')
        
        # Get base queryset
        queryset = Event.objects.filter(
            timestamp__date__gte=start_date,
            timestamp__date__lte=end_date
        )
        
        if event_type:
            queryset = queryset.filter(event_type=event_type)
            self.stdout.write(f'Filtering by event type: {event_type}')
        
        # Get total count
        total_count = queryset.count()
        self.stdout.write(f'Total events: {total_count}')
        
        # Events by type
        self.stdout.write('\nEvents by type:')
        event_counts = queryset.values('event_type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        for event in event_counts:
            self.stdout.write(f"  {event['event_type']}: {event['count']} events")
        
        # Daily event counts
        self.stdout.write('\nDaily event counts:')
        daily_counts = queryset.extra({
            'day': "date(timestamp)"
        }).values('day').annotate(
            count=Count('id')
        ).order_by('day')
        
        for day in daily_counts:
            self.stdout.write(f"  {day['day']}: {day['count']} events")
        
        # Unique users per day
        self.stdout.write('\nUnique users per day:')
        unique_users = queryset.extra({
            'day': "date(timestamp)"
        }).values('day').annotate(
            unique_users=Count('distinct_id', distinct=True)
        ).order_by('day')
        
        for day in unique_users:
            self.stdout.write(f"  {day['day']}: {day['unique_users']} unique users")
        
        # Top device types
        self.stdout.write('\nTop device types:')
        devices = queryset.values('os_name').annotate(
            count=Count('id')
        ).order_by('-count')
        
        for device in devices:
            self.stdout.write(f"  {device['os_name']}: {device['count']} events")
        
        # Check data completeness
        self.stdout.write('\nData completeness:')
        total_days = (end_date - start_date).days + 1
        covered_days = daily_counts.count()
        
        if covered_days < total_days:
            self.stdout.write(
                self.style.WARNING(
                    f'Data incomplete: {covered_days} days with data out of {total_days} days in range'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Data complete for all {total_days} days')
            ) 