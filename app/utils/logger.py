"""
Logging utility for the Personal Dashboard application.
"""
import logging
import sys
from datetime import datetime


def setup_logger(name: str, log_file: str = None, level: str = 'INFO'):
    """
    Set up a logger with console and optional file output.
    
    Args:
        name: Logger name (usually __name__)
        log_file: Optional log file path
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)
    
    # Convert string level to logging constant
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(numeric_level)
    
    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger
    
    # Console handler with custom format
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    
    # Custom format with emojis for visual distinction
    formatter = logging.Formatter(
        '%(levelname_icon)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Add custom filter for emoji icons
    class EmojiFilter(logging.Filter):
        ICONS = {
            'DEBUG': '🔍',
            'INFO': 'ℹ️ ',
            'WARNING': '⚠️ ',
            'ERROR': '❌',
            'CRITICAL': '🚨'
        }
        
        def filter(self, record):
            record.levelname_icon = self.ICONS.get(record.levelname, '  ')
            return True
    
    console_handler.addFilter(EmojiFilter())
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler if specified
    if log_file:
        try:
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(numeric_level)
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            logger.warning(f"Could not create file handler for {log_file}: {e}")
    
    return logger


def log_api_request(logger, service: str, status: int, duration: float = None):
    """Log API request with consistent format"""
    emoji = '✓' if status == 200 else '⚠️'
    msg = f"{emoji} {service} API - Status {status}"
    if duration:
        msg += f" ({duration:.2f}s)"
    
    if status == 200:
        logger.info(msg)
    else:
        logger.warning(msg)


def log_error(logger, service: str, error: Exception):
    """Log error with consistent format"""
    logger.error(f"❌ {service} error: {type(error).__name__}: {str(error)}")
