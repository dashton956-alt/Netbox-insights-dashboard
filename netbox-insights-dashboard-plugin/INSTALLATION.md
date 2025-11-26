# Installation Guide

## Prerequisites

- **NetBox:** Version 4.0 or higher
- **Python:** Version 3.8 or higher  
- **Operating System:** RHEL 9, Rocky Linux 9, or compatible
- **Database:** PostgreSQL (NetBox requirement)
- **Permissions:** Root or sudo access for service restarts

## Installation Steps

### Step 1: Activate NetBox Virtual Environment

```bash
source /opt/netbox/venv/bin/activate
```

Verify you're in the correct environment:
```bash
which python3
# Should output: /opt/netbox/venv/bin/python3
```

### Step 2: Install the Plugin

```bash
pip install netbox-insights-dashboard-plugin
```

For development/testing from source:
```bash
cd /path/to/netbox-insights-dashboard-plugin
pip install -e .
```

### Step 3: Configure NetBox

Edit `/opt/netbox/netbox/netbox/configuration.py`:

```python
# Add to PLUGINS list
PLUGINS = [
    'netbox_insights_dashboard_plugin',
    # ... other plugins
]

# Add plugin configuration
PLUGINS_CONFIG = {
    'netbox_insights_dashboard_plugin': {
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
        'min_link_speed': 1000,
        
        # General Settings
        'enable_caching': True,
        'cache_ttl': 300,
        'enable_background_tasks': True,
    }
}
```

### Step 4: Run Database Migrations

```bash
cd /opt/netbox/netbox
python3 manage.py migrate netbox_insights_dashboard_plugin
```

Expected output:
```
Running migrations:
  Applying netbox_insights_dashboard_plugin.0001_initial... OK
```

### Step 5: Collect Static Files

```bash
python3 manage.py collectstatic --no-input
```

This copies CSS, JavaScript, and other static files to the configured static root.

### Step 6: Restart NetBox Services

```bash
sudo systemctl restart netbox netbox-rq
```

Verify services are running:
```bash
sudo systemctl status netbox
sudo systemctl status netbox-rq
```

Both should show `active (running)`.

### Step 7: Verify Installation

1. **Check plugin is loaded:**

```bash
cd /opt/netbox/netbox
python3 manage.py nbshell
```

In the shell:
```python
from django.conf import settings
print('netbox_insights_dashboard_plugin' in settings.PLUGINS)
# Should output: True
exit()
```

2. **Access the dashboard:**

- Log into NetBox UI
- Navigate to **Plugins** → **Insights Dashboard**
- You should see 6 widget cards loading data

3. **Check logs for errors:**

```bash
tail -f /opt/netbox/logs/netbox.log
```

## Troubleshooting

### Plugin Not Appearing in Menu

**Issue:** Plugin doesn't show in NetBox navigation

**Solutions:**
1. Verify plugin is in PLUGINS list: `grep netbox_insights_dashboard_plugin /opt/netbox/netbox/netbox/configuration.py`
2. Restart services: `sudo systemctl restart netbox netbox-rq`
3. Clear browser cache
4. Check NetBox logs for import errors

### Migration Errors

**Issue:** Database migration fails

**Solutions:**
1. Check PostgreSQL is running: `sudo systemctl status postgresql`
2. Verify NetBox database connectivity: `cd /opt/netbox/netbox && python3 manage.py showmigrations`
3. Check for conflicting migrations
4. Ensure proper permissions on NetBox database

### Static Files Not Loading

**Issue:** CSS/JS not loading (dashboard looks broken)

**Solutions:**
1. Re-run collectstatic: `python3 manage.py collectstatic --no-input --clear`
2. Verify STATIC_ROOT in configuration.py
3. Check nginx/Apache configuration for static file serving
4. Verify file permissions: `ls -l /opt/netbox/netbox/static/`

### Widgets Showing Errors

**Issue:** Widgets display error messages instead of data

**Solutions:**
1. Check for Python errors in logs: `tail -f /opt/netbox/logs/netbox.log`
2. Verify NetBox data exists (devices, prefixes, etc.)
3. Check API endpoints manually: `curl -H "Authorization: Token YOUR_TOKEN" http://localhost:8000/api/plugins/insights/ipam-utilization/summary/`
4. Verify cache backend is working (if Redis is used)

### Performance Issues

**Issue:** Dashboard loads slowly

**Solutions:**
1. Enable caching in configuration
2. Increase cache TTL values
3. Optimize database with: `cd /opt/netbox/netbox && python3 manage.py sqlsequencereset netbox_insights_dashboard_plugin`
4. Add database indexes if needed
5. Check PostgreSQL performance: `tail -f /var/lib/pgsql/data/log/postgresql-*.log`

## Upgrading

### To Upgrade to a Newer Version:

```bash
# Activate venv
source /opt/netbox/venv/bin/activate

# Upgrade plugin
pip install --upgrade netbox-insights-dashboard-plugin

# Run migrations
cd /opt/netbox/netbox
python3 manage.py migrate netbox_insights_dashboard_plugin

# Collect static files
python3 manage.py collectstatic --no-input

# Restart services
sudo systemctl restart netbox netbox-rq
```

## Uninstalling

### To Remove the Plugin:

```bash
# Remove from configuration.py PLUGINS list
# Then:

# Activate venv
source /opt/netbox/venv/bin/activate

# Uninstall package
pip uninstall netbox-insights-dashboard-plugin

# Restart services
sudo systemctl restart netbox netbox-rq
```

**Note:** Database tables will remain. To remove them:
```bash
cd /opt/netbox/netbox
python3 manage.py migrate netbox_insights_dashboard_plugin zero
```

## Docker Installation

For NetBox running in Docker:

1. Add to `plugin_requirements.txt`:
```
netbox-insights-dashboard-plugin
```

2. Add to `configuration/plugins.py`:
```python
PLUGINS = ['netbox_insights_dashboard_plugin']
PLUGINS_CONFIG = { ... }
```

3. Rebuild container:
```bash
docker-compose down
docker-compose build --no-cache netbox
docker-compose up -d
```

4. Run migrations:
```bash
docker-compose exec netbox python manage.py migrate netbox_insights_dashboard_plugin
docker-compose exec netbox python manage.py collectstatic --no-input
```

## System Requirements

### Minimum Requirements
- CPU: 2 cores
- RAM: 4 GB
- Disk: 10 GB free space
- Network: 100 Mbps

### Recommended for Production
- CPU: 4+ cores
- RAM: 8+ GB
- Disk: 50+ GB (SSD preferred)
- Network: 1 Gbps

## Support

If you encounter issues:

1. Check NetBox logs: `/opt/netbox/logs/netbox.log`
2. Review plugin documentation
3. Search GitHub issues
4. Ask in NetBox Slack community
5. Create a GitHub issue with:
   - NetBox version
   - Plugin version
   - Error messages
   - Steps to reproduce

## Next Steps

After successful installation:

1. Review [CONFIGURATION.md](CONFIGURATION.md) for detailed configuration options
2. Explore each widget in the dashboard
3. Set up API access for external integrations
4. Configure alerting thresholds for your environment
5. Schedule background tasks for data collection (optional)

---

**Installation complete! 🎉**
