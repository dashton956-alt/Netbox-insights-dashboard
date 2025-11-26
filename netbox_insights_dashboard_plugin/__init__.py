"""NetBox Insights Dashboard Plugin - Universal analytics and operational visibility dashboard."""

__author__ = """Dan Ashton"""
__email__ = "dashton956@gmail.com"
__version__ = "1.0.0"


from netbox.plugins import PluginConfig


class InsightsDashboardConfig(PluginConfig):
    """NetBox plugin configuration for Insights Dashboard."""
    
    name = "netbox_insights_dashboard_plugin"
    verbose_name = "NetBox Insights Dashboard"
    description = "Universal analytics and operational visibility dashboard for NetBox with vendor-agnostic architecture"
    version = __version__
    author = __author__
    author_email = __email__
    base_url = "insights"
    required_settings = []
    min_version = '4.0.0'
    max_version = '4.9.99'
    default_settings = {
        # IPAM Widget Settings
        'ipam_warning_threshold': 75,
        'ipam_critical_threshold': 90,
        'ipam_refresh_interval': 60,
        
        # Device Health Settings
        'stale_data_days': 30,
        'required_device_fields': ['site', 'device_role', 'device_type'],
        'health_refresh_interval': 300,
        
        # Data Quality Settings
        'min_quality_score': 80,
        'naming_conventions': {},
        'required_fields': ['name', 'site', 'status'],
        
        # Predictive Maintenance Settings
        'trend_period_days': 90,
        'forecast_horizon_days': 180,
        'growth_rate_threshold': 5.0,
        
        # Capacity Planning Settings
        'historical_period_days': 90,
        'capacity_warning_threshold': 80,
        
        # Topology Settings
        'show_inter_site_only': True,
        'min_link_speed': 1000,  # 1G in Mbps
        
        # General Settings
        'enable_caching': True,
        'cache_ttl': 300,
        'enable_background_tasks': True,
    }


config = InsightsDashboardConfig
