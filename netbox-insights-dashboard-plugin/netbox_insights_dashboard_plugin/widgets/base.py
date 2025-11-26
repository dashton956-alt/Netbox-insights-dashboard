"""Base widget class and registry for NetBox Insights Dashboard."""

from typing import Dict, List, Type
from abc import ABC, abstractmethod
from django.conf import settings


# Widget registry
_widget_registry: Dict[str, Type['BaseWidget']] = {}


def register_widget(cls: Type['BaseWidget']) -> Type['BaseWidget']:
    """
    Decorator to register a widget class.
    
    Usage:
        @register_widget
        class MyWidget(BaseWidget):
            pass
    """
    _widget_registry[cls.slug] = cls
    return cls


def get_all_widgets() -> List[Type['BaseWidget']]:
    """Get all registered widgets."""
    return list(_widget_registry.values())


def get_widget(slug: str) -> Type['BaseWidget']:
    """Get a widget by slug."""
    return _widget_registry.get(slug)


class BaseWidget(ABC):
    """
    Base class for dashboard widgets.
    
    All widgets must inherit from this class and implement:
    - slug: Unique identifier
    - name: Display name
    - description: Brief description
    - icon: Icon class or emoji
    - template: Template name
    - get_context_data(): Return data for template rendering
    """
    
    slug: str = None
    name: str = None
    description: str = None
    icon: str = "📊"
    template: str = None
    refresh_interval: int = 60  # seconds
    order: int = 0  # Display order
    
    def __init__(self, request=None):
        """
        Initialize widget with optional request context.
        
        Args:
            request: Django HttpRequest object
        """
        self.request = request
        self.config = self.get_config()
    
    def get_config(self) -> Dict:
        """
        Get plugin configuration from settings.
        
        Returns:
            Configuration dictionary
        """
        plugin_config = getattr(settings, 'PLUGINS_CONFIG', {})
        return plugin_config.get('netbox_insights_dashboard_plugin', {})
    
    @abstractmethod
    def get_context_data(self) -> Dict:
        """
        Get data for widget rendering.
        
        Must return a dictionary with all data needed for the template.
        
        Returns:
            Context dictionary for template
        """
        raise NotImplementedError("Subclasses must implement get_context_data()")
    
    def get_template_name(self) -> str:
        """
        Get the template name for this widget.
        
        Returns:
            Template path
        """
        return self.template or f"netbox_insights_dashboard_plugin/widgets/{self.slug}.html"
    
    def is_enabled(self) -> bool:
        """
        Check if this widget is enabled in configuration.
        
        Returns:
            True if enabled, False otherwise
        """
        widget_config = self.config.get('widgets', {})
        return widget_config.get(self.slug, {}).get('enabled', True)
    
    def get_refresh_interval(self) -> int:
        """
        Get configured refresh interval for this widget.
        
        Returns:
            Refresh interval in seconds
        """
        widget_config = self.config.get('widgets', {})
        widget_settings = widget_config.get(self.slug, {})
        return widget_settings.get('refresh_interval', self.refresh_interval)
    
    def render(self) -> Dict:
        """
        Render the widget and return all necessary data.
        
        Returns:
            Dictionary with widget metadata and context
        """
        return {
            'slug': self.slug,
            'name': self.name,
            'description': self.description,
            'icon': self.icon,
            'template': self.get_template_name(),
            'refresh_interval': self.get_refresh_interval(),
            'order': self.order,
            'enabled': self.is_enabled(),
            'context': self.get_context_data() if self.is_enabled() else {},
        }
    
    def __str__(self):
        return self.name or self.slug
    
    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.slug}>"
