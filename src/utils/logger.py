"""
Logging configuration for Customer Counter Pro
Provides centralized logging to both console and file
"""

import logging
import os
from datetime import datetime
from pathlib import Path


def setup_logger(name="CustomerCounter", log_dir="data/logs"):
    """
    Set up application logger with file and console output
    
    Parameters
    ----------
    name : str
        Logger name
    log_dir : str
        Directory to store log files
    
    Returns
    -------
    logging.Logger
        Configured logger instance
    """
    # Create logs directory if it doesn't exist
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # Avoid duplicate handlers if logger already exists
    if logger.handlers:
        return logger
    
    # File handler - with daily log files
    log_filename = f"{name}_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_path / log_filename)
    file_handler.setLevel(logging.DEBUG)
    
    # Console handler - only show INFO and above
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


# Create default logger instance
logger = setup_logger()

