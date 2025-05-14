# Django Event Tracking System

A scalable Django-based event tracking system for mobile applications, similar to PostHog. This project provides a complete backend for capturing, storing, and analyzing user events from mobile apps.

## Features

- **Event Tracking**: Capture events from mobile applications
- **Session Management**: Track user sessions and behaviors
- **Feature Flags**: Implement A/B testing and feature rollouts
- **Analytics Dashboard**: View and analyze event data
- **Docker-based**: Full containerization for consistent development and deployment
- **PostgreSQL Database**: Robust data storage with PostgreSQL
- **Redis & Celery**: Background task processing and caching
- **Horizontal Scaling**: Designed to scale to millions of users

## Architecture

The system is built with a modern, scalable architecture:

- **Django REST Framework**: API endpoints for mobile clients
- **PostgreSQL**: Primary data storage with table partitioning
- **Redis**: Event buffering and caching
- **Celery**: Asynchronous task processing
- **Nginx**: Load balancing and reverse proxy

## Prerequisites

- Docker Engine (20.10.x or higher)
- Docker Compose (v2.x or higher)
- Make (for Makefile support)

## Quick Start

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/data-tracking.git
   cd data-tracking
   ```

2. Create a `.env` file with the necessary environment variables:
   ```
   DEBUG=1
   SECRET_KEY=your-secret-key
   DJANGO_ALLOWED_HOSTS=localhost 127.0.0.1 [::1]
   POSTGRES_DB=postgres
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=postgres
   ```

3. Start the development environment:
   ```bash
   docker-compose up -d
   ```

4. Run migrations:
   ```bash
   docker-compose exec web python manage.py migrate
   ```

5. Create a superuser:
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

6. Visit the application:
   - Admin interface: http://localhost:8000/admin
   - API endpoints: http://localhost:8000/api/v1/

## Project Structure

```
data-tracking/
├── core/                   # Django project settings
├── apps/                   # Django applications
│   ├── analytics/          # Event tracking app
│   │   ├── models.py       # Data models
│   │   ├── views.py        # API endpoints
│   │   ├── serializers.py  # REST serializers
│   │   ├── tasks.py        # Celery tasks
│   │   └── admin.py        # Admin interfaces
│   └── users/              # User management app
├── nginx/                  # Nginx configuration
├── static/                 # Static files
├── media/                  # User uploaded content
├── docker-compose.yml      # Development configuration
├── docker-compose.prod.yml # Production configuration
├── Dockerfile
├── Makefile                # Development commands
├── README.md
└── requirements.txt        # Python dependencies
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
  "timestamp": "2023-04-13T12:34:56Z"
}
```

## Mobile SDK Integration

Example iOS and Android SDKs are provided in the `apps/analytics/sdk_examples` directory. These show how to integrate the event tracking system with mobile applications.

## Scaling Considerations

The system is designed to scale to millions of users:

- **Database Partitioning**: Events are partitioned by date
- **Redis Buffering**: High traffic is buffered through Redis
- **Asynchronous Processing**: Events are processed in the background
- **Pre-computed Aggregates**: Dashboard data is pre-aggregated for performance

## Development

### Common Commands

```bash
# Start the development environment
docker-compose up -d

# Stop all containers
docker-compose down

# View logs
docker-compose logs -f

# Run the Django shell
docker-compose exec web python manage.py shell

# Run tests
docker-compose exec web python manage.py test

# Apply database migrations
docker-compose exec web python manage.py migrate
```

## Production Deployment

1. Configure environment variables in a `.env.prod` file
2. Build and start the production environment:
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

## License

This project is licensed under the MIT License - see the LICENSE file for details.