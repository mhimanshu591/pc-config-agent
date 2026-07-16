"""Data loader for PC components dataset."""
import pandas as pd
import os
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)


class ComponentDataLoader:
    """Loads and indexes PC component data from CSV files."""
    
    def __init__(self, dataset_path: str):
        """Initialize the data loader with dataset path."""
        self.dataset_path = dataset_path
        self.components: Dict[str, pd.DataFrame] = {}
        self._load_all_components()
    
    def _load_all_components(self):
        """Load all component CSV files."""
        if not os.path.exists(self.dataset_path):
            logger.warning(f"Dataset path {self.dataset_path} does not exist")
            return
        
        for filename in os.listdir(self.dataset_path):
            if filename.endswith('.csv'):
                component_type = filename.replace('.csv', '').replace('-', '_')
                filepath = os.path.join(self.dataset_path, filename)
                try:
                    df = pd.read_csv(filepath)
                    self.components[component_type] = df
                    logger.info(f"Loaded {len(df)} {component_type}")
                except Exception as e:
                    logger.error(f"Failed to load {filename}: {e}")
    
    def get_component_types(self) -> List[str]:
        """Get list of available component types."""
        return list(self.components.keys())
    
    def get_component_schema(self, component_type: str) -> Dict[str, str]:
        """Get available fields for a component type."""
        if component_type not in self.components:
            return {}
        
        df = self.components[component_type]
        return {col: str(df[col].dtype) for col in df.columns}
    
    def search_components(
        self,
        component_type: str,
        filters: Optional[Dict[str, Any]] = None,
        max_price: Optional[float] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Search for components with optional filters."""
        if component_type not in self.components:
            return []
        
        df = self.components[component_type].copy()
        
        # Apply filters
        if filters:
            for key, value in filters.items():
                if key in df.columns:
                    df = df[df[key] == value]
        
        # Apply price filter
        if max_price and 'price' in df.columns:
            df = df[df['price'] <= max_price]
        
        # Limit results
        df = df.head(limit)
        
        return df.to_dict('records')
