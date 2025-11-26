#!/usr/bin/env python

"""Tests for `netbox_insights_dashboard_plugin` package."""

import pytest
from netbox_insights_dashboard_plugin import netbox_insights_dashboard_plugin


def test_plugin_import():
    """Test that the plugin can be imported."""
    assert netbox_insights_dashboard_plugin is not None


def test_plugin_config():
    """Test that plugin configuration is valid."""
    from netbox_insights_dashboard_plugin import config
    assert config.name == "netbox_insights_dashboard_plugin"
    assert config.verbose_name == "NetBox Insights Dashboard"
    assert config.version == "1.0.0"


@pytest.mark.django_db
def test_models():
    """Test that models can be imported and used."""
    from netbox_insights_dashboard_plugin.models import (
        DeviceHealthMetric, IPAMUtilization, CustomMetric, VendorIntegration
    )
    
    # Test model definitions exist
    assert DeviceHealthMetric
    assert IPAMUtilization
    assert CustomMetric
    assert VendorIntegration


def test_widgets():
    """Test that widgets can be loaded."""
    from netbox_insights_dashboard_plugin.widgets import get_all_widgets
    
    widgets = get_all_widgets()
    assert len(widgets) == 6  # Should have 6 widgets
    
    widget_slugs = [w.slug for w in widgets]
    expected_slugs = [
        'ipam-utilization', 'device-health', 'data-quality',
        'predictive-maintenance', 'capacity-planning', 'topology-status'
    ]
    
    for slug in expected_slugs:
        assert slug in widget_slugs


def test_utils():
    """Test utility functions."""
    from netbox_insights_dashboard_plugin.utils.calculations import calculate_prefix_utilization
    from netbox_insights_dashboard_plugin.utils.cache import get_cache_key
    
    # Test cache key generation
    key = get_cache_key("test", "arg1", "arg2", kwarg1="value1")
    assert "test" in key
    assert "arg1" in key
    assert "arg2" in key
    assert "kwarg1:value1" in key
