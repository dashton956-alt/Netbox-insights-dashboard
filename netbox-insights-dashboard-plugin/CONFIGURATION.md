# Configuration Reference

Complete configuration guide for NetBox Insights Dashboard Plugin.

## Configuration Location

All configuration is managed through NetBox's `configuration.py` file:

```
/opt/netbox/netbox/netbox/configuration.py
```

## Full Configuration Example

```python
PLUGINS_CONFIG = {
    'netbox_insights_dashboard_plugin': {
        # ======================
        # IPAM Widget Settings
        # ======================
        'ipam_warning_threshold': 75,           # Warning at 75% utilization
        'ipam_critical_threshold': 90,          # Critical at 90% utilization
        'ipam_refresh_interval': 60,            # Refresh every 60 seconds
        
        # ======================
        # Device Health Settings
        # ======================
        'stale_data_days': 30,                  # Consider data stale after 30 days
        'required_device_fields': [              # Fields that must be populated
            'site',
            'device_role',
            'device_type',
            'primary_ip4',
        ],
        'health_refresh_interval': 300,         # Refresh every 5 minutes
        
        # ======================
        # Data Quality Settings
        # ======================
        'min_quality_score': 80,                # Target quality score
        'naming_conventions': {                  # Regex patterns for validation
            'device_name': r'^[a-z]{3}-[a-z]{3}-[0-9]{2}$',  # Example: nyc-rtr-01
            'interface_name': r'^(Gi|Te|Eth)\d+/\d+(/\d+)?$',  # Example: Gi0/1
        },
        'required_fields': [                     # Required fields for compliance
            'name',
            'site',
            'status',
        ],
        
        # ======================
        # Predictive Maintenance Settings
        # ======================
        'trend_period_days': 90,                # Analyze trends over 90 days
        'forecast_horizon_days': 180,           # Forecast 6 months ahead
        'growth_rate_threshold': 5.0,           # Alert if growth > 5% per week
        
        # ======================
        # Capacity Planning Settings
        # ======================
        'historical_period_days': 90,           # Historical analysis period
        'capacity_warning_threshold': 80,       # Warn at 80% capacity
        
        # ======================
        # Topology Settings
        # ======================
        'show_inter_site_only': True,           # Show only inter-site links
        'min_link_speed': 1000,                 # Minimum link speed in Mbps
        
        # ======================
        # General Settings
        # ======================
        'enable_caching': True,                 # Enable widget data caching
        'cache_ttl': 300,                       # Cache TTL in seconds (5 min)
        'enable_background_tasks': True,        # Enable background data collection
    }
}
```

## Configuration Options Detailed

### IPAM Widget

#### `ipam_warning_threshold`
- **Type:** Integer (0-100)
- **Default:** 75
- **Description:** Percentage at which prefix utilization shows warning status (yellow)
- **Example:** `'ipam_warning_threshold': 80` - Warn at 80% utilization

#### `ipam_critical_threshold`
- **Type:** Integer (0-100)
- **Default:** 90
- **Description:** Percentage at which prefix utilization shows critical status (red)
- **Example:** `'ipam_critical_threshold': 95` - Critical at 95% utilization

#### `ipam_refresh_interval`
- **Type:** Integer (seconds)
- **Default:** 60
- **Description:** How often the IPAM widget refreshes data
- **Example:** `'ipam_refresh_interval': 120` - Refresh every 2 minutes

### Device Health Widget

#### `stale_data_days`
- **Type:** Integer (days)
- **Default:** 30
- **Description:** Number of days before device data is considered stale
- **Example:** `'stale_data_days': 45` - Flag devices not updated in 45 days

#### `required_device_fields`
- **Type:** List of strings
- **Default:** `['site', 'device_role', 'device_type']`
- **Description:** Fields that must be populated for a device to be considered "healthy"
- **Example:** 
```python
'required_device_fields': [
    'site',
    'device_role',
    'device_type',
    'primary_ip4',
    'serial',
    'asset_tag',
]
```

