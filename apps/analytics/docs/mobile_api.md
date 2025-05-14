# Mobile Client API Documentation

This document provides detailed information about the API endpoints available for mobile client integration with our event tracking system.

## Base URL

All API endpoints are relative to:

```
https://api.example.com/api/v1/analytics/
```

## Authentication

Most endpoints are public and do not require authentication. This is designed for easy integration with mobile clients.

## Event Tracking Endpoints

### 1. Capture a Single Event

Sends a single event to the tracking system.

**Endpoint**: `POST /capture/`

**Request Body**:
```json
{
  "distinct_id": "fir-8dac3",
  "event_type": "button_click",
  "properties": {
    "button_name": "submit",
    "page": "checkout"
  },
  "device_id": "device456",
  "app_version": "1.0.0",
  "os_name": "iOS",
  "os_version": "15.0",
  "timestamp": "2023-04-13T12:34:56Z",
  "is_simulator": false,
  "is_rooted_device": false,
  "is_vpn_enabled": false,
  "latitude": 37.7749,
  "longitude": -122.4194,
  "ip_address": "203.0.113.42",
  "city": "San Francisco",
  "country": "United States",
  "continent": "North America",
  "app_check_result": true
}
```

**Required Fields**:
- `distinct_id`: Firebase ID for the user. Use the Firebase UID for authenticated users
- `event_type`: String describing the event
- `device_id`: Unique identifier for the device
- `app_version`: Version of the mobile app
- `os_name`: Operating system name (iOS, Android, etc.)
- `os_version`: Operating system version

**Optional Fields**:
- `properties`: JSON object with additional properties specific to the event
- `timestamp`: ISO 8601 formatted date-time (defaults to server time if not provided)
- `is_simulator`: Boolean indicating if the app is running on a simulator/emulator
- `is_rooted_device`: Boolean indicating if the device is rooted/jailbroken
- `is_vpn_enabled`: Boolean indicating if a VPN is currently active
- `latitude`: Decimal latitude of the device (if location permissions granted)
- `longitude`: Decimal longitude of the device (if location permissions granted)
- `ip_address`: Device's IP address (automatically captured if not provided)
- `city`: City name based on IP geolocation
- `country`: Country name based on IP geolocation
- `continent`: Continent name based on IP geolocation
- `app_check_result`: Boolean indicating the result of Firebase App Check verification

**Response**: `202 Accepted`
```json
{
  "status": "success"
}
```

### 2. Batch Event Capture

Sends multiple events in a single request to minimize network overhead.

**Endpoint**: `POST /batch/`

**Request Body**:
```json
{
  "batch": [
    {
      "distinct_id": "fir-8dac3",
      "event_type": "page_view",
      "properties": {
        "page": "home"
      },
      "device_id": "device456",
      "app_version": "1.0.0",
      "os_name": "iOS",
      "os_version": "15.0",
      "is_simulator": false,
      "is_rooted_device": false,
      "is_vpn_enabled": false,
      "latitude": 37.7749,
      "longitude": -122.4194,
      "ip_address": "203.0.113.42",
      "city": "San Francisco",
      "country": "United States",
      "continent": "North America",
      "app_check_result": true
    },
    {
      "distinct_id": "fir-8dac3",
      "event_type": "button_click",
      "properties": {
        "button_name": "add_to_cart"
      },
      "device_id": "device456",
      "app_version": "1.0.0",
      "os_name": "iOS",
      "os_version": "15.0",
      "is_simulator": false,
      "is_rooted_device": false,
      "is_vpn_enabled": false,
      "latitude": 37.7749,
      "longitude": -122.4194,
      "ip_address": "203.0.113.42",
      "city": "San Francisco",
      "country": "United States",
      "continent": "North America"
    }
  ]
}
```

**Response**: `202 Accepted`
```json
{
  "status": "success",
  "event_count": 2
}
```

## Session Management

### 1. Start a Session

Begins a new tracking session for a user.

**Endpoint**: `POST /session/start/`

**Request Body**:
```json
{
  "distinct_id": "fir-8dac3",
  "device_id": "device456",
  "app_version": "1.0.0",
  "os_name": "iOS",
  "os_version": "15.0",
  "is_simulator": false,
  "is_rooted_device": false,
  "is_vpn_enabled": false,
  "latitude": 37.7749,
  "longitude": -122.4194,
  "ip_address": "203.0.113.42",
  "city": "San Francisco",
  "country": "United States",
  "continent": "North America",
  "app_check_result": true
}
```

**Response**: `201 Created`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "distinct_id": "fir-8dac3",
  "device_id": "device456",
  "start_time": "2023-04-13T12:34:56Z",
  "end_time": null,
  "duration": null,
  "events_count": 0,
  "app_version": "1.0.0",
  "os_name": "iOS",
  "os_version": "15.0",
  "is_simulator": false,
  "is_rooted_device": false,
  "is_vpn_enabled": false,
  "latitude": 37.7749,
  "longitude": -122.4194,
  "ip_address": "203.0.113.42",
  "city": "San Francisco",
  "country": "United States",
  "continent": "North America",
  "app_check_result": true
}
```

### 2. End a Session

Ends an existing session.

**Endpoint**: `PUT /session/{session_id}/end/`

**Path Parameters**:
- `session_id`: UUID of the session to end

**Response**: `200 OK`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "distinct_id": "fir-8dac3",
  "device_id": "device456",
  "start_time": "2023-04-13T12:34:56Z",
  "end_time": "2023-04-13T12:45:23Z",
  "duration": "00:10:27",
  "events_count": 15,
  "app_version": "1.0.0",
  "os_name": "iOS",
  "os_version": "15.0",
  "is_simulator": false,
  "is_rooted_device": false,
  "is_vpn_enabled": false,
  "latitude": 37.7749,
  "longitude": -122.4194,
  "ip_address": "203.0.113.42",
  "city": "San Francisco",
  "country": "United States",
  "continent": "North America",
  "app_check_result": true
}
```

## Error Responses

The API returns standard HTTP status codes:

- `400 Bad Request`: Validation errors in request data
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server-side error

Error response format:
```json
{
  "error": "Error message details"
}
```

## Best Practices

1. **Batch Events**: When possible, use the batch endpoint to send multiple events at once.
2. **Session Management**: Always start a session when your app is opened and end it when the app goes to the background.
3. **Firebase ID**: Use the Firebase UID for authenticated users to ensure consistent user tracking.
4. **Device Information**: Collect device information only with appropriate user consent, especially for location data.
5. **Error Handling**: Implement robust error handling and retry logic for failed API calls.
6. **Privacy Considerations**: Ensure your app has the necessary permissions and privacy policy disclosures for collecting geolocation and device data.

## Rate Limits

To ensure system stability, the following rate limits apply:

- Single Event Capture: 100 requests per minute per IP
- Batch Event Capture: 20 requests per minute per IP (max 1000 events per batch) 