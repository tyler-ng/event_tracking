# Event Tracking Schema

This document outlines the event tracking schema used in our analytics system and provides guidelines for structuring events.

## Core Concepts

### Events

An event represents a single user action or system occurrence. Every event has a type, properties, and contextual metadata.

### Sessions

A session represents a continuous period of user engagement with the application. Sessions have a start time, end time, and are associated with multiple events.

### Users

Users can be anonymous (identified only by a `distinct_id`) or identified (linked to a user account).

## Event Structure

Each event has the following structure:

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
  "timestamp": "2023-04-13T12:34:56Z",
  "ip_address": "203.0.113.42"
}
```

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `distinct_id` | String | Unique identifier for the user |
| `event_type` | String | Type of the event (e.g., `page_view`, `button_click`) |
| `device_id` | String | Unique identifier for the device |
| `app_version` | String | Version of the application |
| `os_name` | String | Operating system name (e.g., `iOS`, `Android`) |
| `os_version` | String | Operating system version |

### Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `properties` | Object | Additional properties specific to the event |
| `timestamp` | String (ISO 8601) | When the event occurred (defaults to server time) |
| `ip_address` | String | IP address of the client (automatically captured if not provided) |

## Session Structure

Sessions have the following structure:

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "distinct_id": "user123",
  "device_id": "device456",
  "start_time": "2023-04-13T12:34:56Z",
  "end_time": "2023-04-13T12:45:23Z",
  "duration": "00:10:27",
  "events_count": 15,
  "app_version": "1.0.0",
  "os_name": "iOS",
  "os_version": "15.0"
}
```

## Event Naming Conventions

Use consistent naming patterns for events to make analysis easier. We recommend:

1. Use lowercase with underscores as separators (`page_view`, not `PageView` or `page-view`)
2. Start with a noun or verb that describes the action
3. Use prefixes for categorization (e.g., `auth_login`, `product_view`, `checkout_complete`)

## Standard Event Types

We recommend using these standard event types when applicable:

### Screen/Page Views

```json
{
  "event_type": "screen_view",
  "properties": {
    "screen_name": "Product Details",
    "screen_id": "product_details",
    "referrer": "search_results"
  }
}
```

### User Authentication

```json
{
  "event_type": "user_login",
  "properties": {
    "method": "email",
    "success": true
  }
}

{
  "event_type": "user_logout",
  "properties": {}
}

{
  "event_type": "user_signup",
  "properties": {
    "method": "google",
    "success": true
  }
}
```

### E-Commerce Events

```json
{
  "event_type": "product_view",
  "properties": {
    "product_id": "12345",
    "product_name": "Wireless Headphones",
    "category": "Electronics",
    "price": 99.99,
    "currency": "USD"
  }
}

{
  "event_type": "add_to_cart",
  "properties": {
    "product_id": "12345",
    "product_name": "Wireless Headphones",
    "category": "Electronics",
    "price": 99.99,
    "currency": "USD",
    "quantity": 1
  }
}

{
  "event_type": "checkout_start",
  "properties": {
    "cart_value": 99.99,
    "items_count": 1,
    "currency": "USD"
  }
}

{
  "event_type": "purchase",
  "properties": {
    "order_id": "ORD-12345",
    "value": 99.99,
    "currency": "USD",
    "payment_method": "credit_card",
    "items": [
      {
        "product_id": "12345",
        "product_name": "Wireless Headphones",
        "category": "Electronics",
        "price": 99.99,
        "quantity": 1
      }
    ]
  }
}
```

### User Engagement

```json
{
  "event_type": "button_click",
  "properties": {
    "button_id": "submit_button",
    "button_text": "Submit",
    "page": "checkout"
  }
}

{
  "event_type": "search",
  "properties": {
    "query": "wireless headphones",
    "results_count": 15,
    "category": "Electronics"
  }
}

{
  "event_type": "video_play",
  "properties": {
    "video_id": "vid-12345",
    "video_title": "Product Demo",
    "duration": 120,
    "position": 0
  }
}

{
  "event_type": "video_complete",
  "properties": {
    "video_id": "vid-12345",
    "video_title": "Product Demo",
    "duration": 120,
    "watched_percentage": 100
  }
}
```

## Property Value Types

