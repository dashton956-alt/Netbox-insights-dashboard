"""Navigation menu items for NetBox Insights Dashboard."""

from netbox.plugins import PluginMenuItem

menu_items = (
    PluginMenuItem(
        link="plugins:netbox_insights_dashboard_plugin:dashboard",
        link_text="Insights Dashboard",
        permissions=["netbox_insights_dashboard_plugin.view_dashboard"],
        buttons=()
    ),
    PluginMenuItem(
        link="plugins:netbox_insights_dashboard_plugin:config",
        link_text="Configuration",
        permissions=["netbox_insights_dashboard_plugin.change_config"],
        buttons=()
    ),
)
