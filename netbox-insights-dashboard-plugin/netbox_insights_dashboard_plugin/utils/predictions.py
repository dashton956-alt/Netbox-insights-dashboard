"""Predictive analytics and trend analysis algorithms."""

from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from django.db.models import Avg, Count, Sum
from django.utils import timezone
import statistics

from ..models import IPAMUtilization, DeviceHealthMetric
from ipam.models import Prefix, IPAddress
from dcim.models import Device


def calculate_growth_rate(data_points: List[Tuple[datetime, float]]) -> float:
    """
    Calculate linear growth rate from time series data.
    
    Args:
        data_points: List of (timestamp, value) tuples
        
    Returns:
        Growth rate per week
    """
    if len(data_points) < 2:
        return 0.0
    
    # Sort by timestamp
    data_points.sort(key=lambda x: x[0])
    
    # Convert to days since first data point
    first_time = data_points[0][0]
    x_values = [(point[0] - first_time).total_seconds() / 86400 for point in data_points]
    y_values = [point[1] for point in data_points]
    
    # Simple linear regression
    n = len(x_values)
    x_mean = statistics.mean(x_values)
    y_mean = statistics.mean(y_values)
    
    numerator = sum((x_values[i] - x_mean) * (y_values[i] - y_mean) for i in range(n))
    denominator = sum((x_values[i] - x_mean) ** 2 for i in range(n))
    
    if denominator == 0:
        return 0.0
    
    # Slope = growth per day
    slope = numerator / denominator
    
    # Convert to growth per week
    weekly_growth = slope * 7
    
    return round(weekly_growth, 2)


def analyze_ipam_trends(prefix_id: int, days: int = 90) -> Dict:
    """
    Analyze IPAM utilization trends for a prefix.
    
    Args:
        prefix_id: Prefix ID to analyze
        days: Number of days to look back
        
    Returns:
        Dictionary with trend analysis
    """
    cutoff_date = timezone.now() - timedelta(days=days)
    
    # Get historical utilization data
    historical_data = IPAMUtilization.objects.filter(
        prefix_id=prefix_id,
        calculated_at__gte=cutoff_date
    ).order_by('calculated_at')
    
    if not historical_data.exists():
        return {
            'has_data': False,
            'message': 'Insufficient historical data'
        }
    
    # Extract data points
    data_points = [
        (record.calculated_at, record.utilization_percent)
        for record in historical_data
    ]
    
    # Calculate growth rate
    growth_rate = calculate_growth_rate(data_points)
    
    # Get current utilization
    current_util = data_points[-1][1] if data_points else 0
    
    # Project future utilization
    weeks_to_90_percent = 0
    weeks_to_100_percent = 0
    
    if growth_rate > 0:
        weeks_to_90_percent = (90 - current_util) / growth_rate
        weeks_to_100_percent = (100 - current_util) / growth_rate
    
    # Calculate projected dates
    now = timezone.now()
    projected_90_date = now + timedelta(weeks=weeks_to_90_percent) if weeks_to_90_percent > 0 else None
    projected_100_date = now + timedelta(weeks=weeks_to_100_percent) if weeks_to_100_percent > 0 else None
    
    return {
        'has_data': True,
        'current_utilization': round(current_util, 2),
        'growth_rate_percent_per_week': growth_rate,
        'weeks_to_90_percent': round(weeks_to_90_percent, 1) if weeks_to_90_percent > 0 else None,
        'weeks_to_100_percent': round(weeks_to_100_percent, 1) if weeks_to_100_percent > 0 else None,
        'projected_90_percent_date': projected_90_date.isoformat() if projected_90_date else None,
        'projected_100_percent_date': projected_100_date.isoformat() if projected_100_date else None,
        'data_points_count': len(data_points),
        'analysis_period_days': days,
    }


