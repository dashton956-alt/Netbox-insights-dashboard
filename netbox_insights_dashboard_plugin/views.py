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
        
        widget = self.widget_class(request=request)
        
        if not widget.is_enabled():
            return JsonResponse({'error': 'Widget is disabled'}, status=403)
        
        try:
            data = widget.get_context_data()
            return JsonResponse(data, safe=False)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


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


class TopologyStatusWidgetView(BaseWidgetView):
    """AJAX endpoint for Topology Status widget data."""
    
    def get(self, request, *args, **kwargs):
        from .widgets.topology_status import TopologyStatusWidget
        self.widget_class = TopologyStatusWidget
        return super().get(request, *args, **kwargs)
