from rest_framework import serializers
from .models import Event, Session, FeatureFlag, EventAggregate


class EventSerializer(serializers.ModelSerializer):
    """
    Serializer for individual events.
    """
    class Meta:
        model = Event
        fields = [
            'id', 'distinct_id', 'event_type', 'properties', 
            'timestamp', 'device_id', 'app_version', 
            'os_name', 'os_version', 'ip_address',
            'is_simulator', 'is_rooted_device', 'is_vpn_enabled',
            'latitude', 'longitude', 'city', 'country', 'continent',
            'app_check_result'
        ]
        read_only_fields = ['id', 'created_at', 'processed']
    
    def create(self, validated_data):
        # Get the client IP from the request if available
        request = self.context.get('request')
        if request and not validated_data.get('ip_address'):
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                validated_data['ip_address'] = x_forwarded_for.split(',')[0]
            else:
                validated_data['ip_address'] = request.META.get('REMOTE_ADDR')
        
        return super().create(validated_data)


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
            # Process each event in the batch
            event = Event.objects.create(**event_data)
            events.append(event)
        
        return {'events': events}


class SessionSerializer(serializers.ModelSerializer):
    """
    Serializer for session data.
    """
    class Meta:
        model = Session
        fields = [
            'id', 'distinct_id', 'device_id', 'start_time',
            'end_time', 'duration', 'events_count', 
            'app_version', 'os_name', 'os_version',
            'is_simulator', 'is_rooted_device', 'is_vpn_enabled',
            'latitude', 'longitude', 'ip_address', 
            'city', 'country', 'continent', 'app_check_result'
        ]
        read_only_fields = ['id', 'duration', 'events_count']


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