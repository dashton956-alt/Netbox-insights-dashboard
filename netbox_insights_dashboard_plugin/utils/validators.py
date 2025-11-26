"""Data quality validators and compliance checking."""

import re
from typing import Dict, List, Tuple
from django.db.models import Q, Count
from dcim.models import Device, Interface, Cable
from ipam.models import IPAddress


def validate_device_completeness(device: Device, required_fields: List[str]) -> Tuple[bool, List[str]]:
    """
    Validate that a device has all required fields populated.
    
    Args:
        device: NetBox Device object
        required_fields: List of required field names
        
    Returns:
        Tuple of (is_valid, list of missing fields)
    """
    missing_fields = []
    
    for field in required_fields:
        # Handle nested fields (e.g., 'site.name')
        if '.' in field:
            parts = field.split('.')
            value = device
            for part in parts:
                value = getattr(value, part, None)
                if value is None:
                    missing_fields.append(field)
                    break
        else:
            value = getattr(device, field, None)
            if value is None or value == '':
                missing_fields.append(field)
    
    return (len(missing_fields) == 0, missing_fields)


def validate_naming_convention(name: str, pattern: str) -> bool:
    """
    Validate a name against a regex pattern.
    
    Args:
        name: Name to validate
        pattern: Regex pattern
        
    Returns:
        True if valid, False otherwise
    """
    try:
        return bool(re.match(pattern, name))
    except re.error:
        return True  # Invalid pattern, skip validation


def calculate_data_quality_score(
    required_fields: List[str] = None,
    naming_patterns: Dict[str, str] = None
) -> Dict:
    """
    Calculate overall data quality score for NetBox.
    
    Args:
        required_fields: List of required device fields
        naming_patterns: Dict of {field: regex_pattern}
        
    Returns:
        Dictionary with quality score and details
    """
    if required_fields is None:
        required_fields = ['site', 'device_role', 'device_type']
    
    if naming_patterns is None:
        naming_patterns = {}
    
    devices = Device.objects.all()
    total_devices = devices.count()
    
    if total_devices == 0:
        return {
            'score': 100,
            'message': 'No devices to evaluate'
        }
    
    # Track issues
    issues = {
        'missing_fields': [],
        'naming_violations': [],
        'duplicate_serials': [],
        'duplicate_macs': [],
        'missing_primary_ip': [],
        'no_interfaces': [],
    }
    
    compliant_devices = 0
    
    for device in devices:
        device_compliant = True
        
        # Check required fields
        is_complete, missing = validate_device_completeness(device, required_fields)
        if not is_complete:
            device_compliant = False
            issues['missing_fields'].append({
                'device': device.name,
                'device_id': device.pk,
                'missing': missing
            })
        
        # Check naming conventions
        if 'device_name' in naming_patterns:
            if not validate_naming_convention(device.name, naming_patterns['device_name']):
                device_compliant = False
                issues['naming_violations'].append({
                    'device': device.name,
                    'device_id': device.pk,
                    'field': 'name',
                    'pattern': naming_patterns['device_name']
                })
        
        # Check for primary IP
        if not device.primary_ip4 and not device.primary_ip6:
            device_compliant = False
            issues['missing_primary_ip'].append({
                'device': device.name,
                'device_id': device.pk,
            })
        
        # Check for interfaces
        if device.interfaces.count() == 0:
            device_compliant = False
            issues['no_interfaces'].append({
                'device': device.name,
                'device_id': device.pk,
            })
        
        if device_compliant:
            compliant_devices += 1
    
    # Check for duplicate serial numbers
    duplicate_serials = Device.objects.values('serial').annotate(
        count=Count('serial')
    ).filter(count__gt=1, serial__isnull=False).exclude(serial='')
    
    for dup in duplicate_serials:
        devices_with_serial = Device.objects.filter(serial=dup['serial'])
        issues['duplicate_serials'].append({
            'serial': dup['serial'],
            'count': dup['count'],
            'devices': [{'name': d.name, 'id': d.pk} for d in devices_with_serial]
        })
    
    # Check for duplicate MAC addresses
    duplicate_macs = Interface.objects.values('mac_address').annotate(
        count=Count('mac_address')
    ).filter(count__gt=1, mac_address__isnull=False)
    
    for dup in duplicate_macs:
        interfaces = Interface.objects.filter(mac_address=dup['mac_address'])
        issues['duplicate_macs'].append({
            'mac_address': str(dup['mac_address']),
            'count': dup['count'],
            'interfaces': [{
                'device': i.device.name if i.device else 'N/A',
                'interface': i.name,
                'id': i.pk
            } for i in interfaces]
        })
    
    # Calculate quality score (0-100)
    score = (compliant_devices / total_devices) * 100
    
    # Count total issues
    total_issues = sum(len(v) for v in issues.values())
    
    return {
        'score': round(score, 1),
        'total_devices': total_devices,
        'compliant_devices': compliant_devices,
        'non_compliant_devices': total_devices - compliant_devices,
        'total_issues': total_issues,
        'issues': issues,
        'details': {
            'missing_fields_count': len(issues['missing_fields']),
            'naming_violations_count': len(issues['naming_violations']),
            'duplicate_serials_count': len(issues['duplicate_serials']),
            'duplicate_macs_count': len(issues['duplicate_macs']),
            'missing_primary_ip_count': len(issues['missing_primary_ip']),
            'no_interfaces_count': len(issues['no_interfaces']),
        }
    }


