"""Network Topology Status Widget."""

from typing import Dict, List
from django.db.models import Count, Q
from django.utils import timezone
from .base import BaseWidget, register_widget
from ..utils.cache import cached_widget_data
from dcim.models import Cable, Interface, Device, Site
from circuits.models import Circuit


@register_widget
class TopologyStatusWidget(BaseWidget):
    """
    Widget displaying network topology and connectivity status.
    
    Features:
    - Site connectivity overview
    - Link redundancy analysis
    - Cable validation
    - Interface status aggregation
    - Circuit tracking
    """
    
    slug = "topology-status"
    name = "Network Topology Status"
    description = "Monitor network connectivity, cables, and topology health"
    icon = "🔗"
    template = "netbox_insights_dashboard_plugin/widgets/topology_status.html"
    refresh_interval = 300
    order = 6
    
    def get_cable_health(self) -> Dict:
        """Analyze cable connections health."""
        cables = Cable.objects.all()
        total_cables = cables.count()
        
        # Count valid cables (both ends connected)
        valid_cables = 0
        invalid_cables = []
        
        for cable in cables:
            is_valid = True
            issues = []
            
            # Check terminations
            if not cable.a_terminations.exists():
                is_valid = False
                issues.append('Missing A-side')
            
            if not cable.b_terminations.exists():
                is_valid = False
                issues.append('Missing B-side')
            
            if not cable.type:
                is_valid = False
                issues.append('No cable type')
            
            if is_valid:
                valid_cables += 1
            else:
                invalid_cables.append({
                    'id': cable.pk,
                    'label': cable.label or f'Cable #{cable.pk}',
                    'issues': issues
                })
        
        return {
            'total': total_cables,
            'valid': valid_cables,
            'invalid': len(invalid_cables),
            'invalid_cables': invalid_cables[:10],  # Top 10
            'health_percentage': round((valid_cables / total_cables * 100), 1) if total_cables > 0 else 100
        }
    
    def get_interface_status(self) -> Dict:
        """Aggregate interface status across all devices."""
        interfaces = Interface.objects.filter(device__isnull=False)
        
        # Count by status
        status_counts = interfaces.values('enabled').annotate(count=Count('id'))
        
        enabled = 0
        disabled = 0
        
        for status in status_counts:
            if status['enabled']:
                enabled = status['count']
            else:
                disabled = status['count']
        
        total = enabled + disabled
        
        # Count connected interfaces (have cables)
        connected = interfaces.filter(cable__isnull=False).count()
        disconnected = total - connected
        
        return {
            'total': total,
            'enabled': enabled,
            'disabled': disabled,
            'connected': connected,
            'disconnected': disconnected,
            'utilization': round((connected / total * 100), 1) if total > 0 else 0
        }
    
    def analyze_site_connectivity(self) -> List[Dict]:
        """Analyze inter-site connectivity."""
        sites = Site.objects.all()
        connectivity_map = []
        
        for site in sites:
            # Find devices at this site
            site_devices = Device.objects.filter(site=site)
            
            # Count interfaces
            total_interfaces = Interface.objects.filter(device__in=site_devices).count()
            
            # Count cables connecting to other sites
            inter_site_cables = 0
            connected_sites = set()
            
            for device in site_devices:
                device_interfaces = device.interfaces.all()
                for interface in device_interfaces:
                    if interface.cable:
                        # Check if cable connects to different site
                        for termination in interface.cable.b_terminations.all():
                            if hasattr(termination, 'device') and termination.device:
                                if termination.device.site and termination.device.site != site:
                                    inter_site_cables += 1
                                    connected_sites.add(termination.device.site.name)
            
            if total_interfaces > 0 or inter_site_cables > 0:
                connectivity_map.append({
                    'site': site.name,
                    'site_id': site.pk,
                    'total_interfaces': total_interfaces,
                    'inter_site_links': inter_site_cables,
                    'connected_to_sites': list(connected_sites),
                    'connection_count': len(connected_sites)
                })
        
        # Sort by inter-site links
        connectivity_map.sort(key=lambda x: x['inter_site_links'], reverse=True)
        return connectivity_map
    
    def get_circuit_summary(self) -> Dict:
        """Get circuit status summary."""
        circuits = Circuit.objects.all()
        total_circuits = circuits.count()
        
        # Count by status
        active_circuits = circuits.filter(status='active').count()
        
        # Count by provider (top 5)
        top_providers = circuits.values('provider__name').annotate(
            count=Count('id')
        ).order_by('-count')[:5]
        
        return {
            'total': total_circuits,
            'active': active_circuits,
            'top_providers': [
                {'name': p['provider__name'] or 'Unknown', 'count': p['count']}
                for p in top_providers
            ]
        }
    
    @cached_widget_data(timeout=300)
    def get_context_data(self) -> Dict:
        """Get network topology status data."""
        # Get configuration
        show_inter_site_only = self.config.get('show_inter_site_only', True)
        min_link_speed = self.config.get('min_link_speed', 1000)
        
        # Get cable health
        cable_health = self.get_cable_health()
        
        # Get interface status
        interface_status = self.get_interface_status()
        
        # Get site connectivity
        site_connectivity = self.analyze_site_connectivity()
        
        # Get circuit summary
        circuit_summary = self.get_circuit_summary()
        
        # Overall health assessment
        cable_health_pct = cable_health['health_percentage']
        interface_util_pct = interface_status['utilization']
        
        overall_health = (cable_health_pct + interface_util_pct) / 2
        
        if overall_health >= 90:
            health_status = 'healthy'
            health_emoji = '🟢'
        elif overall_health >= 70:
            health_status = 'warning'
            health_emoji = '🟡'
        else:
            health_status = 'critical'
            health_emoji = '🔴'
        
        return {
            'overall_health': round(overall_health, 1),
            'health_status': health_status,
            'health_emoji': health_emoji,
            'cable_health': cable_health,
            'interface_status': interface_status,
            'site_connectivity': site_connectivity[:15],  # Top 15 sites
            'circuit_summary': circuit_summary,
            'last_updated': timezone.now().isoformat(),
        }
