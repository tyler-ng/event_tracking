from django.utils import timezone
from .models import Event, Session, DeviceInfo, LocationInfo
from django.db import models


def get_or_create_device_info(device_data):
    """
    Get or create a DeviceInfo instance based on provided data.
    
    Args:
        device_data (dict): Dictionary containing device information.
            Required keys: device_id
            Optional keys: app_version, os_name, os_version, 
                           is_simulator, is_rooted_device, is_vpn_enabled
                        
    Returns:
        DeviceInfo: The retrieved or created DeviceInfo instance
    """
    if not device_data or 'device_id' not in device_data:
        return None
        
    # Extract required fields
    device_id = device_data.pop('device_id')
    
    # Set defaults for missing fields
    defaults = {
        'app_version': '',
        'os_name': '',
        'os_version': '',
    }
    
    # Update defaults with provided values
    defaults.update(device_data)
    
    # Get or create device
    device, _ = DeviceInfo.objects.get_or_create(
        device_id=device_id,
        defaults=defaults
    )
    
    return device


def get_or_create_location_info(location_data):
    """
    Get or create a LocationInfo instance based on provided data.
    
    Args:
        location_data (dict): Dictionary containing location information.
            Required keys: ip_address
            Optional keys: city, country, continent
                        
    Returns:
        LocationInfo: The retrieved or created LocationInfo instance, or None if no ip_address
    """
    if not location_data or 'ip_address' not in location_data:
        return None
        
    # Extract required fields
    ip_address = location_data.pop('ip_address')
    
    if not ip_address:
        return None
    
    # Get or create location
    location, _ = LocationInfo.objects.get_or_create(
        ip_address=ip_address,
        defaults=location_data
    )
    
    return location


def find_active_session(distinct_id, device_id, timestamp=None):
    """
    Find an active session for the given user and device.
    
    Args:
        distinct_id (str): User identifier
        device_id (str): Device identifier
        timestamp (datetime, optional): Event timestamp to check against. Defaults to current time.
        
    Returns:
        Session or None: Active session if found, None otherwise
    """
    if timestamp is None:
        timestamp = timezone.now()
    
    # Find session based on distinct_id and device_id where event time falls within session
    try:
        device = DeviceInfo.objects.get(device_id=device_id)
        session = Session.objects.filter(
            distinct_id=distinct_id,
            device=device,
            start_time__lte=timestamp,
        ).filter(
            # Either session has no end time or event timestamp is before session end
            models.Q(end_time__isnull=True) | models.Q(end_time__gte=timestamp)
        ).order_by('-start_time').first()
        
        return session
    except DeviceInfo.DoesNotExist:
        return None


def create_event(event_data):
    """
    Create an event with proper normalization of device and location data.
    
    Args:
        event_data (dict): Dictionary containing event data.
            Required keys: distinct_id, event_type
            Optional device keys: device_id, app_version, os_name, os_version,
                                  is_simulator, is_rooted_device, is_vpn_enabled
            Optional location keys: ip_address, city, country, continent
            Other data: Any other event-specific data
            
    Returns:
        Event: The created event instance
    """
    # Extract device data from event data
    device_data = {}
    for field in ['device_id', 'app_version', 'os_name', 'os_version', 
                  'is_simulator', 'is_rooted_device', 'is_vpn_enabled']:
        if field in event_data:
            device_data[field] = event_data.pop(field)
            
    # Extract location data from event data
    location_data = {}
    for field in ['ip_address', 'city', 'country', 'continent']:
        if field in event_data:
            location_data[field] = event_data.pop(field)
            
    # Get or create device and location records
    device = get_or_create_device_info(device_data)
    location = get_or_create_location_info(location_data)
    
    # Check if there's an active session we can associate this event with
    session = None
    if device and 'distinct_id' in event_data:
        session = find_active_session(
            event_data['distinct_id'], 
            device.device_id,
            event_data.get('timestamp', timezone.now())
        )
    
    # Create the event
    event = Event.objects.create(
        device=device,
        location=location,
        session=session,
        **event_data
    )
    
    # Update event count on session if we found one
    if session:
        session.events_count = session.events_count + 1
        session.save(update_fields=['events_count'])
    
    return event


def create_session(session_data):
    """
    Create a session with proper normalization of device and location data.
    
    Args:
        session_data (dict): Dictionary containing session data.
            Required keys: distinct_id, start_time
            Optional device keys: device_id, app_version, os_name, os_version,
                                 is_simulator, is_rooted_device, is_vpn_enabled
            Optional location keys: ip_address, city, country, continent
            Other data: Any other session-specific data
            
    Returns:
        Session: The created session instance
    """
    # Extract device data from session data
    device_data = {}
    for field in ['device_id', 'app_version', 'os_name', 'os_version', 
                  'is_simulator', 'is_rooted_device', 'is_vpn_enabled']:
        if field in session_data:
            device_data[field] = session_data.pop(field)
            
    # Extract location data from session data
    location_data = {}
    for field in ['ip_address', 'city', 'country', 'continent']:
        if field in session_data:
            location_data[field] = session_data.pop(field)
            
    # Get or create device and location records
    device = get_or_create_device_info(device_data)
    location = get_or_create_location_info(location_data)
    
    # Create the session
    session = Session.objects.create(
        device=device,
        location=location,
        **session_data
    )
    
    return session 