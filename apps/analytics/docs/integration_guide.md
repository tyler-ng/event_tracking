# Mobile SDK Integration Guide

This guide provides instructions for integrating our event tracking system into your mobile applications. The system allows you to track user events, manage sessions, and implement feature flags for A/B testing.

## Installation

### iOS Integration

#### CocoaPods

Add the SDK to your Podfile:

```ruby
pod 'EventTracker', '~> 1.0'
```

Run `pod install` to install the SDK.

#### Swift Package Manager

Add the following dependency to your Package.swift file:

```swift
dependencies: [
    .package(url: "https://github.com/example/event-tracker-ios.git", .upToNextMajor(from: "1.0.0"))
]
```

### Android Integration

#### Gradle

Add the following to your app's build.gradle file:

```groovy
dependencies {
    implementation 'com.example:event-tracker:1.0.0'
}
```

## Initialization

### iOS (Swift)

```swift
import EventTracker

func application(_ application: UIApplication, didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {
    // Initialize the tracker with your API endpoint
    EventTracker.initialize(apiUrl: "https://api.example.com/api/v1/analytics/")
    
    // Set a distinct ID for the user (could be a UUID for anonymous users)
    EventTracker.shared.setDistinctId("user123")
    
    // Start a new session when the app launches
    EventTracker.shared.startSession()
    
    // Load feature flags
    EventTracker.shared.loadFeatureFlags()
    
    return true
}
```

### Android (Kotlin)

```kotlin
import com.example.eventtracker.EventTracker

class MyApplication : Application() {
    override fun onCreate() {
        super.onCreate()
        
        // Initialize the tracker with your API endpoint
        EventTracker.initialize(this, "https://api.example.com/api/v1/analytics/")
        
        // Set a distinct ID for the user
        EventTracker.getInstance().setDistinctId("user123")
        
        // Start a new session when the app launches
        EventTracker.getInstance().startSession()
        
        // Load feature flags
        EventTracker.getInstance().loadFeatureFlags()
    }
}
```

## Tracking Events

### iOS (Swift)

```swift
// Track a simple event
EventTracker.shared.track(
    eventType: "button_click", 
    properties: ["button_name": "submit", "page": "checkout"]
)

// Track an event with a custom timestamp
let timestamp = ISO8601DateFormatter().date(from: "2023-04-13T12:34:56Z")!
EventTracker.shared.track(
    eventType: "page_view",
    properties: ["page": "home"],
    timestamp: timestamp
)
```

### Android (Kotlin)

```kotlin
// Track a simple event
EventTracker.getInstance().track(
    eventType = "button_click",
    properties = mapOf("button_name" to "submit", "page" to "checkout")
)

// Track an event with a custom timestamp
val sdf = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss'Z'", Locale.US)
val timestamp = sdf.parse("2023-04-13T12:34:56Z")
EventTracker.getInstance().track(
    eventType = "page_view",
    properties = mapOf("page" to "home"),
    timestamp = timestamp
)
```

## Session Management

Sessions are automatically managed by the SDK. A session starts when the app is opened and ends when the app goes to the background.

### iOS (Swift)

```swift
// In AppDelegate.swift
func applicationDidEnterBackground(_ application: UIApplication) {
    EventTracker.shared.endSession()
}

func applicationWillEnterForeground(_ application: UIApplication) {
    EventTracker.shared.startSession()
}
```

### Android (Kotlin)

```kotlin
// In your main activity or base activity
override fun onPause() {
    super.onPause()
    EventTracker.getInstance().endSession()
}

override fun onResume() {
    super.onResume()
    EventTracker.getInstance().startSession()
}
```

## Using Feature Flags

Feature flags allow you to toggle features on and off for specific users.

### iOS (Swift)

```swift
// Check if a feature is enabled
if EventTracker.shared.isFeatureEnabled("new_checkout_flow") {
    // Show the new checkout flow
} else {
    // Show the old checkout flow
}

// Get all feature flags
let featureFlags = EventTracker.shared.getFeatureFlags()
```

### Android (Kotlin)

```kotlin
// Check if a feature is enabled
if (EventTracker.getInstance().isFeatureEnabled("new_checkout_flow")) {
    // Show the new checkout flow
} else {
    // Show the old checkout flow
}

// Get all feature flags
val featureFlags = EventTracker.getInstance().getFeatureFlags()
```

