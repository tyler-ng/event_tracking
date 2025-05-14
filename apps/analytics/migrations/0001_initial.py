from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='EventAggregate',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('event_type', models.CharField(db_index=True, max_length=100)),
                ('date', models.DateField(db_index=True)),
                ('hour', models.IntegerField(blank=True, help_text='Hour of day (0-23) if this is an hourly aggregate', null=True)),
                ('count', models.IntegerField(default=0)),
                ('unique_users', models.IntegerField(default=0)),
                ('properties', models.JSONField(default=dict, help_text='Aggregated properties in JSON format')),
            ],
        ),
        migrations.CreateModel(
            name='FeatureFlag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('key', models.SlugField(max_length=100, unique=True)),
                ('description', models.TextField(blank=True)),
                ('active', models.BooleanField(default=False)),
                ('rollout_percentage', models.IntegerField(default=0, help_text='Percentage of users who should see this feature (0-100)')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Session',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('distinct_id', models.CharField(db_index=True, max_length=200)),
                ('device_id', models.CharField(db_index=True, max_length=100)),
                ('start_time', models.DateTimeField(db_index=True)),
                ('end_time', models.DateTimeField(blank=True, null=True)),
                ('duration', models.DurationField(blank=True, null=True)),
                ('events_count', models.IntegerField(default=0)),
                ('app_version', models.CharField(max_length=50)),
                ('os_name', models.CharField(max_length=50)),
                ('os_version', models.CharField(max_length=50)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='users.user')),
            ],
            options={
                'ordering': ['-start_time'],
                'indexes': [models.Index(fields=['distinct_id'], name='analytics_se_distinc_b59ec0_idx'), models.Index(fields=['start_time'], name='analytics_se_start_t_27fc9a_idx'), models.Index(fields=['device_id'], name='analytics_se_device__4fb0a3_idx')],
            },
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('distinct_id', models.CharField(help_text='Anonymous user identifier', max_length=200)),
                ('event_type', models.CharField(db_index=True, max_length=100)),
                ('properties', models.JSONField(default=dict, help_text='Event properties in JSON format')),
                ('timestamp', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('device_id', models.CharField(max_length=100)),
                ('app_version', models.CharField(max_length=50)),
                ('os_name', models.CharField(max_length=50)),
                ('os_version', models.CharField(max_length=50)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('processed', models.BooleanField(default=False, help_text='Whether this event has been processed')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(blank=True, help_text='Associated user if identified', null=True, on_delete=django.db.models.deletion.SET_NULL, to='users.user')),
            ],
            options={
                'ordering': ['-timestamp'],
                'indexes': [models.Index(fields=['distinct_id'], name='analytics_ev_distinc_25fce5_idx'), models.Index(fields=['event_type'], name='analytics_ev_event_t_7c12c0_idx'), models.Index(fields=['timestamp'], name='analytics_ev_timesta_d72ccb_idx'), models.Index(fields=['device_id'], name='analytics_ev_device__af2646_idx'), models.Index(fields=['processed'], name='analytics_ev_process_0751a1_idx')],
            },
        ),
        migrations.AddConstraint(
            model_name='eventaggregate',
            constraint=models.UniqueConstraint(fields=('event_type', 'date', 'hour'), name='unique_event_aggregate'),
        ),
    ] 