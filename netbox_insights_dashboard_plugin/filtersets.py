"""Filtersets for NetBox Insights Dashboard Plugin."""

from netbox.filtersets import NetBoxModelFilterSet
from .models import DeviceHealthMetric, IPAMUtilization, CustomMetric, VendorIntegration


class DeviceHealthMetricFilterSet(NetBoxModelFilterSet):
    """FilterSet for DeviceHealthMetric model."""
    
    class Meta:
        model = DeviceHealthMetric
        fields = ['device', 'health_score', 'checked_at']

    def search(self, queryset, name, value):
        return queryset.filter(device__name__icontains=value)


class IPAMUtilizationFilterSet(NetBoxModelFilterSet):
    """FilterSet for IPAMUtilization model."""
    
    class Meta:
        model = IPAMUtilization
        fields = ['prefix', 'utilization_percent', 'calculated_at']

    def search(self, queryset, name, value):
        return queryset.filter(prefix__prefix__icontains=value)


class CustomMetricFilterSet(NetBoxModelFilterSet):
    """FilterSet for CustomMetric model."""
    
    class Meta:
        model = CustomMetric
        fields = ['metric_name', 'metric_type', 'device', 'site', 'source']

    def search(self, queryset, name, value):
        return queryset.filter(metric_name__icontains=value)


class VendorIntegrationFilterSet(NetBoxModelFilterSet):
    """FilterSet for VendorIntegration model."""
    
    class Meta:
        model = VendorIntegration
        fields = ['vendor_slug', 'vendor_name', 'enabled', 'sync_status']

    def search(self, queryset, name, value):
        return queryset.filter(vendor_name__icontains=value)
