from celery import shared_task
from django.core import management
from django.utils import timezone
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

@shared_task
def cleanup_old_events():
    """
    Clean up old events based on retention policy.
    
    This task is scheduled to run daily during low-traffic hours.
    """
    logger.info("Starting scheduled cleanup of old events")
    try:
        management.call_command('cleanup_events')
        return "Cleanup completed successfully"
    except Exception as e:
        logger.error(f"Error during event cleanup: {str(e)}")
        return f"Error during cleanup: {str(e)}"


@shared_task
def generate_daily_report():
    """
    Generate a daily analytics report.
    
    This task is scheduled to run every morning to summarize yesterday's activity.
    """
    logger.info("Generating daily analytics report")
    yesterday = (timezone.now() - timedelta(days=1)).date().isoformat()
    
    try:
        management.call_command('analyze_trends', days=1)
        return f"Daily report for {yesterday} generated successfully"
    except Exception as e:
        logger.error(f"Error generating daily report: {str(e)}")
        return f"Error generating report: {str(e)}"


@shared_task
def verify_data_integrity():
    """
    Check for data integrity issues between raw events and aggregated data.
    
    This task ensures that our aggregated data tables match the raw event counts.
    """
    logger.info("Verifying data integrity")
    
    from django.db import connection
    from apps.analytics.models import Event, EventAggregate
    
    # Get the last 7 days to check
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=7)
    
    # Compare raw event counts with aggregated counts
    mismatches = []
    
    with connection.cursor() as cursor:
        # SQL for checking counts by date and event type
        cursor.execute("""
            SELECT 
                date(e.timestamp) as event_date,
                e.event_type,
                COUNT(e.id) as raw_count,
                COALESCE(ea.count, 0) as agg_count
            FROM 
                analytics_event e
                LEFT JOIN analytics_eventaggregate ea ON date(e.timestamp) = ea.date 
                    AND e.event_type = ea.event_type 
                    AND ea.hour IS NULL
            WHERE 
                e.timestamp >= %s
                AND e.timestamp < %s
            GROUP BY 
                date(e.timestamp), e.event_type, ea.count
            HAVING 
                COUNT(e.id) != COALESCE(ea.count, 0)
        """, [start_date, end_date + timedelta(days=1)])
        
        mismatches = cursor.fetchall()
    
    if mismatches:
        logger.warning(f"Found {len(mismatches)} data integrity issues")
        for mismatch in mismatches:
            logger.warning(f"Mismatch on {mismatch[0]} for {mismatch[1]}: raw={mismatch[2]}, agg={mismatch[3]}")
        return f"Data integrity issues found: {len(mismatches)} mismatches"
    
    logger.info("Data integrity verified - no issues found")
    return "Data integrity verified - no issues found" 