Use consistent data types for property values:

- **Strings**: For textual data and identifiers
- **Numbers**: For measurements, counts, and currency values
- **Booleans**: For binary states (true/false)
- **Arrays**: For lists of items
- **Objects**: For nested structured data

## Property Naming Conventions

1. Use lowercase with underscores as separators
2. Be descriptive but concise
3. Use consistent naming across similar events
4. Avoid abbreviations unless well-known (e.g., `user_id` not `uid`)

## Guidelines for Custom Events

When creating custom events:

1. **Be Specific**: Name events to reflect specific actions rather than general categories
2. **Context Matters**: Include relevant contextual properties that help analyze the event later
3. **Avoid Redundancy**: Don't repeat information that's already captured in the standard fields
4. **Consider Analysis**: Think about how you'll want to analyze the data later

## Common Anti-Patterns to Avoid

1. **Overly Generic Events**: Avoid event types like `user_action` that don't provide specific meaning
2. **Inconsistent Naming**: Don't mix naming conventions (e.g., `button_click` and `formSubmit`)
3. **Sensitive Data**: Never include personally identifiable information (PII) like passwords, credit card numbers, etc.
4. **High Cardinality Properties**: Avoid properties with thousands of possible values
5. **Transient IDs**: Don't use session IDs or other transient values as event properties
6. **Massive Events**: Keep events reasonably sized (< 100KB)

## Analytics-Friendly Event Design

Design events with analytics in mind:

1. **Atomic Actions**: Track individual, specific actions rather than bundles of actions
2. **Complete Context**: Include enough context to understand the event without needing to join with other data
3. **Hierarchical Organization**: Use consistent prefixes for related events
4. **Forward Compatibility**: Design your schema to accommodate future extensions

## Example Event Timeline

Here's an example of how events should be captured for a typical e-commerce flow:

1. `screen_view` (Home)
2. `search` (Query: "headphones")
3. `screen_view` (Search Results)
4. `product_view` (Wireless Headphones)
5. `add_to_cart` (Wireless Headphones)
6. `screen_view` (Cart)
7. `checkout_start`
8. `screen_view` (Checkout Address)
9. `checkout_address_submit`
10. `screen_view` (Checkout Payment)
11. `checkout_payment_submit`
12. `purchase`
13. `screen_view` (Order Confirmation)

## Platform-Specific Considerations

### Mobile Apps

- Track app lifecycle events (`app_installed`, `app_updated`, `app_opened`, `app_backgrounded`)
- Include mobile-specific properties like `screen_orientation`, `network_type`, `battery_level` where relevant

### Web Applications

- Include browser information (`browser_name`, `browser_version`)
- Track page load performance (`page_load_time`, `dom_ready_time`)

## Backward Compatibility

When evolving your event schema:

1. Never remove properties from existing events
2. Add new properties with sensible defaults
3. Create new event types rather than changing the meaning of existing ones
4. Version your events if making significant changes

## How Events are Processed

Events go through the following pipeline:

1. **Capture**: Client SDK sends event to the API
2. **Validation**: Server validates event structure
3. **Enrichment**: Additional data may be added (e.g., geolocation from IP)
4. **Storage**: Event is stored in the database
5. **Processing**: Background jobs process events for aggregation and analysis
6. **Analysis**: Events are analyzed in aggregate for dashboards and reports

## Tips for Effective Event Tracking

1. **Track the Minimum Needed**: Only track events that provide analytical value
2. **Be Consistent**: Use consistent naming conventions across your organization
3. **Document Your Schema**: Maintain documentation of your event schema
4. **Test Your Implementation**: Validate that events are being captured as expected
5. **Respect Privacy**: Only track what's needed and respect user privacy preferences
6. **Consider Volume**: Be aware of the volume of events generated and potential costs

## Sample Event Tracking Plan

To help plan your event tracking strategy, create a document with the following columns:

| Event Type | Description | Properties | Trigger | Platform |
|------------|-------------|------------|---------|----------|
| `screen_view` | User views a screen | `screen_name`, `referrer` | When screen appears | All |
| `product_view` | User views product details | `product_id`, `product_name`, `price` | When product page loads | All |
| ... | ... | ... | ... | ... |

This ensures consistent implementation across your team. 