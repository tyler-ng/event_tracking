from rest_framework import serializers
from .models import Event, Session, FeatureFlag, EventAggregate, DeviceInfo, LocationInfo
from .utils import create_event, create_session


class DeviceInfoSerializer(serializers.ModelSerializer):
    """
    Serializer for device information.
    """
    class Meta:
        model = DeviceInfo
        fields = [
            'device_id', 'app_version', 'os_name', 'os_version',
            'is_simulator', 'is_rooted_device', 'is_vpn_enabled'
        ]


class LocationInfoSerializer(serializers.ModelSerializer):
    """
    Serializer for location information.
    """
    class Meta:
        model = LocationInfo
        fields = [
            'ip_address', 'city', 'country', 'continent'
        ]


class EventSerializer(serializers.ModelSerializer):
    """
    Serializer for individual events.
    """
    # Include the complete nested device and location data
    device_info = DeviceInfoSerializer(source='device', read_only=True)
    location_info = LocationInfoSerializer(source='location', read_only=True)
    
    # These fields are for write operations to maintain API compatibility
    device_id = serializers.CharField(write_only=True)
    app_version = serializers.CharField(write_only=True)
    os_name = serializers.CharField(write_only=True)
    os_version = serializers.CharField(write_only=True)
    is_simulator = serializers.BooleanField(required=False, write_only=True)
    is_rooted_device = serializers.BooleanField(required=False, write_only=True)
    is_vpn_enabled = serializers.BooleanField(required=False, write_only=True)
    ip_address = serializers.IPAddressField(required=False, write_only=True)
    city = serializers.CharField(required=False, write_only=True)
    country = serializers.CharField(required=False, write_only=True)
    continent = serializers.CharField(required=False, write_only=True)
    
    class Meta:
        model = Event
        fields = [
            'id', 'distinct_id', 'event_type', 'properties', 
            'timestamp', 'latitude', 'longitude', 'app_check_result',
            # Write-only fields for backward compatibility
            'device_id', 'app_version', 'os_name', 'os_version',
            'is_simulator', 'is_rooted_device', 'is_vpn_enabled',
            'ip_address', 'city', 'country', 'continent',
            # Nested relationships
            'device_info', 'location_info', 'session'
        ]
        read_only_fields = ['id', 'created_at', 'processed', 'device_info', 'location_info']
    
    def create(self, validated_data):
        # Get the client IP from the request if available
        request = self.context.get('request')
        if request and not validated_data.get('ip_address'):
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                validated_data['ip_address'] = x_forwarded_for.split(',')[0]
            else:
                validated_data['ip_address'] = request.META.get('REMOTE_ADDR')
        
        # Use our utility function to create the event
        return create_event(validated_data)


class BatchEventSerializer(serializers.Serializer):
    """
    Serializer for batch event uploads.
    """
    batch = serializers.ListField(
        child=EventSerializer(),
        min_length=1,
        max_length=1000
    )
    
    def create(self, validated_data):
        events = []
        for event_data in validated_data['batch']:
            # Process each event in the batch using our utility
            event = create_event(event_data)
            events.append(event)
        
        return {'events': events}


class SessionSerializer(serializers.ModelSerializer):
    """
    Serializer for session data.
    """
    # Include the complete nested device and location data
    device_info = DeviceInfoSerializer(source='device', read_only=True)
    location_info = LocationInfoSerializer(source='location', read_only=True)
    
    # These fields are for write operations to maintain API compatibility
    device_id = serializers.CharField(write_only=True)
    app_version = serializers.CharField(write_only=True)
    os_name = serializers.CharField(write_only=True)
    os_version = serializers.CharField(write_only=True)
    is_simulator = serializers.BooleanField(required=False, write_only=True)
    is_rooted_device = serializers.BooleanField(required=False, write_only=True)
    is_vpn_enabled = serializers.BooleanField(required=False, write_only=True)
    ip_address = serializers.IPAddressField(required=False, write_only=True)
    city = serializers.CharField(required=False, write_only=True)
    country = serializers.CharField(required=False, write_only=True)
    continent = serializers.CharField(required=False, write_only=True)
    
    class Meta:
        model = Session
        fields = [
            'id', 'distinct_id', 'start_time', 'end_time', 
            'duration', 'events_count', 'latitude', 'longitude', 
            'app_check_result',
            # Write-only fields for backward compatibility
            'device_id', 'app_version', 'os_name', 'os_version',
            'is_simulator', 'is_rooted_device', 'is_vpn_enabled',
            'ip_address', 'city', 'country', 'continent',
            # Nested relationships
            'device_info', 'location_info'
        ]
        read_only_fields = ['id', 'duration', 'events_count', 'device_info', 'location_info']
    
    def create(self, validated_data):
        # Get the client IP from the request if available
        request = self.context.get('request')
        if request and not validated_data.get('ip_address'):
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                validated_data['ip_address'] = x_forwarded_for.split(',')[0]
            else:
                validated_data['ip_address'] = request.META.get('REMOTE_ADDR')
        
        # Use our utility function to create the session
        return create_session(validated_data)


class FeatureFlagSerializer(serializers.ModelSerializer):
    """
    Serializer for feature flags.
    """
    class Meta:
        model = FeatureFlag
        fields = [
            'id', 'name', 'key', 'description', 
            'active', 'rollout_percentage', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class EventAggregateSerializer(serializers.ModelSerializer):
    """
    Serializer for aggregated event data.
    """
    class Meta:
        model = EventAggregate
        fields = [
            'id', 'event_type', 'date', 'hour',
            'count', 'unique_users', 'properties'
        ]
        read_only_fields = ['id'] 