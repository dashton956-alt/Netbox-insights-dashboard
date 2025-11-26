"""API Views for NetBox Insights Dashboard."""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from netbox.api.viewsets import NetBoxModelViewSet
from ..models import DeviceHealthMetric, IPAMUtilization, CustomMetric, VendorIntegration
from ..utils.calculations import get_ipam_utilization_summary
from ..utils.predictions import get_predictive_alerts
from ..utils.validators import calculate_data_quality_score
from .serializers import (
    DeviceHealthMetricSerializer,
    IPAMUtilizationSerializer,
    CustomMetricSerializer,
    VendorIntegrationSerializer,
    IPAMUtilizationSummarySerializer,
    DeviceHealthSummarySerializer,
    PredictiveAlertSerializer,
)


class DeviceHealthMetricViewSet(NetBoxModelViewSet):
    """API viewset for DeviceHealthMetric."""
    
    queryset = DeviceHealthMetric.objects.all()
    serializer_class = DeviceHealthMetricSerializer


class IPAMUtilizationViewSet(NetBoxModelViewSet):
    """API viewset for IPAMUtilization."""
    
    queryset = IPAMUtilization.objects.all()
    serializer_class = IPAMUtilizationSerializer
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get IPAM utilization summary."""
        site_id = request.query_params.get('site_id')
        warning_threshold = float(request.query_params.get('warning_threshold', 75))
        critical_threshold = float(request.query_params.get('critical_threshold', 90))
        
        summary = get_ipam_utilization_summary(
            site_id=site_id,
            warning_threshold=warning_threshold,
            critical_threshold=critical_threshold
        )
        
        # Serialize prefix data
        serializer = IPAMUtilizationSummarySerializer(summary['prefixes'], many=True)
        
        return Response({
            'total_prefixes': summary['total_prefixes'],
            'warning_count': summary['warning_count'],
            'critical_count': summary['critical_count'],
            'healthy_count': summary['healthy_count'],
            'prefixes': serializer.data,
            'calculated_at': summary['calculated_at'],
        })


class CustomMetricViewSet(NetBoxModelViewSet):
    """API viewset for CustomMetric."""
    
    queryset = CustomMetric.objects.all()
    serializer_class = CustomMetricSerializer


class VendorIntegrationViewSet(NetBoxModelViewSet):
    """API viewset for VendorIntegration."""
    
    queryset = VendorIntegration.objects.all()
    serializer_class = VendorIntegrationSerializer


class InsightsAPIViewSet(viewsets.ViewSet):
    """
    API endpoints for insights dashboard data.
    
    Provides high-level aggregated data for external integrations.
    """
    
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def predictive_alerts(self, request):
        """Get predictive maintenance alerts."""
        trend_period_days = int(request.query_params.get('trend_period_days', 90))
        forecast_horizon_days = int(request.query_params.get('forecast_horizon_days', 180))
        growth_threshold = float(request.query_params.get('growth_threshold', 5.0))
        
        alerts = get_predictive_alerts(
            trend_period_days=trend_period_days,
            forecast_horizon_days=forecast_horizon_days,
            growth_threshold=growth_threshold
        )
        
        serializer = PredictiveAlertSerializer(alerts, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def data_quality(self, request):
        """Get data quality score and details."""
        required_fields = request.query_params.getlist('required_fields')
        if not required_fields:
            required_fields = ['name', 'site', 'status']
        
        quality_data = calculate_data_quality_score(
            required_fields=required_fields,
            naming_patterns={}
        )
        
        return Response(quality_data)
    
    @action(detail=False, methods=['post'])
    def webhook(self, request):
        """
        Webhook endpoint for external automation tools.
        
        Accepts custom metrics and events from external systems.
        """
        source = request.data.get('source')
        event = request.data.get('event')
        metadata = request.data.get('metadata', {})
        
        if not source or not event:
            return Response(
                {'error': 'source and event are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create custom metric
        metric = CustomMetric.objects.create(
            metric_name=f"{source}_{event}",
            metric_type='event',
            value=metadata,
            source=source
        )
        
        serializer = CustomMetricSerializer(metric)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
