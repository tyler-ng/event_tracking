# Generated by Django 5.2.1 on 2025-05-14 20:04

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("analytics", "0003_add_app_check_result"),
    ]

    operations = [
        migrations.CreateModel(
            name="DeviceInfo",
            fields=[
                (
                    "device_id",
                    models.CharField(max_length=100, primary_key=True, serialize=False),
                ),
                ("app_version", models.CharField(max_length=50)),
                ("os_name", models.CharField(max_length=50)),
                ("os_version", models.CharField(max_length=50)),
                (
                    "is_simulator",
                    models.BooleanField(
                        blank=True,
                        help_text="Whether the device is a simulator/emulator",
                        null=True,
                    ),
                ),
                (
                    "is_rooted_device",
                    models.BooleanField(
                        blank=True,
                        help_text="Whether the device is rooted/jailbroken",
                        null=True,
                    ),
                ),
                (
                    "is_vpn_enabled",
                    models.BooleanField(
                        blank=True,
                        help_text="Whether a VPN is active on the device",
                        null=True,
                    ),
                ),
                ("last_seen", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Device Information",
                "verbose_name_plural": "Device Information",
            },
        ),
        migrations.CreateModel(
            name="LocationInfo",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                (
                    "ip_address",
                    models.GenericIPAddressField(blank=True, null=True, unique=True),
                ),
                (
                    "city",
                    models.CharField(
                        blank=True,
                        help_text="City based on IP geolocation",
                        max_length=100,
                        null=True,
                    ),
                ),
                (
                    "country",
                    models.CharField(
                        blank=True,
                        help_text="Country based on IP geolocation",
                        max_length=100,
                        null=True,
                    ),
                ),
                (
                    "continent",
                    models.CharField(
                        blank=True,
                        help_text="Continent based on IP geolocation",
                        max_length=100,
                        null=True,
                    ),
                ),
            ],
            options={
                "verbose_name": "Location Information",
                "verbose_name_plural": "Location Information",
            },
        ),
        migrations.RemoveIndex(
            model_name="event",
            name="analytics_e_device__5052af_idx",
        ),
        migrations.RemoveIndex(
            model_name="event",
            name="analytics_e_country_abf8ec_idx",
        ),
        migrations.RemoveIndex(
            model_name="event",
            name="analytics_e_city_db128c_idx",
        ),
        migrations.RemoveIndex(
            model_name="session",
            name="analytics_s_device__fa5057_idx",
        ),
        migrations.RemoveIndex(
            model_name="session",
            name="analytics_s_country_507c3e_idx",
        ),
        migrations.RemoveIndex(
            model_name="session",
            name="analytics_s_city_7215f7_idx",
        ),
        migrations.RenameField(
            model_name="event",
            old_name="city",
            new_name="temp_city",
        ),
        migrations.RenameField(
            model_name="event",
            old_name="continent",
            new_name="temp_continent",
        ),
        migrations.RenameField(
            model_name="event",
            old_name="country",
            new_name="temp_country",
        ),
        migrations.RenameField(
            model_name="event",
            old_name="ip_address",
            new_name="temp_ip_address",
        ),
        migrations.RenameField(
            model_name="event",
            old_name="is_rooted_device",
            new_name="temp_is_rooted_device",
        ),
        migrations.RenameField(
            model_name="event",
            old_name="is_simulator",
            new_name="temp_is_simulator",
        ),
        migrations.RenameField(
            model_name="event",
            old_name="is_vpn_enabled",
            new_name="temp_is_vpn_enabled",
        ),
        migrations.RenameField(
            model_name="session",
            old_name="city",
            new_name="temp_city",
        ),
        migrations.RenameField(
            model_name="session",
            old_name="continent",
            new_name="temp_continent",
        ),
        migrations.RenameField(
            model_name="session",
            old_name="country",
            new_name="temp_country",
        ),
        migrations.RenameField(
            model_name="session",
            old_name="ip_address",
            new_name="temp_ip_address",
        ),
        migrations.RenameField(
            model_name="session",
            old_name="is_rooted_device",
            new_name="temp_is_rooted_device",
        ),
        migrations.RenameField(
            model_name="session",
            old_name="is_simulator",
            new_name="temp_is_simulator",
        ),
        migrations.RenameField(
            model_name="session",
            old_name="is_vpn_enabled",
            new_name="temp_is_vpn_enabled",
        ),
        migrations.RemoveField(
            model_name="event",
            name="app_version",
        ),
        migrations.RemoveField(
            model_name="event",
            name="device_id",
        ),
        migrations.RemoveField(
            model_name="event",
            name="os_name",
        ),
        migrations.RemoveField(
            model_name="event",
            name="os_version",
        ),
        migrations.RemoveField(
            model_name="session",
            name="app_version",
        ),
        migrations.RemoveField(
            model_name="session",
            name="device_id",
        ),
        migrations.RemoveField(
            model_name="session",
            name="os_name",
        ),
        migrations.RemoveField(
            model_name="session",
            name="os_version",
        ),
        migrations.AddField(
            model_name="event",
            name="session",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="events",
                to="analytics.session",
            ),
        ),
        migrations.AddField(
            model_name="event",
            name="temp_app_version",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name="event",
            name="temp_device_id",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name="event",
            name="temp_os_name",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name="event",
            name="temp_os_version",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name="session",
            name="temp_app_version",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name="session",
            name="temp_device_id",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name="session",
            name="temp_os_name",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name="session",
            name="temp_os_version",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name="event",
            name="device",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="events",
                to="analytics.deviceinfo",
            ),
        ),
        migrations.AddField(
            model_name="session",
            name="device",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="sessions",
                to="analytics.deviceinfo",
            ),
        ),
        migrations.AddIndex(
            model_name="locationinfo",
            index=models.Index(
                fields=["country"], name="analytics_l_country_0fe1b3_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="locationinfo",
            index=models.Index(fields=["city"], name="analytics_l_city_25a8af_idx"),
        ),
        migrations.AddField(
            model_name="event",
            name="location",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="events",
                to="analytics.locationinfo",
            ),
        ),
        migrations.AddField(
            model_name="session",
            name="location",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="sessions",
                to="analytics.locationinfo",
            ),
        ),
    ]
