from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
import json

from .models import Event, Session, FeatureFlag, EventAggregate, DeviceInfo, LocationInfo


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


@admin.register(DeviceInfo)
class DeviceInfoAdmin(admin.ModelAdmin):
    list_display = ('device_id', 'os_name', 'os_version', 'app_version', 'is_simulator', 'is_rooted_device', 'is_vpn_enabled', 'last_seen')
    list_filter = ('os_name', 'app_version', 'is_simulator', 'is_rooted_device', 'is_vpn_enabled')
    search_fields = ('device_id', 'os_name', 'os_version', 'app_version')
    readonly_fields = ('last_seen',)


@admin.register(LocationInfo)
class LocationInfoAdmin(admin.ModelAdmin):
    list_display = ('ip_address', 'city', 'country', 'continent')
    list_filter = ('country', 'continent')
    search_fields = ('ip_address', 'city', 'country')


@admin.register(Event)
class EventAdmin(admin.ModelAdmin, JSONFieldPrettifyMixin):
    list_display = ('event_type', 'distinct_id', 'timestamp', 'processed', 'get_device_id', 'get_country', 'app_check_result')
    list_filter = ('event_type', 'processed', 'app_check_result', 'device__os_name', 'device__is_simulator', 'device__is_rooted_device', 'device__is_vpn_enabled', 'location__country')
    search_fields = ('distinct_id', 'event_type', 'device__device_id', 'location__city', 'location__country')
    readonly_fields = ('id', 'created_at', 'properties_pretty')
    date_hierarchy = 'timestamp'
    raw_id_fields = ('device', 'location', 'session', 'user')
    
    def get_device_id(self, obj):
        return obj.device.device_id if obj.device else "-"
    get_device_id.short_description = "Device ID"
    get_device_id.admin_order_field = "device__device_id"
    
    def get_country(self, obj):
        return obj.location.country if obj.location else "-"
    get_country.short_description = "Country"
    get_country.admin_order_field = "location__country"
    
    fieldsets = (
        (None, {
            'fields': ('id', 'event_type', 'distinct_id', 'properties_pretty', 'timestamp', 'session')
        }),
        ('Device Information', {
            'fields': ('device',)
        }),
        ('Location Information', {
            'fields': ('location', 'latitude', 'longitude')
        }),
        ('Security', {
            'fields': ('app_check_result',)
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
    list_display = ('distinct_id', 'start_time', 'end_time', 'duration_display', 'events_count', 'get_device_id', 'get_country', 'app_check_result')
    list_filter = ('device__os_name', 'device__app_version', 'location__country', 'device__is_simulator', 'device__is_rooted_device', 'device__is_vpn_enabled', 'app_check_result')
    search_fields = ('distinct_id', 'device__device_id', 'location__city', 'location__country')
    readonly_fields = ('id', 'duration', 'events_count')
    date_hierarchy = 'start_time'
    raw_id_fields = ('device', 'location', 'user')
    
    def get_device_id(self, obj):
        return obj.device.device_id if obj.device else "-"
    get_device_id.short_description = "Device ID"
    get_device_id.admin_order_field = "device__device_id"
    
    def get_country(self, obj):
        return obj.location.country if obj.location else "-"
    get_country.short_description = "Country"
    get_country.admin_order_field = "location__country"
    
    fieldsets = (
        (None, {
            'fields': ('id', 'distinct_id', 'start_time', 'end_time', 'duration', 'events_count')
        }),
        ('Device Information', {
            'fields': ('device',)
        }),
        ('Location Information', {
            'fields': ('location', 'latitude', 'longitude')
        }),
        ('Security', {
            'fields': ('app_check_result',)
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