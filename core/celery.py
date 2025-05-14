import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('core')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# Define scheduled tasks
app.conf.beat_schedule = {
    'close-inactive-sessions': {
        'task': 'apps.analytics.tasks.close_inactive_sessions',
        'schedule': crontab(minute='*/10'),  # Run every 10 minutes
    },
    'aggregate-daily-events': {
        'task': 'apps.analytics.tasks.aggregate_daily_events',
        'schedule': crontab(hour=1, minute=0),  # Run at 1:00 AM every day
    },
    'aggregate-hourly-events': {
        'task': 'apps.analytics.tasks.aggregate_hourly_events',
        'schedule': crontab(minute=5),  # Run 5 minutes past every hour
    },
    'cleanup-old-events': {
        'task': 'apps.analytics.scheduled_tasks.cleanup_old_events',
        'schedule': crontab(hour=2, minute=0),  # Run at 2:00 AM every day
    },
    'generate-daily-report': {
        'task': 'apps.analytics.scheduled_tasks.generate_daily_report',
        'schedule': crontab(hour=6, minute=0),  # Run at 6:00 AM every day
    },
    'verify-data-integrity': {
        'task': 'apps.analytics.scheduled_tasks.verify_data_integrity',
        'schedule': crontab(day_of_week=1, hour=4, minute=0),  # Run at 4:00 AM every Monday
    },
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}') 