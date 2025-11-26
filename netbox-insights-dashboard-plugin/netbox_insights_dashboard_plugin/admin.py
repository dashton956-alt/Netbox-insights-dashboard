"""Django admin registration for NetBox Insights Dashboard."""

from django.contrib import admin
from .models import DeviceHealthMetric, IPAMUtilization, CustomMetric, VendorIntegration


@admin.register(DeviceHealthMetric)
class DeviceHealthMetricAdmin(admin.ModelAdmin):
    """Admin for DeviceHealthMetric model."""
    
    list_display = ['device', 'health_score', 'checked_at']
    list_filter = ['checked_at', 'health_score']
    search_fields = ['device__name']
    readonly_fields = ['checked_at', 'created', 'last_updated']
    ordering = ['-checked_at']


@admin.register(IPAMUtilization)
class IPAMUtilizationAdmin(admin.ModelAdmin):
    """Admin for IPAMUtilization model."""
    
    list_display = ['prefix', 'utilization_percent', 'available_ips', 'calculated_at']
    list_filter = ['calculated_at', 'utilization_percent']
    search_fields = ['prefix__prefix']
    readonly_fields = ['calculated_at', 'created', 'last_updated']
    ordering = ['-calculated_at']


@admin.register(CustomMetric)
class CustomMetricAdmin(admin.ModelAdmin):
    """Admin for CustomMetric model."""
    
    list_display = ['metric_name', 'metric_type', 'device', 'site', 'source', 'timestamp']
    list_filter = ['metric_type', 'source', 'timestamp']
    search_fields = ['metric_name', 'device__name', 'site__name']
    readonly_fields = ['timestamp', 'created', 'last_updated']
    ordering = ['-timestamp']


@admin.register(VendorIntegration)
class VendorIntegrationAdmin(admin.ModelAdmin):
    """Admin for VendorIntegration model."""
    
    list_display = ['vendor_name', 'vendor_slug', 'enabled', 'sync_status', 'last_sync']
    list_filter = ['enabled', 'sync_status']
    search_fields = ['vendor_name', 'vendor_slug']
    readonly_fields = ['last_sync', 'sync_status', 'sync_message', 'created', 'last_updated']
    ordering = ['vendor_name']
