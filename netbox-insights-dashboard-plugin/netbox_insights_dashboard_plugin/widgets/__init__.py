"""Widget framework for NetBox Insights Dashboard."""

from .base import BaseWidget, register_widget, get_all_widgets
from .ipam_utilization import IPAMUtilizationWidget
from .device_health import DeviceHealthWidget
from .data_quality import DataQualityWidget
from .predictive_maintenance import PredictiveMaintenanceWidget
from .capacity_planning import CapacityPlanningWidget
from .topology_status import TopologyStatusWidget

__all__ = [
    'BaseWidget',
    'register_widget',
    'get_all_widgets',
    'IPAMUtilizationWidget',
    'DeviceHealthWidget',
    'DataQualityWidget',
    'PredictiveMaintenanceWidget',
    'CapacityPlanningWidget',
    'TopologyStatusWidget',
]
