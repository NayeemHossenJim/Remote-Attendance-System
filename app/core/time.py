from datetime import datetime, time
from app.core.config import settings

def get_check_in_time_window():
    """Get check-in time window from settings"""
    return (
        time(settings.CHECK_IN_START_HOUR, settings.CHECK_IN_START_MINUTE),
        time(settings.CHECK_IN_END_HOUR, settings.CHECK_IN_END_MINUTE)
    )

def check_time(now: datetime) -> str:
    """Check if current time is within check-in window"""
    START, END = get_check_in_time_window()
    current_time = now.time()
    
    if START <= current_time <= END:
        return "ON_TIME"
    elif current_time < START:
        return "BEFORE_WINDOW"
    else:
        return "LATE"

def is_within_check_in_window(now: datetime = None) -> bool:
    """Check if current time is within check-in window"""
    if now is None:
        now = datetime.now()
    return check_time(now) == "ON_TIME"
