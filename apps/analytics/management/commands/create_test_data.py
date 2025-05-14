from django.core.management.base import BaseCommand
from django.db import transaction
from apps.analytics.models import FeatureFlag
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Create test data for the analytics app'

    def handle(self, *args, **options):
        self.stdout.write('Creating test data for analytics app...')
        
        self._create_feature_flags()
        
        self.stdout.write(self.style.SUCCESS('Successfully created test data'))
    
    @transaction.atomic
    def _create_feature_flags(self):
        """Create default feature flags for testing."""
        test_flags = [
            {
                'name': 'New Checkout Flow',
                'key': 'new_checkout_flow',
                'description': 'Shows the new redesigned checkout flow',
                'active': True,
                'rollout_percentage': 50,
            },
            {
                'name': 'Dark Mode',
                'key': 'dark_mode',
                'description': 'Enables dark mode in the application',
                'active': True,
                'rollout_percentage': 100,
            },
            {
                'name': 'Enhanced Search',
                'key': 'enhanced_search',
                'description': 'Enables the new search algorithm with better results',
                'active': False,
                'rollout_percentage': 0,
            },
            {
                'name': 'Push Notifications',
                'key': 'push_notifications',
                'description': 'Enables push notifications for order updates',
                'active': True,
                'rollout_percentage': 25,
            },
            {
                'name': 'Beta Features',
                'key': 'beta_features',
                'description': 'Provides access to beta features in the app',
                'active': True,
                'rollout_percentage': 10,
            },
        ]
        
        created_count = 0
        for flag_data in test_flags:
            _, created = FeatureFlag.objects.update_or_create(
                key=flag_data['key'], 
                defaults=flag_data
            )
            if created:
                created_count += 1
        
        self.stdout.write(f'Created {created_count} feature flags') 