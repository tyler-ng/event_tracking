from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.db.models import Count, Avg, F, Sum
from django.utils import timezone
from datetime import timedelta

from .models import Event, Session, FeatureFlag, EventAggregate


@method_decorator(staff_member_required, name='dispatch')
class AnalyticsDashboardView(TemplateView):
    """
    Admin dashboard view for analytics data.
    
    This view is accessible only to staff members and displays
    various event statistics and visualizations.
    """
    template_name = 'analytics/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get date range from request or default to last 7 days
        days = int(self.request.GET.get('days', 7))
        event_type = self.request.GET.get('event_type', '')
        
        # Calculate date ranges
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        prev_start_date = start_date - timedelta(days=days)
        
        # Base queryset with time filter
        events_qs = Event.objects.filter(timestamp__gte=start_date)
        prev_events_qs = Event.objects.filter(
            timestamp__gte=prev_start_date,
            timestamp__lt=start_date
        )
        
        # Apply event type filter if specified
        if event_type:
            events_qs = events_qs.filter(event_type=event_type)
            prev_events_qs = prev_events_qs.filter(event_type=event_type)
        
        # Get all available event types for filter dropdown
        context['event_types'] = Event.objects.values_list(
            'event_type', flat=True
        ).distinct()
        
        # Calculate total events and growth rate
        total_events = events_qs.count()
        prev_total_events = prev_events_qs.count()
        
        if prev_total_events > 0:
            event_growth = ((total_events - prev_total_events) / prev_total_events) * 100
        else:
            event_growth = 100
        
        context['total_events'] = total_events
        context['event_growth'] = round(event_growth, 1)
        
        # Calculate unique users and growth rate
        unique_users = events_qs.values('distinct_id').distinct().count()
        prev_unique_users = prev_events_qs.values('distinct_id').distinct().count()
        
        if prev_unique_users > 0:
            user_growth = ((unique_users - prev_unique_users) / prev_unique_users) * 100
        else:
            user_growth = 100
        
        context['unique_users'] = unique_users
        context['user_growth'] = round(user_growth, 1)
        
        # Calculate session metrics
        sessions = Session.objects.filter(start_time__gte=start_date)
        
        # Average session duration
        avg_duration = sessions.exclude(duration__isnull=True).aggregate(
            avg_duration=Avg('duration')
        )['avg_duration']
        
        if avg_duration:
            # Format duration as minutes and seconds
            total_seconds = avg_duration.total_seconds()
            minutes = int(total_seconds // 60)
            seconds = int(total_seconds % 60)
            context['avg_session_duration'] = f"{minutes}m {seconds}s"
        else:
            context['avg_session_duration'] = "N/A"
        
        # Events per session
        events_per_session = sessions.exclude(events_count=0).aggregate(
            avg_events=Avg('events_count')
        )['avg_events'] or 0
        
        context['events_per_session'] = round(events_per_session, 1)
        
        # Get recent events for table
        context['recent_events'] = events_qs.order_by('-timestamp')[:50]
        
        # Get data for daily events chart
        daily_counts = events_qs.extra(
            select={'day': "DATE(timestamp)"}
        ).values('day').annotate(
            count=Count('id')
        ).order_by('day')
        
        context['daily_counts'] = list(daily_counts)
        
        # Get data for top event types chart
        event_type_counts = events_qs.values('event_type').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        context['event_type_counts'] = list(event_type_counts)
        
        # Get data for device distribution chart
        device_counts = events_qs.values('os_name').annotate(
            count=Count('id')
        ).order_by('-count')
        
        context['device_counts'] = list(device_counts)
        
        # Get data for app version distribution chart
        version_counts = events_qs.values('app_version').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        context['version_counts'] = list(version_counts)
        
        return context 