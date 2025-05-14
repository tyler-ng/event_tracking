import uuid
from django.db import models
from django.utils import timezone
from apps.users.models import User


class DeviceInfo(models.Model):
    """
    Stores device information that rarely changes to reduce redundancy.
    """
    device_id = models.CharField(max_length=100, primary_key=True)
    app_version = models.CharField(max_length=50)
    os_name = models.CharField(max_length=50)
    os_version = models.CharField(max_length=50)
    is_simulator = models.BooleanField(null=True, blank=True, help_text="Whether the device is a simulator/emulator")
    is_rooted_device = models.BooleanField(null=True, blank=True, help_text="Whether the device is rooted/jailbroken")
    is_vpn_enabled = models.BooleanField(null=True, blank=True, help_text="Whether a VPN is active on the device")
    last_seen = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.device_id} - {self.os_name} {self.os_version}"
    
    class Meta:
        verbose_name = "Device Information"
        verbose_name_plural = "Device Information"


class LocationInfo(models.Model):
    """
    Stores location information to reduce redundancy.
    """
    id = models.AutoField(primary_key=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True, unique=True)
    city = models.CharField(max_length=100, null=True, blank=True, help_text="City based on IP geolocation")
    country = models.CharField(max_length=100, null=True, blank=True, help_text="Country based on IP geolocation")
    continent = models.CharField(max_length=100, null=True, blank=True, help_text="Continent based on IP geolocation")
    
    def __str__(self):
        return f"{self.ip_address} - {self.city}, {self.country}"
    
    class Meta:
        verbose_name = "Location Information"
        verbose_name_plural = "Location Information"
        indexes = [
            models.Index(fields=['country']),
            models.Index(fields=['city']),
        ]


class Session(models.Model):
    """
    Represents a user session with start and end times.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    distinct_id = models.CharField(max_length=200, db_index=True)
    device = models.ForeignKey(DeviceInfo, on_delete=models.PROTECT, related_name='sessions', null=True, blank=True)
    start_time = models.DateTimeField(db_index=True)
    end_time = models.DateTimeField(null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)
    events_count = models.IntegerField(default=0)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    # Location can change during a session (e.g. mobile user moving)
    location = models.ForeignKey(LocationInfo, null=True, blank=True, on_delete=models.SET_NULL, related_name='sessions')
    latitude = models.FloatField(null=True, blank=True, help_text="Latitude of the device location")
    longitude = models.FloatField(null=True, blank=True, help_text="Longitude of the device location")
    app_check_result = models.BooleanField(null=True, blank=True, help_text="Result of Firebase App Check verification")
    
    class Meta:
        indexes = [
            models.Index(fields=['distinct_id']),
            models.Index(fields=['start_time']),
        ]
        ordering = ['-start_time']
    
    def __str__(self):
        return f"Session {self.id} - {self.distinct_id}"
    
    def calculate_duration(self):
        if self.end_time and self.start_time:
            self.duration = self.end_time - self.start_time
            return self.duration
        return None


class Event(models.Model):
    """
    Stores event data captured from mobile applications.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='events', null=True, blank=True)
    distinct_id = models.CharField(max_length=200, help_text="Anonymous user identifier")
    event_type = models.CharField(max_length=100, db_index=True)
    properties = models.JSONField(default=dict, help_text="Event properties in JSON format")
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    # We can still reference the device directly for events without sessions
    device = models.ForeignKey(DeviceInfo, on_delete=models.PROTECT, related_name='events', null=True, blank=True)
    # Location can change during a session (e.g. mobile user moving)
    location = models.ForeignKey(LocationInfo, null=True, blank=True, on_delete=models.SET_NULL, related_name='events')
    # Fields that remain in the model
    latitude = models.FloatField(null=True, blank=True, help_text="Latitude of the device location")
    longitude = models.FloatField(null=True, blank=True, help_text="Longitude of the device location")
    app_check_result = models.BooleanField(null=True, blank=True, help_text="Result of Firebase App Check verification")
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, 
                            help_text="Associated user if identified")
    processed = models.BooleanField(default=False, help_text="Whether this event has been processed")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['distinct_id']),
            models.Index(fields=['event_type']),
            models.Index(fields=['timestamp']),
            models.Index(fields=['processed']),
        ]
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.event_type} - {self.distinct_id} - {self.timestamp}"


class FeatureFlag(models.Model):
    """
    Feature flags for controlling feature availability and A/B testing.
    """
    name = models.CharField(max_length=100, unique=True)
    key = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    active = models.BooleanField(default=False)
    rollout_percentage = models.IntegerField(default=0, 
                                            help_text="Percentage of users who should see this feature (0-100)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        status = "Active" if self.active else "Inactive"
        return f"{self.name} ({status})"


class EventAggregate(models.Model):
    """
    Pre-computed aggregations of event data for faster dashboard loading.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event_type = models.CharField(max_length=100, db_index=True)
    date = models.DateField(db_index=True)
    hour = models.IntegerField(null=True, blank=True, 
                              help_text="Hour of day (0-23) if this is an hourly aggregate")
    count = models.IntegerField(default=0)
    unique_users = models.IntegerField(default=0)
    properties = models.JSONField(default=dict, help_text="Aggregated properties in JSON format")
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['event_type', 'date', 'hour'],
                name='unique_event_aggregate'
            )
        ]
    
    def __str__(self):
        time_str = f"{self.date}"
        if self.hour is not None:
            time_str += f" {self.hour:02d}:00"
        return f"{self.event_type} - {time_str} - {self.count} events" 