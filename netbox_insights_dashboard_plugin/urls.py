"""URL routing for NetBox Insights Dashboard."""

from django.urls import path, include
from . import views

app_name = 'netbox_insights_dashboard_plugin'

urlpatterns = [
    # Main dashboard view
    path('', views.DashboardView.as_view(), name='dashboard'),
    
    # Configuration
    path('config/', views.ConfigurationView.as_view(), name='config'),
    
    # Widget data endpoints (AJAX refresh)
    path('widgets/ipam-utilization/', views.IPAMUtilizationWidgetView.as_view(), name='widget_ipam'),
    path('widgets/device-health/', views.DeviceHealthWidgetView.as_view(), name='widget_device_health'),
    path('widgets/data-quality/', views.DataQualityWidgetView.as_view(), name='widget_data_quality'),
    path('widgets/predictive/', views.PredictiveMaintenanceWidgetView.as_view(), name='widget_predictive'),
    path('widgets/capacity/', views.CapacityPlanningWidgetView.as_view(), name='widget_capacity'),
    path('widgets/topology/', views.TopologyStatusWidgetView.as_view(), name='widget_topology'),
    
    # Health check endpoint
    path('health/', views.HealthCheckView.as_view(), name='health_check'),
    
    # API endpoints
    path('api/', include('netbox_insights_dashboard_plugin.api.urls')),
]
