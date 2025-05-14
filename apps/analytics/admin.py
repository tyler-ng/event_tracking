from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
import json

from .models import Event, Session, FeatureFlag, EventAggregate


class JSONFieldPrettifyMixin:
    """
    Mixin to display JSON fields in a more readable format in the admin.
    """
    def prettify_json_field(self, obj, field_name):
        value = getattr(obj, field_name)
        if not value:
            return "-"
        
        try:
            # Format the JSON data for readable display
            formatted_json = json.dumps(value, indent=2)
            return mark_safe(f'<pre>{formatted_json}</pre>')
        except Exception:
            return str(value)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin, JSONFieldPrettifyMixin):
    list_display = ('event_type', 'distinct_id', 'timestamp', 'processed', 'device_id', 'country', 'city', 'app_check_result')
    list_filter = ('event_type', 'processed', 'os_name', 'app_version', 'country', 'is_simulator', 'is_rooted_device', 'is_vpn_enabled', 'app_check_result')
    search_fields = ('distinct_id', 'event_type', 'device_id', 'city', 'country')
    readonly_fields = ('id', 'created_at', 'properties_pretty')
    date_hierarchy = 'timestamp'
    
    fieldsets = (
        (None, {
            'fields': ('id', 'event_type', 'distinct_id', 'properties_pretty', 'timestamp')
        }),
        ('Device Information', {
            'fields': ('device_id', 'app_version', 'os_name', 'os_version', 'ip_address')
        }),
        ('Device Status', {
            'fields': ('is_simulator', 'is_rooted_device', 'is_vpn_enabled', 'app_check_result')
        }),
        ('Location Information', {
            'fields': ('latitude', 'longitude', 'city', 'country', 'continent')
        }),
        ('Processing Status', {
            'fields': ('processed', 'created_at', 'user')
        }),
    )
    
    def properties_pretty(self, obj):
        """Display the JSON properties in a readable format."""
        return self.prettify_json_field(obj, 'properties')
    properties_pretty.short_description = 'Properties'


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('distinct_id', 'start_time', 'end_time', 'duration_display', 'events_count', 'country', 'city', 'app_check_result')
    list_filter = ('os_name', 'app_version', 'country', 'is_simulator', 'is_rooted_device', 'is_vpn_enabled', 'app_check_result')
    search_fields = ('distinct_id', 'device_id', 'city', 'country')
    readonly_fields = ('id', 'duration')
    date_hierarchy = 'start_time'
    
    fieldsets = (
        (None, {
            'fields': ('id', 'distinct_id', 'start_time', 'end_time', 'duration', 'events_count')
        }),
        ('Device Information', {
            'fields': ('device_id', 'app_version', 'os_name', 'os_version', 'ip_address')
        }),
        ('Device Status', {
            'fields': ('is_simulator', 'is_rooted_device', 'is_vpn_enabled', 'app_check_result')
        }),
        ('Location Information', {
            'fields': ('latitude', 'longitude', 'city', 'country', 'continent')
        }),
        ('User Information', {
            'fields': ('user',)
        }),
    )
    
    def duration_display(self, obj):
        if obj.duration:
            # Format duration as minutes and seconds
            total_seconds = obj.duration.total_seconds()
            minutes = int(total_seconds // 60)
            seconds = int(total_seconds % 60)
            return f"{minutes}m {seconds}s"
        return "-"
    duration_display.short_description = 'Duration'


@admin.register(FeatureFlag)
class FeatureFlagAdmin(admin.ModelAdmin):
    list_display = ('name', 'key', 'active_badge', 'rollout_percentage', 'updated_at')
    list_filter = ('active',)
    search_fields = ('name', 'key', 'description')
    readonly_fields = ('created_at', 'updated_at')
    
    def active_badge(self, obj):
        if obj.active:
            return format_html('<span style="background-color: #28a745; color: white; padding: 3px 8px; border-radius: 4px;">Active</span>')
        return format_html('<span style="background-color: #dc3545; color: white; padding: 3px 8px; border-radius: 4px;">Inactive</span>')
    active_badge.short_description = 'Status'


@admin.register(EventAggregate)
class EventAggregateAdmin(admin.ModelAdmin, JSONFieldPrettifyMixin):
    list_display = ('event_type', 'date', 'hour_display', 'count', 'unique_users')
    list_filter = ('event_type', 'date')
    date_hierarchy = 'date'
    readonly_fields = ('id', 'properties_pretty')
    
    def hour_display(self, obj):
        if obj.hour is not None:
            return f"{obj.hour:02d}:00"
        return "Daily"
    hour_display.short_description = 'Hour'
    
    def properties_pretty(self, obj):
        """Display the JSON properties in a readable format."""
        return self.prettify_json_field(obj, 'properties')
    properties_pretty.short_description = 'Properties' 