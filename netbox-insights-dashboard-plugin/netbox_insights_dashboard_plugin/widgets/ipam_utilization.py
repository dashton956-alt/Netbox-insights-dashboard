"""IPAM Utilization Dashboard Widget."""

from typing import Dict
from django.utils import timezone
from .base import BaseWidget, register_widget
from ..utils.calculations import (
    get_ipam_utilization_summary,
    calculate_vlan_utilization
)
from ..utils.cache import cached_widget_data


@register_widget
class IPAMUtilizationWidget(BaseWidget):
    """
    Widget displaying IPAM prefix and VLAN utilization with threshold alerts.
    
    Features:
    - Real-time prefix utilization with color-coded thresholds
    - VLAN usage by site
    - Configurable alert thresholds
    - Quick filters and drill-down links
    """
    
    slug = "ipam_utilization"
    name = "IPAM Utilization"
    description = "Monitor IP address and VLAN usage across your network"
    icon = "🌐"
    template = "netbox_insights_dashboard_plugin/widgets/ipam_utilization.html"
    refresh_interval = 60
    order = 1
    
    @cached_widget_data(timeout=60)
    def get_context_data(self) -> Dict:
        """Get IPAM utilization data."""
        # Get thresholds from config
        warning_threshold = self.config.get('ipam_warning_threshold', 75)
        critical_threshold = self.config.get('ipam_critical_threshold', 90)
        
        # Get prefix utilization summary
        ipam_summary = get_ipam_utilization_summary(
            warning_threshold=warning_threshold,
            critical_threshold=critical_threshold
        )
        
        # Get VLAN utilization
        vlan_data = calculate_vlan_utilization()
        
        # Filter top prefixes by utilization (show top 20)
        top_prefixes = ipam_summary['prefixes'][:20]
        
        # Count by status
        status_summary = {
            'healthy': ipam_summary['healthy_count'],
            'warning': ipam_summary['warning_count'],
            'critical': ipam_summary['critical_count'],
            'total': ipam_summary['total_prefixes']
        }
        
        return {
            'summary': status_summary,
            'top_prefixes': top_prefixes,
            'vlan_data': vlan_data[:10],  # Top 10 sites
            'warning_threshold': warning_threshold,
            'critical_threshold': critical_threshold,
            'last_updated': timezone.now().isoformat(),
        }
