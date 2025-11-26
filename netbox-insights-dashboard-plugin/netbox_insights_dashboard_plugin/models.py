"""Database models for NetBox Insights Dashboard Plugin."""

from django.db import models
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
from netbox.models import NetBoxModel
from dcim.models import Device, Site
from ipam.models import Prefix


class DeviceHealthMetric(NetBoxModel):
    """Store health scores over time for trending and historical analysis."""
    
    device = models.ForeignKey(
        to=Device,
        on_delete=models.CASCADE,
        related_name='health_metrics'
    )
    health_score = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Overall health score (0-100)"
    )
    checked_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this health check was performed"
    )
    issues = models.JSONField(
        default=list,
        help_text="List of identified issues"
    )
    metadata = models.JSONField(
        default=dict,
        help_text="Vendor-specific data and additional context"
    )

    class Meta:
        ordering = ('-checked_at',)
        indexes = [
            models.Index(fields=['device', '-checked_at']),
        ]
        verbose_name = "Device Health Metric"
        verbose_name_plural = "Device Health Metrics"

    def __str__(self):
        return f"{self.device.name} - {self.health_score}% at {self.checked_at}"

    def get_absolute_url(self):
        return reverse("plugins:netbox_insights_dashboard_plugin:dashboard")


class IPAMUtilization(NetBoxModel):
    """Cache IPAM calculations for performance and trend analysis."""
    
    prefix = models.ForeignKey(
        to=Prefix,
        on_delete=models.CASCADE,
        related_name='utilization_metrics'
    )
    utilization_percent = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text="Percentage of IPs used in this prefix"
    )
    available_ips = models.IntegerField(
        help_text="Number of available IPs"
    )
    calculated_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this calculation was performed"
    )
    trend = models.FloatField(
        null=True,
        blank=True,
        help_text="Growth rate percentage per week"
    )

    class Meta:
        ordering = ('-calculated_at',)
        indexes = [
            models.Index(fields=['prefix', '-calculated_at']),
        ]
        verbose_name = "IPAM Utilization"
        verbose_name_plural = "IPAM Utilizations"

    def __str__(self):
        return f"{self.prefix} - {self.utilization_percent:.1f}% at {self.calculated_at}"

    def get_absolute_url(self):
        return reverse("plugins:netbox_insights_dashboard_plugin:dashboard")


class CustomMetric(NetBoxModel):
    """User-defined metrics from external sources (optional integration)."""
    
    metric_name = models.CharField(
        max_length=100,
        help_text="Name of the metric"
    )
    metric_type = models.CharField(
        max_length=50,
        default='gauge',
        help_text="Type of metric (counter, gauge, histogram, etc.)"
    )
    value = models.JSONField(
        help_text="Metric value (can be scalar or complex)"
    )
    device = models.ForeignKey(
        to=Device,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='custom_metrics',
        help_text="Associated device (optional)"
    )
    site = models.ForeignKey(
        to=Site,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='custom_metrics',
        help_text="Associated site (optional)"
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text="When this metric was recorded"
    )
    source = models.CharField(
        max_length=100,
        blank=True,
        help_text="Source system or tool (e.g., 'ansible_tower', 'prometheus')"
    )

    class Meta:
        ordering = ('-timestamp',)
        indexes = [
            models.Index(fields=['metric_name', '-timestamp']),
            models.Index(fields=['device', '-timestamp']),
            models.Index(fields=['site', '-timestamp']),
        ]
        verbose_name = "Custom Metric"
        verbose_name_plural = "Custom Metrics"

    def __str__(self):
        return f"{self.metric_name}: {self.value} at {self.timestamp}"

    def get_absolute_url(self):
        return reverse("plugins:netbox_insights_dashboard_plugin:dashboard")


class VendorIntegration(NetBoxModel):
    """Configuration for each vendor module."""
    
    vendor_slug = models.CharField(
        max_length=50,
        unique=True,
        help_text="Unique identifier for this vendor (e.g., 'cisco_ios')"
    )
    vendor_name = models.CharField(
        max_length=100,
        help_text="Display name for this vendor"
    )
    enabled = models.BooleanField(
        default=True,
        help_text="Whether this integration is active"
    )
    config = models.JSONField(
        default=dict,
        help_text="Vendor-specific configuration settings"
    )
    last_sync = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last successful synchronization time"
    )
    sync_status = models.CharField(
        max_length=20,
        default='pending',
        help_text="Status of last sync (success, failed, pending)"
    )
    sync_message = models.TextField(
        blank=True,
        help_text="Details about last sync operation"
    )

    class Meta:
        ordering = ('vendor_name',)
        verbose_name = "Vendor Integration"
        verbose_name_plural = "Vendor Integrations"

    def __str__(self):
        status = "✓" if self.enabled else "✗"
        return f"{status} {self.vendor_name}"

    def get_absolute_url(self):
        return reverse("plugins:netbox_insights_dashboard_plugin:config")
