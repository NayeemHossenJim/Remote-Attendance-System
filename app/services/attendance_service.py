from datetime import datetime
from app.core.time import check_time
from app.core.geo import haversine
from app.models.attendance import Attendance

def check_in(db, user, lat, lng):
    now = datetime.utcnow()
    time_state = check_time(now)

    distance = haversine(
        lat, lng,
        user.home_latitude,
        user.home_longitude
    )

    if time_state == "ON_TIME":
        if distance > user.allowed_radius_m:
            status = "ABSENT"
        else:
            status = "PRESENT"
    else:
        status = "PENDING"

    record = Attendance(
        user_id=user.id,
        status=status,
        latitude=lat,
        longitude=lng
    )
    db.add(record)
    db.commit()

    return {"status": status}
