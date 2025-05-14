# Django Event Tracking System

A scalable Django-based event tracking system for mobile applications, similar to PostHog. This project provides a complete backend for capturing, storing, and analyzing user events from mobile apps.

## Features

- **Event Tracking**: Capture events from mobile applications
- **Session Management**: Track user sessions and behaviors
- **Feature Flags**: Implement A/B testing and feature rollouts
- **Analytics Dashboard**: View and analyze event data
- **Optimized Data Storage**: Normalized device and location data to reduce redundancy
- **Docker-based**: Full containerization for consistent development and deployment
- **PostgreSQL Database**: Robust data storage with PostgreSQL
- **Redis & Celery**: Background task processing and caching
- **Horizontal Scaling**: Designed to scale to millions of users

## Architecture

The system is built with a modern, scalable architecture:

- **Django REST Framework**: API endpoints for mobile clients
- **PostgreSQL**: Primary data storage with normalized data models
- **Redis**: Event buffering and caching
- **Celery**: Asynchronous task processing
- **Nginx**: Load balancing and reverse proxy

### Data Models

We use a normalized data structure to reduce storage requirements and improve query performance:

- **DeviceInfo**: Stores device-specific data (OS, version, etc.) that rarely changes
- **LocationInfo**: Stores IP-based location data (city, country, etc.)
- **Event**: References DeviceInfo and LocationInfo to avoid redundancy
- **Session**: Groups related events and references the same device and location information

## Running Locally with Docker

### Prerequisites

- Docker Engine (20.10.x or higher)
- Docker Compose (v2.x or higher)

### Setup and Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/data-tracking.git
   cd data-tracking
   ```

2. Create a `.env` file in the project root with the following environment variables:
   ```
   DEBUG=1
   SECRET_KEY=django-insecure-!obqg==iukt0^hu$#uzvcz&n^#d&$p3@&__8c68ipo3h6(b-rs
   DJANGO_ALLOWED_HOSTS=localhost 127.0.0.1 [::1]
   
   # Database
   POSTGRES_DB=postgres
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=postgres
   POSTGRES_HOST=db
   POSTGRES_PORT=5432
   
   # Redis/Celery
   CELERY_BROKER=redis://redis:6379/0
   CELERY_BACKEND=redis://redis:6379/0
   ```

3. Start all services with Docker Compose:
   ```bash
   docker compose up -d
   ```

4. Apply database migrations:
   ```bash
   docker compose exec web python manage.py migrate
   ```

5. Create a superuser for admin access:
   ```bash
   docker compose exec web python manage.py createsuperuser
   ```
   Follow the prompts to create your admin user.

6. Access the application:
   - **Admin interface**: http://localhost:8000/admin/
   - **API endpoints**: http://localhost:8000/api/v1/analytics/

### Checking Service Status

Verify all services are running correctly:

```bash
docker compose ps
```

You should see the following services running:
- `web`: Django web server
- `db`: PostgreSQL database
- `redis`: Redis cache/message broker
- `celery-worker`: Celery worker for background tasks
- `celery-beat`: Celery beat for scheduled tasks

### Viewing Logs

Monitor service logs to troubleshoot issues:

```bash
# View logs for all services
docker compose logs

# View logs for a specific service
docker compose logs web

# Follow logs in real-time
docker compose logs -f
```

### Testing the API

Send test events using curl:

```bash
# Capture a single event
curl -X POST -H "Content-Type: application/json" \
  -d '{"distinct_id":"test-user","event_type":"button_click","device_id":"test-device","app_version":"1.0","os_name":"iOS","os_version":"15.0"}' \
  http://localhost:8000/api/v1/analytics/capture/

# Start a session
curl -X POST -H "Content-Type: application/json" \
  -d '{"distinct_id":"test-user","device_id":"test-device","app_version":"1.0","os_name":"iOS","os_version":"15.0"}' \
  http://localhost:8000/api/v1/analytics/session/start/
```

### Stopping the Services

Stop all running services:

```bash
docker compose down
```

## Project Structure

```
data-tracking/
├── core/                   # Django project settings
├── apps/                   # Django applications
│   ├── analytics/          # Event tracking app
│   │   ├── models.py       # Data models with normalized structure
│   │   ├── views.py        # API endpoints
│   │   ├── serializers.py  # REST serializers
│   │   ├── tasks.py        # Celery tasks
│   │   ├── utils.py        # Utility functions for data normalization
│   │   ├── admin.py        # Admin interfaces
│   │   └── migrations/     # Database migrations
│   └── users/              # User management app
├── nginx/                  # Nginx configuration
├── docker-compose.yml      # Development configuration
├── docker-compose.prod.yml # Production configuration
├── Dockerfile
├── Makefile                # Development commands
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

## API Endpoints

### Public Endpoints (No Authentication Required)

#### Event Capture
- `POST /api/v1/analytics/capture/` - Capture a single event
- `POST /api/v1/analytics/batch/` - Capture multiple events at once
- `POST /api/v1/analytics/session/start/` - Start a new session
- `PUT /api/v1/analytics/session/{session_id}/end/` - End an existing session

#### Feature Flags
- `GET /api/v1/analytics/public/feature-flags/` - List all active feature flags
- `GET /api/v1/analytics/public/feature-flags/for_user/?distinct_id={distinct_id}` - Get feature flags for a user

### Admin Endpoints (Authentication Required)
- `GET /api/v1/analytics/admin/events/` - List all events
- `GET /api/v1/analytics/admin/events/event_counts/` - Get event counts by type
- `GET /api/v1/analytics/admin/sessions/` - List all sessions
- `GET /api/v1/analytics/admin/feature-flags/` - Manage feature flags
- `GET /api/v1/analytics/admin/event-aggregates/` - View aggregated event data

## Event Structure

A typical event includes:

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

## Data Normalization Strategy

To optimize storage and improve performance, we use a normalized data structure:

1. **DeviceInfo Model**: Stores device-specific information that rarely changes
2. **LocationInfo Model**: Stores location data derived from IP addresses
3. **Session-Event Relationship**: Events are linked to sessions automatically
4. **Utility Functions**: Helper functions handle data normalization transparently

This approach provides several benefits:
- **Reduced Storage**: Up to 60-80% reduction in database size for large installations
- **Improved Query Performance**: Faster queries on normalized data
- **Data Consistency**: Device and location information is consistent across events
- **API Compatibility**: The API remains backward compatible despite the internal changes

## Production Deployment

1. Configure environment variables in a `.env.prod` file
2. Build and start the production environment:
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

## License

This project is licensed under the MIT License - see the LICENSE file for details.