def validate_cable_connections() -> Dict:
    """
    Validate cable connections for completeness.
    
    Returns:
        Dictionary with cable validation results
    """
    cables = Cable.objects.all()
    total_cables = cables.count()
    
    invalid_cables = []
    
    for cable in cables:
        issues = []
        
        # Check both ends are connected
        if not cable.a_terminations.exists():
            issues.append('Missing A-side termination')
        
        if not cable.b_terminations.exists():
            issues.append('Missing B-side termination')
        
        # Check cable has a type
        if not cable.type:
            issues.append('Missing cable type')
        
        if issues:
            invalid_cables.append({
                'cable_id': cable.pk,
                'label': cable.label or f'Cable #{cable.pk}',
                'issues': issues
            })
    
    valid_cables = total_cables - len(invalid_cables)
    
    return {
        'total_cables': total_cables,
        'valid_cables': valid_cables,
        'invalid_cables_count': len(invalid_cables),
        'invalid_cables': invalid_cables[:50],  # Limit to first 50
        'validation_passed': len(invalid_cables) == 0
    }


def get_data_quality_recommendations() -> List[Dict]:
    """
    Generate actionable recommendations for improving data quality.
    
    Returns:
        List of recommendation dictionaries
    """
    recommendations = []
    
    # Check for devices missing primary IPs
    devices_no_ip = Device.objects.filter(
        Q(primary_ip4__isnull=True) & Q(primary_ip6__isnull=True),
        status='active'
    ).count()
    
    if devices_no_ip > 0:
        recommendations.append({
            'priority': 'high',
            'category': 'completeness',
            'title': f'{devices_no_ip} active devices missing primary IP',
            'description': 'Primary IPs are essential for device management and monitoring',
            'action': 'Assign primary IPs to active devices',
            'impact': 'High - Affects device management and automation'
        })
    
    # Check for devices with no interfaces
    devices_no_interfaces = Device.objects.annotate(
        interface_count=Count('interfaces')
    ).filter(interface_count=0, status='active').count()
    
    if devices_no_interfaces > 0:
        recommendations.append({
            'priority': 'medium',
            'category': 'completeness',
            'title': f'{devices_no_interfaces} devices have no interfaces',
            'description': 'Devices should have at least one interface documented',
            'action': 'Add interface information to these devices',
            'impact': 'Medium - Affects network topology visibility'
        })
    
    # Check for duplicate serial numbers
    duplicate_serials_count = Device.objects.values('serial').annotate(
        count=Count('serial')
    ).filter(count__gt=1, serial__isnull=False).exclude(serial='').count()
    
    if duplicate_serials_count > 0:
        recommendations.append({
            'priority': 'high',
            'category': 'accuracy',
            'title': f'{duplicate_serials_count} duplicate serial numbers found',
            'description': 'Serial numbers must be unique for inventory tracking',
            'action': 'Review and correct duplicate serial numbers',
            'impact': 'High - Affects asset tracking and warranty management'
        })
    
    return recommendations
