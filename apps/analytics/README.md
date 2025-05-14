# Event Tracking System

This Django app provides a scalable event tracking system similar to PostHog for mobile applications. It allows you to capture, store, and analyze events from mobile apps, track user sessions, and implement feature flags.

## Features

- Event capture API with single and batch endpoints
- Session tracking
- Feature flags for A/B testing
- Event aggregation for faster analytics
- Admin dashboard for viewing events and analytics
- Asynchronous processing with Celery

## API Endpoints

### Public Endpoints (No Authentication Required)

#### Event Capture

- `POST /api/v1/analytics/capture/` - Capture a single event
- `POST /api/v1/analytics/batch/` - Capture multiple events at once
- `POST /api/v1/analytics/session/start/` - Start a new session
- `PUT /api/v1/analytics/session/{session_id}/end/` - End an existing session

#### Feature Flags

- `GET /api/v1/analytics/public/feature-flags/` - List all active feature flags
- `GET /api/v1/analytics/public/feature-flags/{id}/` - Get a specific feature flag
- `GET /api/v1/analytics/public/feature-flags/for_user/?distinct_id={distinct_id}` - Get feature flags for a specific user

### Admin Endpoints (Authentication Required)

- `GET /api/v1/analytics/admin/events/` - List all events
- `GET /api/v1/analytics/admin/events/event_counts/` - Get event counts by type
- `GET /api/v1/analytics/admin/sessions/` - List all sessions
- `GET /api/v1/analytics/admin/feature-flags/` - Manage feature flags
- `GET /api/v1/analytics/admin/event-aggregates/` - View aggregated event data

## Event Structure

A typical event should include:

```json
{
  "distinct_id": "user123",
  "event_type": "button_click",
  "properties": {
    "button_name": "submit",
    "page": "checkout"
  },
  "device_id": "device456",
  "app_version": "1.0.0",
  "os_name": "iOS",
  "os_version": "15.0",
  "timestamp": "2023-04-13T12:34:56Z"
}
```

## Batch Event Structure

For sending multiple events at once:

```json
{
  "events": [
    {
      "distinct_id": "user123",
      "event_type": "button_click",
      "properties": { "button_name": "submit" },
      "device_id": "device456",
      "app_version": "1.0.0",
      "os_name": "iOS",
      "os_version": "15.0"
    },
    {
      "distinct_id": "user123",
      "event_type": "page_view",
      "properties": { "page": "checkout" },
      "device_id": "device456",
      "app_version": "1.0.0",
      "os_name": "iOS",
      "os_version": "15.0"
    }
  ]
}
```

## Feature Flag Usage

Feature flags can be used to control feature rollout or for A/B testing. To check if a feature is enabled for a user:

```python
# Client-side code (example)
feature_flags = api.get_feature_flags(distinct_id="user123")
if feature_flags.get("new_checkout_flow", {}).get("active", False):
    # Show the new checkout flow
else:
    # Show the old checkout flow
```

## Scheduled Tasks

The system runs several scheduled tasks:

- Close inactive sessions (every 10 minutes)
- Aggregate daily event data (1:00 AM daily)
- Aggregate hourly event data (5 minutes past every hour)

## Scaling Considerations

The system is designed to scale to millions of users with:

- Database partitioning for events by date
- Redis for buffering events during traffic spikes
- Celery for asynchronous processing
- Pre-computed aggregates for fast dashboard loading

## Implementation Roadmap

1. **High Priority**
   - Implement table partitioning for events
   - Add indexes for common queries
   - Set up data retention policies

2. **Medium Priority**
   - Implement ClickHouse for analytics queries
   - Add more dashboard visualizations
   - Develop funnel analysis features

3. **Future Enhancements**
   - Real-time event streaming
   - Machine learning for user behavior analysis
   - Advanced segmentation capabilities
   - Custom event property indexing 