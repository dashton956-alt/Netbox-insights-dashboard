"""IPAM calculations and utilization logic."""

from typing import Dict, List, Tuple
from decimal import Decimal
from datetime import datetime, timedelta
from django.db.models import Count, Q
from ipam.models import Prefix, IPAddress, VLAN
from dcim.models import Site


def calculate_prefix_utilization(prefix: Prefix) -> Dict:
    """
    Calculate utilization for a single prefix.
    
    Args:
        prefix: NetBox Prefix object
        
    Returns:
        Dictionary with utilization metrics
    """
    try:
        # Get total IPs in prefix
        total_ips = prefix.get_total_ips()
        
        # Get used IPs (count IP addresses in this prefix)
        used_ips = IPAddress.objects.filter(
            address__net_contained_or_equal=str(prefix.prefix)
        ).count()
        
        # Calculate utilization percentage
        if total_ips > 0:
            utilization = (used_ips / total_ips) * 100
        else:
            utilization = 0.0
        
        # Available IPs
        available_ips = total_ips - used_ips
        
        # Status based on utilization
        if utilization >= 95:
            status = 'critical'
            emoji = '🔴'
        elif utilization >= 90:
            status = 'danger'
            emoji = '🔴'
        elif utilization >= 75:
            status = 'warning'
            emoji = '🟡'
        else:
            status = 'healthy'
            emoji = '🟢'
        
        return {
            'prefix': str(prefix.prefix),
            'prefix_id': prefix.pk,
            'site': prefix.site.name if prefix.site else 'No Site',
            'site_id': prefix.site.pk if prefix.site else None,
            'vrf': prefix.vrf.name if prefix.vrf else 'Global',
            'role': prefix.role.name if prefix.role else 'No Role',
            'total_ips': total_ips,
            'used_ips': used_ips,
            'available_ips': available_ips,
            'utilization': round(utilization, 2),
            'status': status,
            'emoji': emoji,
            'description': prefix.description or '',
        }
    except Exception as e:
        return {
            'prefix': str(prefix.prefix),
            'error': str(e),
            'utilization': 0.0,
            'status': 'error',
            'emoji': '⚠️'
        }


def get_ipam_utilization_summary(
    site_id: int = None,
    role_slug: str = None,
    warning_threshold: float = 75.0,
    critical_threshold: float = 90.0
) -> Dict:
    """
    Get IPAM utilization summary with filtering.
    
    Args:
        site_id: Optional site ID to filter by
        role_slug: Optional role slug to filter by
        warning_threshold: Warning threshold percentage
        critical_threshold: Critical threshold percentage
        
    Returns:
        Dictionary with summary and prefix list
    """
    # Build query
    prefixes = Prefix.objects.filter(status='active')
    
    if site_id:
        prefixes = prefixes.filter(site_id=site_id)
    
    if role_slug:
        prefixes = prefixes.filter(role__slug=role_slug)
    
    # Calculate utilization for each prefix
    prefix_data = []
    total_prefixes = 0
    warning_count = 0
    critical_count = 0
    healthy_count = 0
    
    for prefix in prefixes:
        util_data = calculate_prefix_utilization(prefix)
        prefix_data.append(util_data)
        total_prefixes += 1
        
        utilization = util_data.get('utilization', 0)
        if utilization >= critical_threshold:
            critical_count += 1
        elif utilization >= warning_threshold:
            warning_count += 1
        else:
            healthy_count += 1
    
    # Sort by utilization (highest first)
    prefix_data.sort(key=lambda x: x.get('utilization', 0), reverse=True)
    
    return {
        'total_prefixes': total_prefixes,
        'warning_count': warning_count,
        'critical_count': critical_count,
        'healthy_count': healthy_count,
        'prefixes': prefix_data,
        'warning_threshold': warning_threshold,
        'critical_threshold': critical_threshold,
        'calculated_at': datetime.now().isoformat(),
    }


def calculate_vlan_utilization() -> List[Dict]:
    """
    Calculate VLAN usage by site.
    
    Returns:
        List of VLAN utilization data by site
    """
    sites = Site.objects.all()
    vlan_data = []
    
    for site in sites:
        total_vlans = VLAN.objects.filter(site=site).count()
        
        if total_vlans > 0:
            # Count VLANs with interfaces
            used_vlans = VLAN.objects.filter(
                site=site
            ).annotate(
                interface_count=Count('interfaces')
            ).filter(interface_count__gt=0).count()
            
            utilization = (used_vlans / total_vlans) * 100
            
            vlan_data.append({
                'site': site.name,
                'site_id': site.pk,
                'total_vlans': total_vlans,
                'used_vlans': used_vlans,
                'available_vlans': total_vlans - used_vlans,
                'utilization': round(utilization, 2),
            })
    
    # Sort by utilization
    vlan_data.sort(key=lambda x: x['utilization'], reverse=True)
    
    return vlan_data


def calculate_subnet_exhaustion_date(
    prefix: Prefix, 
    growth_rate: float
) -> datetime:
    """
    Calculate projected exhaustion date for a prefix based on growth rate.
    
    Args:
        prefix: NetBox Prefix object
        growth_rate: IPs consumed per week
        
    Returns:
        Projected exhaustion datetime
    """
    util_data = calculate_prefix_utilization(prefix)
    available_ips = util_data['available_ips']
    
    if growth_rate <= 0:
        return None
    
    weeks_remaining = available_ips / growth_rate
    exhaustion_date = datetime.now() + timedelta(weeks=weeks_remaining)
    
    return exhaustion_date