## Identifying Users

When a user logs in, you can associate their events with their user ID.

### iOS (Swift)

```swift
// When a user logs in
func userDidLogin(userId: String) {
    // Update the distinct ID to the user's ID
    EventTracker.shared.setDistinctId(userId)
    
    // Track the login event
    EventTracker.shared.track(
        eventType: "user_login",
        properties: ["method": "email"]
    )
}
```

### Android (Kotlin)

```kotlin
// When a user logs in
fun userDidLogin(userId: String) {
    // Update the distinct ID to the user's ID
    EventTracker.getInstance().setDistinctId(userId)
    
    // Track the login event
    EventTracker.getInstance().track(
        eventType = "user_login",
        properties = mapOf("method" to "email")
    )
}
```

## Batch Uploading

The SDK automatically batches events to minimize network requests. By default, events are uploaded when:

1. The batch size reaches 20 events
2. The app goes to the background
3. A session ends

You can also manually flush events:

### iOS (Swift)

```swift
// Manually flush events
EventTracker.shared.flush()
```

### Android (Kotlin)

```kotlin
// Manually flush events
EventTracker.getInstance().flush()
```

## Offline Support

The SDK automatically stores events locally when the device is offline and uploads them when the connection is restored.

## Advanced Configuration

### iOS (Swift)

```swift
// Configure the SDK with custom options
EventTracker.initialize(
    apiUrl: "https://api.example.com/api/v1/analytics/",
    options: EventTrackerOptions(
        batchSize: 10,
        flushInterval: 30,
        maxQueueSize: 1000,
        enableLogging: true
    )
)
```

### Android (Kotlin)

```kotlin
// Configure the SDK with custom options
EventTracker.initialize(
    context = applicationContext,
    apiUrl = "https://api.example.com/api/v1/analytics/",
    options = EventTrackerOptions(
        batchSize = 10,
        flushInterval = 30,
        maxQueueSize = 1000,
        enableLogging = true
    )
)
```

## Debugging

### iOS (Swift)

```swift
// Enable debug logging
EventTracker.setLogLevel(.debug)
```

### Android (Kotlin)

```kotlin
// Enable debug logging
EventTracker.setLogLevel(LogLevel.DEBUG)
```

## Error Handling

The SDK handles network errors and retries failed requests automatically. You can listen for errors:

### iOS (Swift)

```swift
EventTracker.shared.onError = { error in
    print("Event tracking error: \(error)")
}
```

### Android (Kotlin)

```kotlin
EventTracker.getInstance().setErrorListener { error ->
    Log.e("EventTracker", "Event tracking error: $error")
}
```

## Privacy Compliance

To help with privacy regulations like GDPR and CCPA:

### iOS (Swift)

```swift
// Opt out of tracking
EventTracker.shared.optOut()

// Opt back in
EventTracker.shared.optIn()

// Clear stored data for a user
EventTracker.shared.clearUserData(userId: "user123")
```

### Android (Kotlin)

```kotlin
// Opt out of tracking
EventTracker.getInstance().optOut()

// Opt back in
EventTracker.getInstance().optIn()

// Clear stored data for a user
EventTracker.getInstance().clearUserData(userId = "user123")
```

## Best Practices

1. **Initialize Early**: Initialize the tracker in your `Application` class or `AppDelegate`.
2. **Consistent IDs**: Use consistent distinct IDs across sessions to track user behavior accurately.
3. **Descriptive Event Names**: Use clear, descriptive event names that follow a consistent pattern.
4. **Structured Properties**: Keep property names and values consistent.
5. **Minimize Custom Timestamps**: Let the SDK handle timestamps when possible.
6. **Handle App Lifecycle**: Always start and end sessions with app lifecycle events.
7. **Cache Feature Flags**: Reduce API calls by caching feature flags.
8. **Regular Updates**: Keep the SDK updated to benefit from performance improvements and bug fixes.

## Sample Projects

For complete working examples, see:

- [iOS Sample App](https://github.com/example/event-tracker-ios-sample)
- [Android Sample App](https://github.com/example/event-tracker-android-sample)

## Additional Resources

- [API Documentation](./mobile_api.md)
- [Troubleshooting Guide](./troubleshooting.md)
- [SDK Reference](https://docs.example.com/event-tracker-sdk)
- [Changelog](./changelog.md) 