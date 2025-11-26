"""Data Quality & Compliance Widget."""

from typing import Dict
from django.utils import timezone
from .base import BaseWidget, register_widget
from ..utils.validators import (
    calculate_data_quality_score,
    validate_cable_connections,
    get_data_quality_recommendations
)
from ..utils.cache import cached_widget_data


@register_widget
class DataQualityWidget(BaseWidget):
    """
    Widget displaying overall data quality and compliance metrics.
    
    Features:
    - Overall data quality score (0-100%)
    - Required field compliance tracking
    - Naming convention validation
    - Duplicate detection
    - Actionable recommendations
    """
    
    slug = "data_quality"
    name = "Data Quality & Compliance"
    description = "Monitor data completeness, accuracy, and compliance"
    icon = "✅"
    template = "netbox_insights_dashboard_plugin/widgets/data_quality.html"
    refresh_interval = 600
    order = 3
    
    @cached_widget_data(timeout=600)
    def get_context_data(self) -> Dict:
        """Get data quality metrics."""
        # Get configuration
        required_fields = self.config.get('required_fields', ['name', 'site', 'status'])
        naming_patterns = self.config.get('naming_conventions', {})
        min_quality_score = self.config.get('min_quality_score', 80)
        
        # Calculate overall quality score
        quality_data = calculate_data_quality_score(
            required_fields=required_fields,
            naming_patterns=naming_patterns
        )
        
        # Validate cable connections
        cable_validation = validate_cable_connections()
        
        # Get recommendations
        recommendations = get_data_quality_recommendations()
        
        # Determine status
        score = quality_data['score']
        if score >= min_quality_score:
            status = 'healthy'
            status_emoji = '🟢'
        elif score >= 60:
            status = 'warning'
            status_emoji = '🟡'
        else:
            status = 'critical'
            status_emoji = '🔴'
        
        # Prepare issue summary (limit each category)
        issues_summary = {
            'missing_fields': quality_data['issues']['missing_fields'][:10],
            'naming_violations': quality_data['issues']['naming_violations'][:10],
            'duplicate_serials': quality_data['issues']['duplicate_serials'][:5],
            'duplicate_macs': quality_data['issues']['duplicate_macs'][:5],
            'missing_primary_ip': quality_data['issues']['missing_primary_ip'][:10],
            'no_interfaces': quality_data['issues']['no_interfaces'][:10],
        }
        
        return {
            'quality_score': score,
            'status': status,
            'status_emoji': status_emoji,
            'min_score': min_quality_score,
            'total_devices': quality_data['total_devices'],
            'compliant_devices': quality_data['compliant_devices'],
            'non_compliant_devices': quality_data['non_compliant_devices'],
            'total_issues': quality_data['total_issues'],
            'issue_counts': quality_data['details'],
            'issues': issues_summary,
            'cable_validation': cable_validation,
            'recommendations': recommendations[:5],  # Top 5 recommendations
            'last_updated': timezone.now().isoformat(),
        }
