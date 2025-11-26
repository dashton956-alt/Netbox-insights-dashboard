"""Predictive Maintenance Widget."""

from typing import Dict
from django.utils import timezone
from .base import BaseWidget, register_widget
from ..utils.predictions import (
    get_predictive_alerts,
    detect_stale_devices
)
from ..utils.cache import cached_widget_data


@register_widget
class PredictiveMaintenanceWidget(BaseWidget):
    """
    Widget providing predictive analytics and proactive alerts.
    
    Features:
    - IPAM exhaustion prediction
    - Growth trend analysis
    - Anomaly detection
    - Stale device detection
    - Priority-based alerts
    """
    
    slug = "predictive_maintenance"
    name = "Predictive Maintenance"
    description = "Proactive alerts based on trend analysis and forecasting"
    icon = "🔮"
    template = "netbox_insights_dashboard_plugin/widgets/predictive_maintenance.html"
    refresh_interval = 600
    order = 4
    
    @cached_widget_data(timeout=600)
    def get_context_data(self) -> Dict:
        """Get predictive maintenance alerts."""
        # Get configuration
        trend_period_days = self.config.get('trend_period_days', 90)
        forecast_horizon_days = self.config.get('forecast_horizon_days', 180)
        growth_threshold = self.config.get('growth_rate_threshold', 5.0)
        stale_days = self.config.get('stale_data_days', 30)
        
        # Get predictive alerts
        alerts = get_predictive_alerts(
            trend_period_days=trend_period_days,
            forecast_horizon_days=forecast_horizon_days,
            growth_threshold=growth_threshold
        )
        
        # Get stale device alerts
        stale_alerts = detect_stale_devices(stale_days=stale_days)
        
        # Combine alerts
        all_alerts = alerts + stale_alerts
        
        # Count by severity
        high_priority = [a for a in all_alerts if a.get('severity') == 'high']
        medium_priority = [a for a in all_alerts if a.get('severity') == 'medium']
        low_priority = [a for a in all_alerts if a.get('severity') == 'low']
        
        # Count by type
        alert_types = {}
        for alert in all_alerts:
            alert_type = alert.get('type', 'unknown')
            alert_types[alert_type] = alert_types.get(alert_type, 0) + 1
        
        return {
            'total_alerts': len(all_alerts),
            'high_priority_count': len(high_priority),
            'medium_priority_count': len(medium_priority),
            'low_priority_count': len(low_priority),
            'high_priority_alerts': high_priority[:10],  # Top 10
            'medium_priority_alerts': medium_priority[:10],
            'low_priority_alerts': low_priority[:5],
            'alert_types': alert_types,
            'trend_period_days': trend_period_days,
            'forecast_horizon_days': forecast_horizon_days,
            'last_updated': timezone.now().isoformat(),
        }
