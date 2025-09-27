"""
Logging configuration for OMF2 Dashboard
Provides structured logging with consistent formatting
"""

import logging
import sys
from pathlib import Path
from typing import Optional


def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Get a configured logger instance for OMF2
    
    Args:
        name: Logger name (typically module name)
        level: Logging level
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Only configure if not already configured
    if not logger.handlers:
        # Create handler
        handler = logging.StreamHandler(sys.stdout)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(level)
        
        # Prevent duplicate logging
        logger.propagate = False
    
    return logger


def setup_file_logging(log_dir: Optional[Path] = None) -> Path:
    """
    Setup file logging for OMF2
    
    Args:
        log_dir: Directory for log files (defaults to logs/ in project root)
    
    Returns:
        Path to log directory
    """
    if log_dir is None:
        project_root = Path(__file__).parent.parent.parent
        log_dir = project_root / "logs"
    
    log_dir.mkdir(exist_ok=True)
    
    # Configure root logger for file output
    log_file = log_dir / "omf2.log"
    
    file_handler = logging.FileHandler(log_file)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    
    root_logger = logging.getLogger("omf2")
    root_logger.addHandler(file_handler)
    root_logger.setLevel(logging.INFO)
    
    return log_dir