"""Caching utilities for performance optimization."""

from typing import Any, Callable, Optional
from datetime import timedelta
from django.core.cache import cache
from django.conf import settings
from functools import wraps


def get_cache_key(prefix: str, *args, **kwargs) -> str:
    """
    Generate a cache key from prefix and arguments.
    
    Args:
        prefix: Cache key prefix
        *args: Positional arguments to include in key
        **kwargs: Keyword arguments to include in key
        
    Returns:
        Cache key string
    """
    key_parts = [prefix]
    key_parts.extend(str(arg) for arg in args)
    key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
    return ":".join(key_parts)


def cached_widget_data(timeout: int = 300):
    """
    Decorator to cache widget data.
    
    Args:
        timeout: Cache timeout in seconds (default 5 minutes)
        
    Usage:
        @cached_widget_data(timeout=60)
        def get_widget_data():
            return expensive_calculation()
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Check if caching is enabled
            plugin_config = getattr(settings, 'PLUGINS_CONFIG', {})
            insights_config = plugin_config.get('netbox_insights_dashboard_plugin', {})
            
            if not insights_config.get('enable_caching', True):
                return func(*args, **kwargs)
            
            # Generate cache key
            cache_key = get_cache_key(f"insights:{func.__name__}", *args, **kwargs)
            
            # Try to get from cache
            cached_data = cache.get(cache_key)
            if cached_data is not None:
                return cached_data
            
            # Calculate and cache
            data = func(*args, **kwargs)
            cache.set(cache_key, data, timeout)
            
            return data
        
        return wrapper
    return decorator


def invalidate_cache(pattern: str):
    """
    Invalidate cache entries matching a pattern.
    
    Args:
        pattern: Cache key pattern to invalidate
    """
    try:
        # This is a simplified version - full implementation would require
        # cache backend that supports pattern-based deletion
        cache_key = f"insights:{pattern}"
        cache.delete(cache_key)
    except Exception:
        pass  # Fail silently


def get_cache_timeout() -> int:
    """
    Get configured cache timeout from settings.
    
    Returns:
        Cache timeout in seconds
    """
    plugin_config = getattr(settings, 'PLUGINS_CONFIG', {})
    insights_config = plugin_config.get('netbox_insights_dashboard_plugin', {})
    return insights_config.get('cache_ttl', 300)
