"""
Utility functions and helpers for the Personal Dashboard.
"""
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from typing import Optional


def get_timezone(tz_string: str = 'Europe/Berlin') -> ZoneInfo:
    """
    Get ZoneInfo object for specified timezone.
    
    Args:
        tz_string: Timezone string (e.g., 'Europe/Berlin')
    
    Returns:
        ZoneInfo object
    """
    return ZoneInfo(tz_string)


def now_in_timezone(tz_string: str = 'Europe/Berlin') -> datetime:
    """
    Get current datetime in specified timezone.
    
    Args:
        tz_string: Timezone string
    
    Returns:
        datetime object in specified timezone
    """
    return datetime.now(get_timezone(tz_string))


def parse_calendar_datetime(date_str: str, tz_string: str = 'Europe/Berlin') -> Optional[datetime]:
    """
    Parse calendar date/datetime string and convert to specified timezone.
    Handles both date-only and datetime formats.
    
    Args:
        date_str: Date or datetime string from calendar
        tz_string: Target timezone
    
    Returns:
        datetime object in specified timezone, or None if parsing fails
    """
    try:
        if 'T' in date_str:
            # DateTime format - convert to target timezone
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return dt.astimezone(get_timezone(tz_string))
        else:
            # Date-only format (all-day events)
            return datetime.fromisoformat(date_str).replace(tzinfo=get_timezone(tz_string))
    except Exception:
        return None


def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to human-readable string.
    
    Args:
        seconds: Duration in seconds
    
    Returns:
        Formatted string (e.g., "7h 30m")
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    
    if hours > 0:
        return f"{hours}h {minutes}m"
    return f"{minutes}m"


def truncate_text(text: str, max_length: int = 100, suffix: str = '...') -> str:
    """
    Truncate text to maximum length with suffix.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
    
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def safe_get(dictionary: dict, *keys, default=None):
    """
    Safely get nested dictionary value.
    
    Args:
        dictionary: Dictionary to access
        *keys: Sequence of keys to traverse
        default: Default value if key not found
    
    Returns:
        Value if found, default otherwise
    
    Example:
        safe_get(data, 'user', 'profile', 'name', default='Unknown')
    """
    current = dictionary
    for key in keys:
        if isinstance(current, dict):
            current = current.get(key)
            if current is None:
                return default
        else:
            return default
    return current if current is not None else default
