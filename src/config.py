"""
Configuration management for Customer Counter Pro
Loads settings from YAML file with sensible defaults
"""

import yaml
from pathlib import Path
from typing import Any, Dict
from src.utils.logger import logger


class Config:
    """Configuration manager with default values and YAML loading"""
    
    # Default configuration
    DEFAULTS = {
        'camera': {
            'source': 0,
            'resolution': [1280, 720],
            'fps': 30
        },
        'detection': {
            'model': 'models/yolov8n.pt',
            'confidence_threshold': 0.5
        },
        'counting': {
            'line_position': 0.5,  # 50% from top
            'direction': 'vertical',  # or 'horizontal'
            'tracking_enabled': True
        },
        'display': {
            'show_boxes': True,
            'show_ids': True,
            'show_line': True,
            'box_color': [0, 255, 0],  # Green in BGR
            'line_color': [0, 0, 255],  # Red in BGR
            'text_color': [255, 255, 255]  # White in BGR
        },
        'data': {
            'save_to_database': True,
            'database_path': 'data/counter_data.db',
            'export_interval': 3600  # Export report every hour (seconds)
        },
        'alerts': {
            'max_occupancy': 50,
            'alert_sound': False,
            'alert_enabled': False
        },
        'app': {
            'window_title': 'Customer Counter Pro',
            'company_name': 'Your Company',
            'version': '1.0.0'
        },
        'performance': {
            'frame_skip': 1,
            'detection_resolution': [640, 480],
            'display_resolution': [1280, 720],
            'use_roi': False,
            'roi_coords': [0, 0, 1280, 720]
        },
        'analytics': {
            'enabled': True,
            'historical_weeks': 4,
            'anomaly_threshold': 2.0,
            'auto_insights': True,
            'min_data_points': 10
        },
        'privacy': {
            'no_video_save': True,
            'offline_only': True,
            'anonymize_logs': False
        },
        'charts': {
            'default_format': 'pdf',
            'include_heatmap': True,
            'include_predictions': True,
            'color_scheme': 'professional'
        }
    }
    
    def __init__(self, config_path='config/settings.yaml'):
        """
        Initialize configuration
        
        Parameters
        ----------
        config_path : str
            Path to YAML configuration file
        """
        self.config_path = Path(config_path)
        self.config = self.DEFAULTS.copy()
        self.load()
    
    def load(self):
        """Load configuration from YAML file, use defaults if file doesn't exist"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    user_config = yaml.safe_load(f)
                    if user_config:
                        self._deep_update(self.config, user_config)
                        logger.info(f"Configuration loaded from {self.config_path}")
            except Exception as e:
                logger.error(f"Error loading config file: {e}. Using defaults.")
        else:
            logger.warning(f"Config file not found at {self.config_path}. Using defaults.")
            # Create config file with defaults
            self.save()
    
    def save(self):
        """Save current configuration to YAML file"""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)
            logger.info(f"Configuration saved to {self.config_path}")
        except Exception as e:
            logger.error(f"Error saving config file: {e}")
    
    def get(self, *keys, default=None):
        """
        Get configuration value using dot notation
        
        Parameters
        ----------
        *keys : str
            Keys to navigate configuration (e.g., 'camera', 'source')
        default : Any
            Default value if key not found
        
        Returns
        -------
        Any
            Configuration value
        
        Examples
        --------
        >>> config.get('camera', 'source')
        0
        >>> config.get('detection', 'model')
        'models/yolov8n.pt'
        """
        value = self.config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value
    
    def set(self, *keys, value):
        """
        Set configuration value using dot notation
        
        Parameters
        ----------
        *keys : str
            Keys to navigate configuration
        value : Any
            Value to set
        """
        config = self.config
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        config[keys[-1]] = value
    
    def _deep_update(self, base_dict, update_dict):
        """Recursively update nested dictionary"""
        for key, value in update_dict.items():
            if isinstance(value, dict) and key in base_dict and isinstance(base_dict[key], dict):
                self._deep_update(base_dict[key], value)
            else:
                base_dict[key] = value


# Global config instance
config = Config()