def get_predictive_alerts(
    trend_period_days: int = 90,
    forecast_horizon_days: int = 180,
    growth_threshold: float = 5.0
) -> List[Dict]:
    """
    Generate predictive maintenance alerts.
    
    Args:
        trend_period_days: Period to analyze trends
        forecast_horizon_days: How far ahead to forecast
        growth_threshold: Minimum growth rate to alert on
        
    Returns:
        List of alert dictionaries
    """
    alerts = []
    cutoff_date = timezone.now() - timedelta(days=trend_period_days)
    
    # Analyze IPAM exhaustion
    prefixes = Prefix.objects.filter(status='active')
    
    for prefix in prefixes:
        # Get recent utilization history
        recent_utils = IPAMUtilization.objects.filter(
            prefix=prefix,
            calculated_at__gte=cutoff_date
        ).order_by('calculated_at')
        
        if recent_utils.count() >= 2:
            data_points = [
                (u.calculated_at, u.utilization_percent)
                for u in recent_utils
            ]
            
            growth_rate = calculate_growth_rate(data_points)
            
            if growth_rate >= growth_threshold:
                current_util = data_points[-1][1]
                weeks_to_exhaustion = (100 - current_util) / growth_rate if growth_rate > 0 else 999
                
                if weeks_to_exhaustion < (forecast_horizon_days / 7):
                    severity = 'high' if weeks_to_exhaustion < 4 else 'medium'
                    eta = timezone.now() + timedelta(weeks=weeks_to_exhaustion)
                    
                    alerts.append({
                        'type': 'ipam_exhaustion',
                        'severity': severity,
                        'prefix': str(prefix.prefix),
                        'prefix_id': prefix.pk,
                        'site': prefix.site.name if prefix.site else 'No Site',
                        'current_utilization': round(current_util, 1),
                        'growth_rate': round(growth_rate, 2),
                        'weeks_remaining': round(weeks_to_exhaustion, 1),
                        'estimated_exhaustion': eta.isoformat(),
                        'message': f"Prefix {prefix.prefix} projected to exhaust in {weeks_to_exhaustion:.1f} weeks",
                        'recommendation': 'Consider expanding the prefix or implementing IPv6',
                    })
    
    # Detect anomalies (unusual growth patterns)
    for prefix in prefixes:
        recent_utils = IPAMUtilization.objects.filter(
            prefix=prefix,
            calculated_at__gte=cutoff_date
        ).order_by('calculated_at')
        
        if recent_utils.count() >= 5:
            util_values = [u.utilization_percent for u in recent_utils]
            
            # Calculate standard deviation
            if len(util_values) > 1:
                std_dev = statistics.stdev(util_values)
                mean_util = statistics.mean(util_values)
                latest_util = util_values[-1]
                
                # Alert if latest is more than 2 standard deviations from mean
                if abs(latest_util - mean_util) > (2 * std_dev):
                    alerts.append({
                        'type': 'anomaly_detected',
                        'severity': 'medium',
                        'prefix': str(prefix.prefix),
                        'prefix_id': prefix.pk,
                        'site': prefix.site.name if prefix.site else 'No Site',
                        'message': f"Unusual growth pattern detected in {prefix.prefix}",
                        'current_utilization': round(latest_util, 1),
                        'mean_utilization': round(mean_util, 1),
                        'std_deviation': round(std_dev, 2),
                        'recommendation': 'Investigate recent changes or automation errors',
                    })
    
    # Sort alerts by severity
    severity_order = {'high': 0, 'medium': 1, 'low': 2}
    alerts.sort(key=lambda x: severity_order.get(x['severity'], 3))
    
    return alerts


def detect_stale_devices(stale_days: int = 30) -> List[Dict]:
    """
    Detect devices with stale data.
    
    Args:
        stale_days: Number of days before data is considered stale
        
    Returns:
        List of stale device alerts
    """
    cutoff_date = timezone.now() - timedelta(days=stale_days)
    alerts = []
    
    # Find devices not updated recently
    stale_devices = Device.objects.filter(
        last_updated__lt=cutoff_date,
        status='active'
    )
    
    for device in stale_devices:
        days_since_update = (timezone.now() - device.last_updated).days
        
        alerts.append({
            'type': 'stale_device_data',
            'severity': 'low',
            'device': device.name,
            'device_id': device.pk,
            'site': device.site.name if device.site else 'No Site',
            'days_since_update': days_since_update,
            'last_updated': device.last_updated.isoformat(),
            'message': f"Device {device.name} hasn't been updated in {days_since_update} days",
            'recommendation': 'Verify device is still active and update NetBox data',
        })
    
    return alerts
