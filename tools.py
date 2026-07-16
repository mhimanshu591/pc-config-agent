"""Tool definitions for PC Configuration Agent."""
from typing import Dict, Callable, Any
import json
import logging

logger = logging.getLogger(__name__)


class ToolRegistry:
    """Registry for agent tools."""
    
    def __init__(self, data_loader):
        """Initialize tool registry with data loader."""
        self.data_loader = data_loader
        self.tools: Dict[str, Dict[str, Any]] = self._define_tools()
    
    def _define_tools(self) -> Dict[str, Dict[str, Any]]:
        """Define available tools."""
        return {
            "search_components": {
                "description": "Search for components by type with optional filters",
                "parameters": {
                    "component_type": "Type of component (cpu, motherboard, memory, video-card, power-supply, case, internal-hard-drive, cpu-cooler) (required)",
                    "filters": "JSON string of key-value pairs to filter results (optional, default: {})",
                    "max_price": "Maximum price filter (optional, default: None)",
                    "limit": "Maximum number of results (optional, default: 5)"
                },
                "function": self._search_components
            },
            "get_component_types": {
                "description": "List all available component types",
                "parameters": {},
                "function": self._get_component_types
            },
            "get_component_schema": {
                "description": "Get available fields for a component type",
                "parameters": {
                    "component_type": "Type of component (required)"
                },
                "function": self._get_component_schema
            }
        }
    
    def _search_components(self, component_type: str, filters: str = "{}", max_price: str = "None", limit: str = "5") -> str:
        """Search for components."""
        try:
            filter_dict = json.loads(filters) if filters != "{}" else None
            max_price_val = float(max_price) if max_price != "None" else None
            limit_val = int(limit)
            
            results = self.data_loader.search_components(
                component_type=component_type,
                filters=filter_dict,
                max_price=max_price_val,
                limit=limit_val
            )
            return json.dumps(results, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error searching components: {e}")
            return json.dumps({"error": str(e)})
    
    def _get_component_types(self) -> str:
        """Get available component types."""
        types = self.data_loader.get_component_types()
        return json.dumps(types, indent=2)
    
    def _get_component_schema(self, component_type: str) -> str:
        """Get component schema."""
        schema = self.data_loader.get_component_schema(component_type)
        return json.dumps(schema, indent=2)
