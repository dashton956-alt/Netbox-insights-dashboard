"""API Serializers for NetBox Insights Dashboard."""

from rest_framework import serializers
from ..models import DeviceHealthMetric, IPAMUtilization, CustomMetric, VendorIntegration


class DeviceHealthMetricSerializer(serializers.ModelSerializer):
    """Serializer for DeviceHealthMetric model."""
    
    device_name = serializers.CharField(source='device.name', read_only=True)
    
    class Meta:
        model = DeviceHealthMetric
        fields = [
            'id', 'device', 'device_name', 'health_score',
            'checked_at', 'issues', 'metadata', 'created', 'last_updated'
        ]


class IPAMUtilizationSerializer(serializers.ModelSerializer):
    """Serializer for IPAMUtilization model."""
    
    prefix_str = serializers.CharField(source='prefix.prefix', read_only=True)
    site_name = serializers.CharField(source='prefix.site.name', read_only=True)
    
    class Meta:
        model = IPAMUtilization
        fields = [
            'id', 'prefix', 'prefix_str', 'site_name',
            'utilization_percent', 'available_ips', 'calculated_at',
            'trend', 'created', 'last_updated'
        ]


class CustomMetricSerializer(serializers.ModelSerializer):
    """Serializer for CustomMetric model."""
    
    device_name = serializers.CharField(source='device.name', read_only=True, allow_null=True)
    site_name = serializers.CharField(source='site.name', read_only=True, allow_null=True)
    
    class Meta:
        model = CustomMetric
        fields = [
            'id', 'metric_name', 'metric_type', 'value',
            'device', 'device_name', 'site', 'site_name',
            'timestamp', 'source', 'created', 'last_updated'
        ]


class VendorIntegrationSerializer(serializers.ModelSerializer):
    """Serializer for VendorIntegration model."""
    
    class Meta:
        model = VendorIntegration
        fields = [
            'id', 'vendor_slug', 'vendor_name', 'enabled',
            'config', 'last_sync', 'sync_status', 'sync_message',
            'created', 'last_updated'
        ]
        read_only_fields = ['last_sync', 'sync_status', 'sync_message']


class IPAMUtilizationSummarySerializer(serializers.Serializer):
    """Serializer for IPAM utilization summary data."""
    
    prefix = serializers.CharField()
    site = serializers.CharField()
    utilization = serializers.FloatField()
    total_ips = serializers.IntegerField()
    used_ips = serializers.IntegerField()
    available_ips = serializers.IntegerField()
    status = serializers.CharField()


class DeviceHealthSummarySerializer(serializers.Serializer):
    """Serializer for device health summary data."""
    
    device_id = serializers.IntegerField()
    device_name = serializers.CharField()
    health_score = serializers.IntegerField()
    issues = serializers.ListField()


class PredictiveAlertSerializer(serializers.Serializer):
    """Serializer for predictive maintenance alerts."""
    
    type = serializers.CharField()
    severity = serializers.CharField()
    message = serializers.CharField()
    recommendation = serializers.CharField(required=False)
    estimated_exhaustion = serializers.CharField(required=False)
