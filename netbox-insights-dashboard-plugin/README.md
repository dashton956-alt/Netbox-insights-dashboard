# NetBox Insights Dashboard Plugin

**Universal analytics and operational visibility dashboard for NetBox with vendor-agnostic architecture**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![NetBox Version](https://img.shields.io/badge/netbox-4.0%2B-blue)](https://github.com/netbox-community/netbox)

## 🎯 Overview

NetBox Insights Dashboard is a powerful NetBox plugin that provides comprehensive operational visibility into your network infrastructure. Built with a vendor-agnostic architecture, it works seamlessly with any network vendor through extensible plugin architecture.

### Key Features

- **📊 6 Core Widgets** - IPAM utilization, device health, data quality, predictive maintenance, capacity planning, and topology status
- **🚀 Zero Configuration Start** - Works immediately after installation with sensible defaults
- **🔌 Vendor Agnostic** - Supports any network vendor (Cisco, Juniper, Arista, etc.)
- **📈 Predictive Analytics** - Trend-based forecasting and proactive alerts
- **🎨 Modern UI** - Responsive dashboard with auto-refresh and color-coded status indicators
- **🔐 REST API** - Full API for external integrations and automation
- **⚡ Performance Optimized** - Built-in caching and efficient database queries

## 🚀 Quick Start

### Prerequisites

- NetBox 4.0 or higher
- Python 3.8 or higher


### Installation

1. **Activate NetBox virtual environment:**

```bash
source /opt/netbox/venv/bin/activate
```

2. **Install the plugin:**

```bash
pip install netbox-insights-dashboard-plugin
```

3. **Add to NetBox configuration:**

Edit `/opt/netbox/netbox/netbox/configuration.py`:

```python
PLUGINS = [
    'netbox_insights_dashboard_plugin',
]

PLUGINS_CONFIG = {
    'netbox_insights_dashboard_plugin': {
        'ipam_warning_threshold': 75,
        'ipam_critical_threshold': 90,
        'stale_data_days': 30,
        'trend_period_days': 90,
    }
}
```

4. **Run database migrations:**

```bash
cd /opt/netbox/netbox
python3 manage.py migrate netbox_insights_dashboard_plugin
```

5. **Collect static files:**

```bash
python3 manage.py collectstatic --no-input
```

6. **Restart NetBox services:**

```bash
sudo systemctl restart netbox netbox-rq
```

7. **Access the dashboard:**

Navigate to **Plugins → Insights Dashboard** in the NetBox UI.

## 📊 Dashboard Widgets

### 1. IPAM Utilization Dashboard 🌐
Monitor IP address and VLAN usage with color-coded threshold alerts.

### 2. Device Health Monitor 💚
Track device health scores and identify data completeness issues.

### 3. Data Quality & Compliance ✅
Monitor data quality with compliance scoring and validation.

### 4. Predictive Maintenance 🔮
Proactive alerts based on trend analysis and capacity forecasting.

### 5. Capacity Planning 📈
Track growth trends and forecast future capacity requirements.

### 6. Network Topology Status 🔗
Monitor network connectivity, cables, and topology health.

## 🔧 Configuration

Basic configuration example:

```python
PLUGINS_CONFIG = {
    'netbox_insights_dashboard_plugin': {
        # IPAM Settings
        'ipam_warning_threshold': 75,
        'ipam_critical_threshold': 90,
        
        # Device Health
        'stale_data_days': 30,
        
        # Predictive Maintenance
        'trend_period_days': 90,
        'forecast_horizon_days': 180,
        
        # Performance
        'enable_caching': True,
        'cache_ttl': 300,
    }
}
```

## 🌐 REST API

The plugin provides a full REST API for external integrations:

```bash
# Get IPAM utilization summary
GET /api/plugins/insights/ipam-utilization/summary/

# Get predictive alerts
GET /api/plugins/insights/insights/predictive_alerts/

# Get data quality score
GET /api/plugins/insights/insights/data_quality/

# Push custom metrics (webhook)
POST /api/plugins/insights/insights/webhook/
```

## Compatibility

| NetBox Version | Plugin Version |
|----------------|----------------|
|     4.0+       |      1.0.0     |
|     4.4+       |      1.0.0     |

## 📚 Documentation

- `INSTALLATION.md` - Detailed installation guide
- `CONFIGURATION.md` - Configuration reference
- Plugin Admin → Configuration for current settings

## 🤝 Contributing

Contributions are welcome! Please see `CONTRIBUTING.md` for guidelines.

## 📄 License

This project is licensed under the MIT License - see the `LICENSE` file for details.

## Credits

This package was created with [Cookiecutter](https://github.com/audreyr/cookiecutter) and the [`netbox-community/cookiecutter-netbox-plugin`](https://github.com/netbox-community/cookiecutter-netbox-plugin) project template.

---

**Made with ❤️ for the NetBox community**
