"""Forms for NetBox Insights Dashboard Plugin."""

from django import forms
from netbox.forms import NetBoxModelForm
from .models import DeviceHealthMetric, IPAMUtilization, CustomMetric, VendorIntegration


class DeviceHealthMetricForm(NetBoxModelForm):
    """Form for DeviceHealthMetric model."""
    
    class Meta:
        model = DeviceHealthMetric
        fields = ['device', 'health_score', 'issues', 'metadata', 'tags']


class IPAMUtilizationForm(NetBoxModelForm):
    """Form for IPAMUtilization model."""
    
    class Meta:
        model = IPAMUtilization
        fields = ['prefix', 'utilization_percent', 'available_ips', 'trend', 'tags']


class CustomMetricForm(NetBoxModelForm):
    """Form for CustomMetric model."""
    
    class Meta:
        model = CustomMetric
        fields = [
            'metric_name', 'metric_type', 'value',
            'device', 'site', 'source', 'tags'
        ]


class VendorIntegrationForm(NetBoxModelForm):
    """Form for VendorIntegration model."""
    
    class Meta:
        model = VendorIntegration
        fields = [
            'vendor_slug', 'vendor_name', 'enabled',
            'config', 'tags'
        ]


class ConfigurationForm(forms.Form):
    """Configuration form for dashboard settings."""
    
    # IPAM Settings
    ipam_warning_threshold = forms.IntegerField(
        min_value=0,
        max_value=100,
        initial=75,
        label='IPAM Warning Threshold (%)',
        help_text='Show warning when prefix utilization reaches this percentage'
    )
    
    ipam_critical_threshold = forms.IntegerField(
        min_value=0,
        max_value=100,
        initial=90,
        label='IPAM Critical Threshold (%)',
        help_text='Show critical alert when prefix utilization reaches this percentage'
    )
    
    # Device Health Settings
    stale_data_days = forms.IntegerField(
        min_value=1,
        max_value=365,
        initial=30,
        label='Stale Data Threshold (days)',
        help_text='Consider device data stale after this many days'
    )
    
    # Data Quality Settings
    min_quality_score = forms.IntegerField(
        min_value=0,
        max_value=100,
        initial=80,
        label='Minimum Quality Score',
        help_text='Target data quality score percentage'
    )
    
    # Predictive Settings
    trend_period_days = forms.IntegerField(
        min_value=7,
        max_value=365,
        initial=90,
        label='Trend Analysis Period (days)',
        help_text='Analyze trends over this many days'
    )
    
    forecast_horizon_days = forms.IntegerField(
        min_value=30,
        max_value=730,
        initial=180,
        label='Forecast Horizon (days)',
        help_text='How far ahead to forecast capacity needs'
    )
    
    # Capacity Planning Settings
    historical_period_days = forms.IntegerField(
        min_value=30,
        max_value=365,
        initial=90,
        label='Historical Period (days)',
        help_text='Period for historical capacity analysis'
    )
    
    capacity_warning_threshold = forms.IntegerField(
        min_value=0,
        max_value=100,
        initial=80,
        label='Capacity Warning Threshold (%)',
        help_text='Alert when capacity reaches this percentage'
    )
    
    # General Settings
    enable_caching = forms.BooleanField(
        initial=True,
        required=False,
        label='Enable Caching',
        help_text='Cache widget data for improved performance'
    )
    
    cache_ttl = forms.IntegerField(
        min_value=60,
        max_value=3600,
        initial=300,
        label='Cache TTL (seconds)',
        help_text='How long to cache widget data'
    )
