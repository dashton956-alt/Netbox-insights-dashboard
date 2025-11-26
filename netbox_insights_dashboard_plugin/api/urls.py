"""API URL routing for NetBox Insights Dashboard."""

from rest_framework.routers import DefaultRouter
from .views import (
    DeviceHealthMetricViewSet,
    IPAMUtilizationViewSet,
    CustomMetricViewSet,
    VendorIntegrationViewSet,
    InsightsAPIViewSet,
)

router = DefaultRouter()
router.register('device-health', DeviceHealthMetricViewSet)
router.register('ipam-utilization', IPAMUtilizationViewSet)
router.register('custom-metrics', CustomMetricViewSet)
router.register('vendor-integrations', VendorIntegrationViewSet)
router.register('insights', InsightsAPIViewSet, basename='insights')

urlpatterns = router.urls
