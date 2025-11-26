"""Tables for NetBox Insights Dashboard Plugin (not currently used by dashboard)."""

import django_tables2 as tables
from netbox.tables import NetBoxTable

from .models import DeviceHealthMetric, IPAMUtilization, CustomMetric, VendorIntegration


class DeviceHealthMetricTable(NetBoxTable):
    """Table for DeviceHealthMetric model."""
    
    device = tables.Column(linkify=True)
    health_score = tables.Column()
    checked_at = tables.DateTimeColumn()

    class Meta(NetBoxTable.Meta):
        model = DeviceHealthMetric
        fields = ("pk", "id", "device", "health_score", "checked_at", "actions")
        default_columns = ("device", "health_score", "checked_at")


class IPAMUtilizationTable(NetBoxTable):
    """Table for IPAMUtilization model."""
    
    prefix = tables.Column(linkify=True)
    utilization_percent = tables.Column()
    calculated_at = tables.DateTimeColumn()

    class Meta(NetBoxTable.Meta):
        model = IPAMUtilization
        fields = ("pk", "id", "prefix", "utilization_percent", "available_ips", "trend", "calculated_at", "actions")
        default_columns = ("prefix", "utilization_percent", "available_ips", "calculated_at")


class CustomMetricTable(NetBoxTable):
    """Table for CustomMetric model."""
    
    metric_name = tables.Column(linkify=True)
    device = tables.Column(linkify=True)
    site = tables.Column(linkify=True)
    timestamp = tables.DateTimeColumn()

    class Meta(NetBoxTable.Meta):
        model = CustomMetric
        fields = ("pk", "id", "metric_name", "metric_type", "device", "site", "source", "timestamp", "actions")
        default_columns = ("metric_name", "metric_type", "device", "site", "timestamp")


class VendorIntegrationTable(NetBoxTable):
    """Table for VendorIntegration model."""
    
    vendor_name = tables.Column(linkify=True)
    enabled = tables.BooleanColumn()
    last_sync = tables.DateTimeColumn()

    class Meta(NetBoxTable.Meta):
        model = VendorIntegration
        fields = ("pk", "id", "vendor_name", "vendor_slug", "enabled", "sync_status", "last_sync", "actions")
        default_columns = ("vendor_name", "enabled", "sync_status", "last_sync")
