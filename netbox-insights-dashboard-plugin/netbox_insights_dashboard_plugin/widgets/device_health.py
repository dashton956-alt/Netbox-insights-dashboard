"""Device Health Monitor Widget."""

from typing import Dict, List
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from .base import BaseWidget, register_widget
from ..utils.cache import cached_widget_data
from ..models import DeviceHealthMetric
from dcim.models import Device


@register_widget
class DeviceHealthWidget(BaseWidget):
    """
    Widget monitoring device health and data completeness.
    
    Features:
    - Device status categorization
    - Missing data identification
    - Custom field validation
    - Health score trending
    """
    
    slug = "device_health"
    name = "Device Health Monitor"
    description = "Track device health and identify data quality issues"
    icon = "💚"
    template = "netbox_insights_dashboard_plugin/widgets/device_health.html"
    refresh_interval = 300
    order = 2
    
    def calculate_device_health(self, device: Device) -> Dict:
        """Calculate health score for a single device."""
        score = 100
        issues = []
        
        # Check for primary IP (-20 points)
        if not device.primary_ip4 and not device.primary_ip6:
            score -= 20
            issues.append("Missing primary IP address")
        
        # Check for site (-15 points)
        if not device.site:
            score -= 15
            issues.append("No site assigned")
        
        # Check for role (-15 points)
        if not device.device_role:
            score -= 15
            issues.append("No device role assigned")
        
        # Check for interfaces (-15 points)
        if device.interfaces.count() == 0:
            score -= 15
            issues.append("No interfaces configured")
        
        # Check for serial number (-10 points)
        if not device.serial:
            score -= 10
            issues.append("Missing serial number")
        
        # Check for asset tag (-10 points)
        if not device.asset_tag:
            score -= 10
            issues.append("Missing asset tag")
        
        # Check for platform (-10 points)
        if not device.platform:
            score -= 10
            issues.append("No platform specified")
        
        # Check if device is offline (-5 points)
        if device.status == 'offline':
            score -= 5
            issues.append("Device is offline")
        
        return {
            'device': device,
            'score': max(0, score),
            'issues': issues,
            'is_healthy': score >= 80
        }
    
    @cached_widget_data(timeout=300)
    def get_context_data(self) -> Dict:
        """Get device health monitoring data."""
        stale_days = self.config.get('stale_data_days', 30)
        cutoff_date = timezone.now() - timedelta(days=stale_days)
        
        # Get all active devices
        devices = Device.objects.filter(status='active')
        total_devices = devices.count()
        
        # Categorize devices
        healthy_devices = []
        warning_devices = []
        critical_devices = []
        
        for device in devices:
            health_data = self.calculate_device_health(device)
            score = health_data['score']
            
            if score >= 80:
                healthy_devices.append(health_data)
            elif score >= 60:
                warning_devices.append(health_data)
            else:
                critical_devices.append(health_data)
        
        # Find devices with stale data
        stale_devices = Device.objects.filter(
            status='active',
            last_updated__lt=cutoff_date
        )
        
        # Common issues summary
        devices_no_ip = devices.filter(
            Q(primary_ip4__isnull=True) & Q(primary_ip6__isnull=True)
        ).count()
        
        devices_no_interfaces = devices.annotate(
            interface_count=Count('interfaces')
        ).filter(interface_count=0).count()
        
        devices_no_site = devices.filter(site__isnull=True).count()
        
        devices_no_role = devices.filter(device_role__isnull=True).count()
        
        # Calculate overall health percentage
        if total_devices > 0:
            overall_health = (len(healthy_devices) / total_devices) * 100
        else:
            overall_health = 100
        
        return {
            'total_devices': total_devices,
            'healthy_count': len(healthy_devices),
            'warning_count': len(warning_devices),
            'critical_count': len(critical_devices),
            'overall_health': round(overall_health, 1),
            'critical_devices': critical_devices[:10],  # Top 10 worst
            'warning_devices': warning_devices[:10],
            'stale_devices_count': stale_devices.count(),
            'common_issues': {
                'no_primary_ip': devices_no_ip,
                'no_interfaces': devices_no_interfaces,
                'no_site': devices_no_site,
                'no_role': devices_no_role,
            },
            'last_updated': timezone.now().isoformat(),
        }
