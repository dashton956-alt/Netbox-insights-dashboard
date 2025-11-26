"""Capacity Planning Widget."""

from typing import Dict, List
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Count
from .base import BaseWidget, register_widget
from ..utils.cache import cached_widget_data
from dcim.models import Device, Rack, Site
from circuits.models import Circuit
from ipam.models import Prefix


@register_widget
class CapacityPlanningWidget(BaseWidget):
    """
    Widget for capacity planning and growth forecasting.
    
    Features:
    - Device count growth trends
    - IPAM space consumption rate
    - Rack space utilization
    - Circuit/bandwidth tracking
    - Forecast projections
    """
    
    slug = "capacity-planning"
    name = "Capacity Planning"
    description = "Track growth trends and forecast capacity requirements"
    icon = "📈"
    template = "netbox_insights_dashboard_plugin/widgets/capacity_planning.html"
    refresh_interval = 900
    order = 5
    
    def calculate_growth_metrics(self, days: int = 90) -> Dict:
        """Calculate growth metrics over specified period."""
        now = timezone.now()
        cutoff_date = now - timedelta(days=days)
        
        # Device growth
        total_devices = Device.objects.count()
        new_devices = Device.objects.filter(created__gte=cutoff_date).count()
        
        # Calculate weekly growth rate
        weeks = days / 7
        devices_per_week = new_devices / weeks if weeks > 0 else 0
        
        # IPAM growth
        total_prefixes = Prefix.objects.count()
        new_prefixes = Prefix.objects.filter(created__gte=cutoff_date).count()
        prefixes_per_week = new_prefixes / weeks if weeks > 0 else 0
        
        # Circuit growth
        total_circuits = Circuit.objects.count()
        new_circuits = Circuit.objects.filter(created__gte=cutoff_date).count()
        circuits_per_week = new_circuits / weeks if weeks > 0 else 0
        
        return {
            'devices': {
                'total': total_devices,
                'new': new_devices,
                'per_week': round(devices_per_week, 2),
                'growth_rate': round((new_devices / total_devices * 100), 2) if total_devices > 0 else 0
            },
            'prefixes': {
                'total': total_prefixes,
                'new': new_prefixes,
                'per_week': round(prefixes_per_week, 2),
                'growth_rate': round((new_prefixes / total_prefixes * 100), 2) if total_prefixes > 0 else 0
            },
            'circuits': {
                'total': total_circuits,
                'new': new_circuits,
                'per_week': round(circuits_per_week, 2),
                'growth_rate': round((new_circuits / total_circuits * 100), 2) if total_circuits > 0 else 0
            }
        }
    
    def calculate_rack_utilization(self) -> List[Dict]:
        """Calculate rack space utilization by site."""
        racks = Rack.objects.all()
        site_utilization = {}
        
        for rack in racks:
            site_name = rack.site.name if rack.site else 'No Site'
            
            if site_name not in site_utilization:
                site_utilization[site_name] = {
                    'site': site_name,
                    'total_racks': 0,
                    'total_u_space': 0,
                    'used_u_space': 0,
                }
            
            site_data = site_utilization[site_name]
            site_data['total_racks'] += 1
            
            # Add U space
            if rack.u_height:
                site_data['total_u_space'] += rack.u_height
                
                # Calculate used space (count device U heights in this rack)
                devices_in_rack = Device.objects.filter(rack=rack)
                for device in devices_in_rack:
                    if device.device_type and device.device_type.u_height:
                        site_data['used_u_space'] += device.device_type.u_height
        
        # Calculate utilization percentages
        result = []
        for site_data in site_utilization.values():
            if site_data['total_u_space'] > 0:
                utilization = (site_data['used_u_space'] / site_data['total_u_space']) * 100
            else:
                utilization = 0
            
            site_data['utilization'] = round(utilization, 1)
            site_data['available_u_space'] = site_data['total_u_space'] - site_data['used_u_space']
            result.append(site_data)
        
        # Sort by utilization
        result.sort(key=lambda x: x['utilization'], reverse=True)
        return result
    
    def forecast_capacity(self, growth_metrics: Dict, months: int = 6) -> Dict:
        """Forecast future capacity based on current growth rates."""
        weeks = months * 4.33  # Average weeks per month
        
        # Forecast devices
        device_growth = growth_metrics['devices']['per_week'] * weeks
        forecasted_devices = growth_metrics['devices']['total'] + device_growth
        
        # Forecast prefixes
        prefix_growth = growth_metrics['prefixes']['per_week'] * weeks
        forecasted_prefixes = growth_metrics['prefixes']['total'] + prefix_growth
        
        # Forecast circuits
        circuit_growth = growth_metrics['circuits']['per_week'] * weeks
        forecasted_circuits = growth_metrics['circuits']['total'] + circuit_growth
        
        return {
            'months': months,
            'devices': {
                'current': growth_metrics['devices']['total'],
                'forecasted': int(forecasted_devices),
                'growth': int(device_growth)
            },
            'prefixes': {
                'current': growth_metrics['prefixes']['total'],
                'forecasted': int(forecasted_prefixes),
                'growth': int(prefix_growth)
            },
            'circuits': {
                'current': growth_metrics['circuits']['total'],
                'forecasted': int(forecasted_circuits),
                'growth': int(circuit_growth)
            }
        }
    
    @cached_widget_data(timeout=900)
    def get_context_data(self) -> Dict:
        """Get capacity planning data."""
        # Get configuration
        historical_days = self.config.get('historical_period_days', 90)
        capacity_threshold = self.config.get('capacity_warning_threshold', 80)
        
        # Calculate growth metrics
        growth_30 = self.calculate_growth_metrics(days=30)
        growth_90 = self.calculate_growth_metrics(days=historical_days)
        
        # Get rack utilization
        rack_utilization = self.calculate_rack_utilization()
        
        # Forecast future capacity (6 months)
        forecast = self.forecast_capacity(growth_90, months=6)
        
        # Find sites approaching capacity
        sites_near_capacity = [
            site for site in rack_utilization
            if site['utilization'] >= capacity_threshold
        ]
        
        return {
            'growth_30_days': growth_30,
            'growth_90_days': growth_90,
            'rack_utilization': rack_utilization[:10],  # Top 10 sites
            'sites_near_capacity': sites_near_capacity,
            'forecast_6_months': forecast,
            'capacity_threshold': capacity_threshold,
            'last_updated': timezone.now().isoformat(),
        }