#### `health_refresh_interval`
- **Type:** Integer (seconds)
- **Default:** 300
- **Description:** How often the device health widget refreshes
- **Example:** `'health_refresh_interval': 600` - Refresh every 10 minutes

### Data Quality Widget

#### `min_quality_score`
- **Type:** Integer (0-100)
- **Default:** 80
- **Description:** Target quality score percentage
- **Example:** `'min_quality_score': 90` - Aim for 90% compliance

#### `naming_conventions`
- **Type:** Dictionary (field_name: regex_pattern)
- **Default:** `{}`
- **Description:** Regex patterns to validate naming conventions
- **Example:**
```python
'naming_conventions': {
    'device_name': r'^[a-z]{3}-[a-z]{3}-\d{2}$',      # site-role-##
    'site_name': r'^[A-Z]{3}$',                        # Three letter code
    'interface_name': r'^(Gi|Te|Eth)\d+/\d+$',        # Interface format
}
```

#### `required_fields`
- **Type:** List of strings
- **Default:** `['name', 'site', 'status']`
- **Description:** Fields that must be populated for compliance
- **Example:**
```python
'required_fields': [
    'name',
    'site',
    'status',
    'tenant',
    'description',
]
```

### Predictive Maintenance Widget

#### `trend_period_days`
- **Type:** Integer (7-365)
- **Default:** 90
- **Description:** Number of days to analyze for trend calculation
- **Example:** `'trend_period_days': 180` - Analyze 6 months of data

#### `forecast_horizon_days`
- **Type:** Integer (30-730)
- **Default:** 180
- **Description:** How far ahead to forecast capacity needs
- **Example:** `'forecast_horizon_days': 365` - Forecast 1 year ahead

#### `growth_rate_threshold`
- **Type:** Float (percentage)
- **Default:** 5.0
- **Description:** Minimum growth rate (% per week) to trigger alerts
- **Example:** `'growth_rate_threshold': 10.0` - Alert if growth > 10%/week

### Capacity Planning Widget

#### `historical_period_days`
- **Type:** Integer (30-365)
- **Default:** 90
- **Description:** Historical period for capacity analysis
- **Example:** `'historical_period_days': 180` - Analyze 6 months of history

#### `capacity_warning_threshold`
- **Type:** Integer (0-100)
- **Default:** 80
- **Description:** Percentage at which capacity warnings are generated
- **Example:** `'capacity_warning_threshold': 85` - Warn at 85% capacity

### Topology Widget

#### `show_inter_site_only`
- **Type:** Boolean
- **Default:** True
- **Description:** Show only links between sites (hide intra-site links)
- **Example:** `'show_inter_site_only': False` - Show all links

#### `min_link_speed`
- **Type:** Integer (Mbps)
- **Default:** 1000
- **Description:** Minimum link speed to display (in Mbps)
- **Example:** `'min_link_speed': 10000` - Show only 10G+ links

### General Settings

#### `enable_caching`
- **Type:** Boolean
- **Default:** True
- **Description:** Enable caching of widget data for performance
- **Example:** `'enable_caching': False` - Disable caching for troubleshooting

#### `cache_ttl`
- **Type:** Integer (seconds)
- **Default:** 300
- **Description:** How long to cache widget data
- **Example:** `'cache_ttl': 600` - Cache for 10 minutes

#### `enable_background_tasks`
- **Type:** Boolean
- **Default:** True
- **Description:** Enable background data collection tasks
- **Example:** `'enable_background_tasks': False` - Disable background tasks

## Environment-Specific Configurations

### Small Environment (<100 devices)

```python
PLUGINS_CONFIG = {
    'netbox_insights_dashboard_plugin': {
        'ipam_warning_threshold': 75,
        'ipam_critical_threshold': 90,
        'stale_data_days': 30,
        'trend_period_days': 30,           # Shorter trend period
        'forecast_horizon_days': 90,       # Shorter forecast
        'enable_caching': False,            # Caching not needed
        'cache_ttl': 60,
    }
}
```

