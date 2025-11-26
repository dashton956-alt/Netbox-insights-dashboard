"""Views for NetBox Insights Dashboard Plugin."""

from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import JsonResponse
from django.views import View

from .widgets import get_all_widgets


class DashboardView(LoginRequiredMixin, TemplateView):
    """
    Main dashboard view displaying all enabled widgets.
    """
    template_name = 'netbox_insights_dashboard_plugin/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get all registered widgets
        widget_classes = get_all_widgets()
        
        # Instantiate and render each widget
        widgets = []
        for WidgetClass in widget_classes:
            widget = WidgetClass(request=self.request)
            if widget.is_enabled():
                widgets.append(widget.render())
        
        # Sort by order
        widgets.sort(key=lambda w: w['order'])
        
        context['widgets'] = widgets
        context['page_title'] = 'Insights Dashboard'
        
        return context


class ConfigurationView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    """
    Configuration view for dashboard settings.
    """
    template_name = 'netbox_insights_dashboard_plugin/config.html'
    permission_required = 'netbox_insights_dashboard_plugin.change_config'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Dashboard Configuration'
        return context


class BaseWidgetView(LoginRequiredMixin, View):
    """Base view for widget AJAX data endpoints."""
    
    widget_class = None
    
    def get(self, request, *args, **kwargs):
        """Return widget data as JSON."""
        if not self.widget_class:
            return JsonResponse({'error': 'No widget class specified'}, status=400)
        
        try:
            widget = self.widget_class(request=request)
            
            if not widget.is_enabled():
                return JsonResponse({'error': 'Widget is disabled'}, status=403)
            
            data = widget.get_context_data()
            return JsonResponse(data, safe=False)
        except Exception as e:
            # Log the error for debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error loading widget {self.widget_class.__name__}: {str(e)}", exc_info=True)
            
            return JsonResponse({
                'error': 'Failed to load widget data',
                'details': str(e) if settings.DEBUG else 'Internal server error'
            }, status=500)


class IPAMUtilizationWidgetView(BaseWidgetView):
    """AJAX endpoint for IPAM Utilization widget data."""
    
    def get(self, request, *args, **kwargs):
        from .widgets.ipam_utilization import IPAMUtilizationWidget
        self.widget_class = IPAMUtilizationWidget
        return super().get(request, *args, **kwargs)


class DeviceHealthWidgetView(BaseWidgetView):
    """AJAX endpoint for Device Health widget data."""
    
    def get(self, request, *args, **kwargs):
        from .widgets.device_health import DeviceHealthWidget
        self.widget_class = DeviceHealthWidget
        return super().get(request, *args, **kwargs)


class DataQualityWidgetView(BaseWidgetView):
    """AJAX endpoint for Data Quality widget data."""
    
    def get(self, request, *args, **kwargs):
        from .widgets.data_quality import DataQualityWidget
        self.widget_class = DataQualityWidget
        return super().get(request, *args, **kwargs)


class PredictiveMaintenanceWidgetView(BaseWidgetView):
    """AJAX endpoint for Predictive Maintenance widget data."""
    
    def get(self, request, *args, **kwargs):
        from .widgets.predictive_maintenance import PredictiveMaintenanceWidget
        self.widget_class = PredictiveMaintenanceWidget
        return super().get(request, *args, **kwargs)


class CapacityPlanningWidgetView(BaseWidgetView):
    """AJAX endpoint for Capacity Planning widget data."""
    
    def get(self, request, *args, **kwargs):
        from .widgets.capacity_planning import CapacityPlanningWidget
        self.widget_class = CapacityPlanningWidget
        return super().get(request, *args, **kwargs)


class HealthCheckView(View):
    """Simple health check endpoint for monitoring."""
    
    def get(self, request, *args, **kwargs):
        """Return plugin health status."""
        from django.db import connection
        from django.core.cache import cache
        
        health_status = {
            'status': 'healthy',
            'timestamp': timezone.now().isoformat(),
            'version': '1.0.0',
            'checks': {}
        }
        
        # Check database connectivity
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            health_status['checks']['database'] = 'ok'
        except Exception as e:
            health_status['checks']['database'] = f'error: {str(e)}'
            health_status['status'] = 'unhealthy'
        
        # Check cache
        try:
            cache.set('health_check', 'ok', 10)
            cache_value = cache.get('health_check')
            if cache_value == 'ok':
                health_status['checks']['cache'] = 'ok'
            else:
                health_status['checks']['cache'] = 'error: cache not working'
                health_status['status'] = 'unhealthy'
        except Exception as e:
            health_status['checks']['cache'] = f'error: {str(e)}'
            health_status['status'] = 'unhealthy'
        
        # Check widgets
        try:
            widget_classes = get_all_widgets()
            health_status['checks']['widgets'] = f'{len(widget_classes)} widgets loaded'
        except Exception as e:
            health_status['checks']['widgets'] = f'error: {str(e)}'
            health_status['status'] = 'unhealthy'
        
        status_code = 200 if health_status['status'] == 'healthy' else 503
        return JsonResponse(health_status, status=status_code)
