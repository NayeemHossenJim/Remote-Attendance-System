from datetime import datetime, time

START = time(8, 0)
END = time(9, 30)

def check_time(now: datetime) -> str:
    if START <= now.time() <= END:
        return "ON_TIME"
    return "LATE"
