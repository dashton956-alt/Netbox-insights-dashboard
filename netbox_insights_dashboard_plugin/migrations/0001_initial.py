# Generated migration for netbox_insights_dashboard_plugin

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import taggit.managers


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('dcim', '0001_initial'),
        ('ipam', '0001_initial'),
        ('extras', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeviceHealthMetric',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=None)),
                ('health_score', models.IntegerField(
                    help_text='Overall health score (0-100)',
                    validators=[
                        django.core.validators.MinValueValidator(0),
                        django.core.validators.MaxValueValidator(100)
                    ]
                )),
                ('checked_at', models.DateTimeField(auto_now_add=True, help_text='When this health check was performed')),
                ('issues', models.JSONField(default=list, help_text='List of identified issues')),
                ('metadata', models.JSONField(default=dict, help_text='Vendor-specific data and additional context')),
                ('device', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='health_metrics',
                    to='dcim.device'
                )),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
            ],
            options={
                'verbose_name': 'Device Health Metric',
                'verbose_name_plural': 'Device Health Metrics',
                'ordering': ('-checked_at',),
            },
        ),
        migrations.CreateModel(
            name='IPAMUtilization',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=None)),
                ('utilization_percent', models.FloatField(
                    help_text='Percentage of IPs used in this prefix',
                    validators=[
                        django.core.validators.MinValueValidator(0.0),
                        django.core.validators.MaxValueValidator(100.0)
                    ]
                )),
                ('available_ips', models.IntegerField(help_text='Number of available IPs')),
                ('calculated_at', models.DateTimeField(auto_now_add=True, help_text='When this calculation was performed')),
                ('trend', models.FloatField(blank=True, help_text='Growth rate percentage per week', null=True)),
                ('prefix', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='utilization_metrics',
                    to='ipam.prefix'
                )),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
            ],
            options={
                'verbose_name': 'IPAM Utilization',
                'verbose_name_plural': 'IPAM Utilizations',
                'ordering': ('-calculated_at',),
            },
        ),
        migrations.CreateModel(
            name='CustomMetric',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=None)),
                ('metric_name', models.CharField(help_text='Name of the metric', max_length=100)),
                ('metric_type', models.CharField(
                    default='gauge',
                    help_text='Type of metric (counter, gauge, histogram, etc.)',
                    max_length=50
                )),
                ('value', models.JSONField(help_text='Metric value (can be scalar or complex)')),
                ('timestamp', models.DateTimeField(auto_now_add=True, help_text='When this metric was recorded')),
                ('source', models.CharField(
                    blank=True,
                    help_text='Source system or tool (e.g., ansible_tower, prometheus)',
                    max_length=100
                )),
                ('device', models.ForeignKey(
                    blank=True,
                    help_text='Associated device (optional)',
                    null=True,
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='custom_metrics',
                    to='dcim.device'
                )),
                ('site', models.ForeignKey(
                    blank=True,
                    help_text='Associated site (optional)',
                    null=True,
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='custom_metrics',
                    to='dcim.site'
                )),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
            ],
            options={
                'verbose_name': 'Custom Metric',
                'verbose_name_plural': 'Custom Metrics',
                'ordering': ('-timestamp',),
            },
        ),
        migrations.CreateModel(
            name='VendorIntegration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=None)),
                ('vendor_slug', models.CharField(
                    help_text='Unique identifier for this vendor (e.g., cisco_ios)',
                    max_length=50,
                    unique=True
                )),
                ('vendor_name', models.CharField(help_text='Display name for this vendor', max_length=100)),
                ('enabled', models.BooleanField(default=True, help_text='Whether this integration is active')),
                ('config', models.JSONField(default=dict, help_text='Vendor-specific configuration settings')),
                ('last_sync', models.DateTimeField(
                    blank=True,
                    help_text='Last successful synchronization time',
                    null=True
                )),
                ('sync_status', models.CharField(
                    default='pending',
                    help_text='Status of last sync (success, failed, pending)',
                    max_length=20
                )),
                ('sync_message', models.TextField(blank=True, help_text='Details about last sync operation')),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
            ],
            options={
                'verbose_name': 'Vendor Integration',
                'verbose_name_plural': 'Vendor Integrations',
                'ordering': ('vendor_name',),
            },
        ),
        migrations.AddIndex(
            model_name='devicehealthmetric',
            index=models.Index(fields=['device', '-checked_at'], name='netbox_insi_device__idx'),
        ),
        migrations.AddIndex(
            model_name='ipamutilization',
            index=models.Index(fields=['prefix', '-calculated_at'], name='netbox_insi_prefix__idx'),
        ),
        migrations.AddIndex(
            model_name='custommetric',
            index=models.Index(fields=['metric_name', '-timestamp'], name='netbox_insi_metric__idx'),
        ),
        migrations.AddIndex(
            model_name='custommetric',
            index=models.Index(fields=['device', '-timestamp'], name='netbox_insi_device_t_idx'),
        ),
        migrations.AddIndex(
            model_name='custommetric',
            index=models.Index(fields=['site', '-timestamp'], name='netbox_insi_site_ti_idx'),
        ),
    ]
