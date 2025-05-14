# Installation Guide

This guide provides detailed instructions for setting up the Event Tracking System.

## Development Setup

### Prerequisites

- Docker Engine (20.10.x or higher)
- Docker Compose (v2.x or higher)
- Git

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/data-tracking.git
cd data-tracking
```

### Step 2: Create Environment Configuration

Create a `.env` file in the project root with the following content:

```
# Django development settings
DEBUG=1
SECRET_KEY=change-me-to-a-random-string-in-production
DJANGO_ALLOWED_HOSTS=localhost 127.0.0.1 [::1]

# Database settings
POSTGRES_DB=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=db
POSTGRES_PORT=5432

# Redis settings
REDIS_URL=redis://redis:6379/0
CELERY_BROKER=redis://redis:6379/0
CELERY_BACKEND=redis://redis:6379/0

# Event tracking settings
SESSION_TIMEOUT_MINUTES=30
MAX_BATCH_SIZE=1000
RETENTION_DAYS=365
```

### Step 3: Start the Development Environment

```bash
docker-compose up -d
```

This will start all required services:
- Django web server
- PostgreSQL database
- Redis cache
- Celery worker
- Celery beat scheduler

### Step 4: Initialize the Database

Run migrations to set up the database schema:

```bash
docker-compose exec web python manage.py migrate
```

### Step 5: Create an Admin User

```bash
docker-compose exec web python manage.py createsuperuser
```

Follow the prompts to create your admin account.

### Step 6: Verify the Installation

Open your browser and visit:
- Admin interface: http://localhost:8000/admin/
- API endpoints: http://localhost:8000/api/v1/

## Production Deployment

For production deployments, additional configuration is required.

### Step 1: Create Production Environment Configuration

Create a `.env.prod` file with appropriate values:

```
# Django production settings
DEBUG=0
SECRET_KEY=your-secure-production-secret-key
DJANGO_ALLOWED_HOSTS=yourdomain.com www.yourdomain.com

# Database settings
POSTGRES_DB=postgres
POSTGRES_USER=secure_username
POSTGRES_PASSWORD=secure_password
POSTGRES_HOST=db
POSTGRES_PORT=5432

# Redis settings
REDIS_URL=redis://redis:6379/0
CELERY_BROKER=redis://redis:6379/0
CELERY_BACKEND=redis://redis:6379/0

# Event tracking settings
SESSION_TIMEOUT_MINUTES=30
MAX_BATCH_SIZE=1000
RETENTION_DAYS=365
```

### Step 2: Launch with Production Configuration

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Step 3: Set Up SSL (Recommended)

For production, you should configure SSL certificates with Let's Encrypt or a similar service.

### Step 4: Database Partitioning Setup

For high-volume production use, set up table partitioning for the Event table:

```sql
-- Example PostgreSQL partitioning setup (to be run by a database administrator)
CREATE TABLE analytics_event_y2023m01 PARTITION OF analytics_event
    FOR VALUES FROM ('2023-01-01') TO ('2023-02-01');
    
CREATE TABLE analytics_event_y2023m02 PARTITION OF analytics_event
    FOR VALUES FROM ('2023-02-01') TO ('2023-03-01');
    
-- And so on for future months
```

### Step 5: Monitoring Setup

For production environments, set up monitoring with Prometheus and Grafana.

## Troubleshooting

### Common Issues

#### Database Connection Errors

If the web service can't connect to the database:

```bash
# Verify the database is running
docker-compose ps

# Check database logs
docker-compose logs db

# Try recreating the containers
docker-compose down
docker-compose up -d
```

#### Redis Connection Issues

If Celery workers can't connect to Redis:

```bash
# Check Redis logs
docker-compose logs redis

# Verify Redis is accessible
docker-compose exec redis redis-cli ping
```

#### Celery Tasks Not Running

If background tasks aren't processing:

```bash
# Check Celery logs
docker-compose logs celery-worker
docker-compose logs celery-beat

# Restart Celery services
docker-compose restart celery-worker celery-beat
```

## Maintenance

### Database Backups

Create regular database backups:

```bash
docker-compose exec db pg_dump -U postgres postgres > backup_$(date +%Y-%m-%d_%H-%M-%S).sql
```

### Log Rotation

The Docker logs will grow over time. Set up log rotation for production environments.

## Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework Documentation](https://www.django-rest-framework.org/)
- [Celery Documentation](https://docs.celeryproject.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)