### Medium Environment (100-500 devices)

```python
PLUGINS_CONFIG = {
    'netbox_insights_dashboard_plugin': {
        'ipam_warning_threshold': 75,
        'ipam_critical_threshold': 90,
        'stale_data_days': 30,
        'trend_period_days': 90,
        'forecast_horizon_days': 180,
        'enable_caching': True,
        'cache_ttl': 300,                  # 5 minutes
    }
}
```

### Large Environment (500+ devices)

```python
PLUGINS_CONFIG = {
    'netbox_insights_dashboard_plugin': {
        'ipam_warning_threshold': 80,      # Higher thresholds
        'ipam_critical_threshold': 95,
        'stale_data_days': 14,             # Stricter staleness check
        'trend_period_days': 90,
        'forecast_horizon_days': 365,      # Longer forecast
        'enable_caching': True,
        'cache_ttl': 600,                  # 10 minutes
        'health_refresh_interval': 600,    # Longer refresh intervals
    }
}
```

## Advanced Configuration

### Custom Naming Patterns

```python
'naming_conventions': {
    # Device naming: location-function-number
    # Example: nyc-rtr-01, lax-sw-02
    'device_name': r'^[a-z]{3}-[a-z]{3}-\d{2}$',
    
    # Site naming: Three letter airport code
    # Example: JFK, LAX, ORD
    'site_name': r'^[A-Z]{3}$',
    
    # Interface naming: Type + slot/port
    # Example: GigabitEthernet0/1, TenGigabitEthernet1/1/1
    'interface_name': r'^(GigabitEthernet|TenGigabitEthernet|Ethernet)\d+/\d+(/\d+)?$',
    
    # Prefix description: Descriptive name
    # Example: Management Network, User VLANs
    'prefix_description': r'^[A-Z][a-zA-Z\s]+$',
}
```

### Multiple Required Fields

```python
'required_device_fields': [
    'site',                # Physical location
    'device_role',         # Role in network
    'device_type',         # Hardware model
    'platform',            # OS platform
    'serial',              # Serial number
    'asset_tag',           # Asset tag
    'primary_ip4',         # IPv4 management address
],
```

## Applying Configuration Changes

After modifying `configuration.py`:

```bash
# Restart NetBox services
sudo systemctl restart netbox netbox-rq

# Clear cache (if needed)
cd /opt/netbox/netbox
python3 manage.py shell
>>> from django.core.cache import cache
>>> cache.clear()
>>> exit()
```

## Viewing Current Configuration

Access via NetBox UI:
- Navigate to **Plugins** → **Insights Dashboard** → **Configuration**

Or via Python shell:
```bash
cd /opt/netbox/netbox
python3 manage.py nbshell
```

```python
from django.conf import settings
config = settings.PLUGINS_CONFIG.get('netbox_insights_dashboard_plugin', {})
print(config)
```

## Best Practices

1. **Start with defaults** - Use default values initially, then adjust based on your needs
2. **Monitor performance** - Watch for slow widget loads and adjust cache settings
3. **Customize thresholds** - Set IPAM thresholds based on your IP space management practices
4. **Document changes** - Comment your configuration.py with reasons for non-default values
5. **Test in dev first** - Try configuration changes in a dev environment before production
6. **Version control** - Keep configuration.py in version control (excluding secrets)

## Troubleshooting

### Changes Not Taking Effect

```bash
# Verify configuration syntax
cd /opt/netbox/netbox
python3 -c "from netbox import configuration; print('OK')"

# Restart services
sudo systemctl restart netbox netbox-rq

# Check for errors
tail -f /opt/netbox/logs/netbox.log
```

### Widget Performance Issues

- Increase `cache_ttl` values
- Reduce refresh intervals
- Decrease `trend_period_days` for faster calculations
- Enable caching if disabled

### Validation Errors

- Check regex patterns with: https://regex101.com/
- Test naming conventions on sample data first
- Review error messages in widget displays

---

**Need help?** Check the GitHub issues or NetBox community Slack.
